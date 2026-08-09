# Video hashing for prdb

**Normative.** This document defines how the `osHash` and `pHash` values that the
prdb Public API accepts are computed. It is written so that an implementation
can be built from it alone, without reading anyone else's source.

Endpoints that take these values:

- `POST /videos/filehashes/lookup`
- `POST /indexer-filehashes/lookup`
- `POST /videos/identify`
- `POST /videos/filehash-submissions`
- `POST /downloaded-from-indexers/{id}/filenames`

## Why this is written down

The API validates `pHash` as sixteen hex digits and stores it in a `char(16)`
column. That says what the value looks like, not what it means. Two 64-bit
values produced by different perceptual hashing methods sit roughly 32 bits
apart whether or not they describe the same video, so a distance comparison over
a column holding a mixture of methods is not imprecise — it is meaningless.

The method below is therefore not a proposal. It is the one already in use:
Stash computes an `oshash` and a `pHash` for every file it manages, and it is
the established open-source program in this space. A value that Stash would not
produce for the same input is the foreign body in the corpus, not the other way
round.

## OSHash

The OpenSubtitles hash. It reads 64 KiB from each end of the file, which makes
it cheap on large files and stable under renaming, but it changes completely
when the file is re-encoded.

```
blockSize = 65536

hash  = fileSizeInBytes                                (mod 2^64)
hash += sum of the 8192 little-endian uint64 values in the first blockSize bytes
hash += sum of the 8192 little-endian uint64 values in the last  blockSize bytes
```

All additions are unsigned 64-bit and wrap on overflow.

A file smaller than `2 * blockSize` (131072 bytes) **has no osHash**. It must
not be padded, and no value may be substituted; the field is simply absent.

The output is the 64-bit result as **16 lowercase hex digits**, zero-padded.

## pHash

The perceptual hash describes what the video looks like rather than what its
bytes are, so it survives a re-encode, a different container or a changed
bitrate — and it is the rung of the identification ladder that sits between an
exact file hash and guessing from the filename.

It is a 64-bit DCT hash computed over a 5×5 montage of frames sampled across the
video. The full chain is:

1. Extract 25 frames with ffmpeg
2. Assemble them into a 5×5 montage
3. Resize the montage to 64×64
4. Convert to greyscale
5. Discrete cosine transform, keeping the top-left 8×8 block
6. Derive a threshold from the 64 coefficients
7. Set one bit per coefficient
8. Emit 16 lowercase hex digits

Steps 2 through 8 are pure arithmetic and reproduce exactly in any language.
Step 1 does not: which single frame ffmpeg returns depends on the argument list
and on the behaviour of the ffmpeg build. That is why the command line below is
normative down to the argument order, and why video-level test vectors have to
name the ffmpeg version that produced them.

### Step 1 — Frame extraction

**Duration.** Probe the container with ffprobe:

```
ffprobe -v quiet -print_format json -show_entries format=duration <path>
```

Read `format.duration`, which may be a JSON number or a JSON string. A duration
that is absent, unparseable or not greater than zero means the file has no
pHash — it is a failure, not a zero-length video.

**Sample points.** 25 timestamps in seconds, skipping 5 % at each end so that
intros and end cards do not dominate:

```
frameCount = 25
offset     = 0.05 * duration
step       = 0.9  * duration / frameCount

t[i] = offset + i * step        for i = 0 .. 24
```

Note that this spreads the samples over `[0.05·d, 0.914·d]`: the last sample
sits one full step below the 95 % mark, because the step is the *width* of a
slice rather than the gap between endpoints. This is deliberate and must be
reproduced.

**Timestamp formatting.** Each timestamp is rendered as the shortest decimal
string that round-trips back to the same 64-bit float — Go's `fmt.Sprint` for a
`float64`, C#'s `"R"` format. It must use a period as the decimal separator
regardless of locale: a comma makes ffmpeg seek to the wrong place, or to zero,
silently.

**Capture.** For each timestamp, with fast seek (the seek argument **before**
`-i`):

```
ffmpeg -loglevel error -y -ss <t> -i <path> \
       -frames:v 1 -vf scale=160:-2 -c:v bmp -f rawvideo -
```

and with accurate seek (the seek argument **after** `-i`):

```
ffmpeg -loglevel error -y -i <path> -ss <t> \
       -frames:v 1 -vf scale=160:-2 -c:v bmp -f rawvideo -
```

Fast seek jumps to the nearest keyframe instead of decoding up to the timestamp,
so it is much faster and lands on a different frame.

**Seek strategy.** Start with fast seek. On the first failure, switch to
accurate seek for that frame **and for every remaining frame** — do not retry
each frame individually and do not switch back. A container with a broken index
fails the fast path consistently, so switching once is cheaper than discovering
it 25 times. This also means the strategy is a property of the file, not of the
individual frame, which keeps the result reproducible.

Any frame that cannot be captured even with accurate seek means the file has no
pHash. A montage may not be assembled from fewer than 25 frames, and a missing
frame may not be substituted with a black one.

**Frame format.** ffmpeg's `bmp` encoder emits an uncompressed bottom-up BMP,
24 bits per pixel, samples stored in BGR order, rows padded to a multiple of
4 bytes. A negative height in the header means the rows are stored top-down
instead. Read the geometry from the `BITMAPINFOHEADER` (header size 40; the V4
and V5 headers, 108 and 124, only add colour-space fields after the geometry and
are read the same way).

Convert each pixel to straight, non-premultiplied 8-bit RGBA: red from the third
sample byte, green from the second, blue from the first, and **alpha forced to
255** rather than read. Every stage after this assumes fully opaque pixels.

### Step 2 — The montage

The image model from here on is a straight 8-bit RGBA buffer: four bytes per
pixel in R, G, B, A order, rows top to bottom, stride `width * 4`. This mirrors
Go's `image.NRGBA` layout, which the arithmetic below is written against.

Take the width and height from the **first** frame. All 25 frames must have
those same dimensions; a differing frame is an error, because it would land
misaligned and leave uncovered canvas inside the hash. (In practice the scale
filter guarantees this, so a mismatch means ffmpeg ignored it.)

The montage is `5 * width` by `5 * height`. Frame `i` is pasted at:

```
x = width  * (i mod 5)
y = height * (i div 5)
```

Frames fill the grid left to right, top to bottom, in sample order.

Hashing a montage rather than a single frame is what makes the value describe
the whole video: one frame would collide across every scene with a similar
composition, and would land on a title card or a black frame often enough to be
useless.

### Step 3 — Resize to 64×64

**This is the step most likely to go wrong.** "Bilinear" here does not mean the
usual four-neighbour interpolation. The method is the bilinear path of
`github.com/nfnt/resize`, which scales the triangle filter's support by the
downscale factor — reducing 800×450 to 64×64 averages over a window of about
26 taps per axis, not 2. It also runs two passes that each write a *transposed*
intermediate, and it accumulates in 32-bit integers with 16-bit fixed-point
weights. Each of those choices moves individual hash bits.

If the input is already 64×64, return it unchanged. This shortcut is observable:
running the filter anyway would re-quantise the pixels.

Otherwise:

```
scaleX = montageWidth  / 64      (floating point division)
scaleY = montageHeight / 64
```

**Weights.** For an output length `n` and a scale `s`:

```
filterLength = 2 * max(ceil(s), 1)          integer
filterFactor = min(1 / s, 1)

for y in 0 .. n-1:
    u          = s * (y + 0.5) - 0.5
    offset[y]  = trunc(u) - filterLength/2 + 1     integer division, trunc toward zero
    u          = u - offset[y]

    for i in 0 .. filterLength-1:
        coeff[y*filterLength + i] = (int16) (triangle((u - i) * filterFactor) * 256)

triangle(v):  v = abs(v);  return v <= 1 ? 1 - v : 0
```

The cast to `int16` truncates toward zero; it is not a rounding operation.

**Passes.** Each pass reads rows of the source and writes a transposed
destination, so two passes produce an upright result.

- Pass 1: destination is `montageHeight` wide and `64` tall. Weights are built
  with `n = 64` and `s = scaleX`. Source is the montage.
- Pass 2: destination is `64` wide and `64` tall. Weights are built with
  `n = 64` and `s = scaleY`. Source is the pass-1 result.

A single pass, with `maxX = sourceWidth - 1`:

```
for x in 0 .. destWidth-1:
    rowStart = x * sourceStride

    for y in 0 .. destHeight-1:
        r = g = b = a = 0            int32
        sum = 0                      int32
        start = offset[y]

        for i in 0 .. filterLength-1:
            c = coeff[y*filterLength + i]
            if c == 0: continue

            j = start + i
            if   j >= maxX: p = maxX * 4         # clamp to the last pixel
            elif j <  0:    p = 0                # clamp to the first
            else:           p = j * 4

            r += c * source[rowStart + p + 0]
            g += c * source[rowStart + p + 1]
            b += c * source[rowStart + p + 2]
            a += c * source[rowStart + p + 3]
            sum += c

        t = y * destStride + x * 4
        dest[t + 0] = clampToByte(r / sum)       # integer division, truncating
        dest[t + 1] = clampToByte(g / sum)
        dest[t + 2] = clampToByte(b / sum)
        dest[t + 3] = clampToByte(a / sum)
```

Three details that are easy to lose and each of which changes the output:

- The edge clamp uses `>= maxX`, not `> maxX`. Reaching the last pixel takes the
  same branch as running past it. The original relies on unsigned wraparound to
  fold negative indices into that comparison; spelling it out as two branches is
  equivalent.
- The division by `sum` is integer division that truncates toward zero, applied
  after the whole tap loop — not floating point, and not rounded.
- Taps with a zero coefficient are skipped, so they contribute to neither the
  accumulator nor `sum`.

`clampToByte` maps values below 0 to 0 and above 255 to 255.

### Step 4 — Greyscale

For each of the 4096 pixels, from the 8-bit channel values, in double precision
and without rounding:

```
luma = 0.299 * R + 0.587 * G + 0.114 * B
```

Keep the result as a 64×64 array of doubles in row-major order.

(The reference converts nominally 16-bit channels and divides two of them by 257
and the third by 256, which reads like a typo. For 8-bit sources both divisions
return the original byte exactly, so applying the weights to the bytes directly
does not change a single result.)

### Step 5 — Discrete cosine transform

An **unscaled** DCT-II computed by the Byeong Gi Lee recursion. No
normalisation factor is applied at any stage.

```
for each of the 64 rows:  forward64(row)

for i in 0 .. 7:
    column[j] = pixels[64*j + i]   for j in 0 .. 63
    forward64(column)
    for j in 0 .. 7:
        result[8*j + i] = column[j]
```

The row transform runs over all 64 rows; the column transform runs over the
first 8 columns only, because the remaining columns cannot influence the
top-left 8×8 block. The result is that block, flattened row-major: 64
coefficients, with the DC coefficient at index 0.

The recursion, at each level `N` (64, 32, 16):

```
forwardN(v):
    for i in 0 .. N/2-1:
        x = v[i];  y = v[N-1-i]
        t[i]       = x + y
        t[i + N/2] = (x - y) / DCT_N[i]

    forward(N/2) on t[0 .. N/2-1]
    forward(N/2) on t[N/2 .. N-1]

    for i in 0 .. N/2-2:
        v[2*i]     = t[i]
        v[2*i + 1] = t[i + N/2] + t[i + N/2 + 1]

    v[N-2] = t[N/2 - 1]
    v[N-1] = t[N-1]
```

with `forward8` and `forward4` as the base cases:

```
forward8(v):
    a[0..3] = v[0]+v[7], v[1]+v[6], v[2]+v[5], v[3]+v[4]
    b[0]    = (v[0]-v[7]) / 1.9615705608064609
    b[1]    = (v[1]-v[6]) / 1.6629392246050907
    b[2]    = (v[2]-v[5]) / 1.1111404660392046
    b[3]    = (v[3]-v[4]) / 0.3901806440322566
    forward4(a);  forward4(b)
    v = [ a[0], b[0]+b[1], a[1], b[1]+b[2], a[2], b[2]+b[3], a[3], b[3] ]

forward4(v):
    t0 = v[0] + v[3]
    t1 = v[1] + v[2]
    t2 = (v[0] - v[3]) / 1.8477590650225735
    t3 = (v[1] - v[2]) / 0.7653668647301797

    x = t0;  y = t1
    t0 = t0 + t1
    t1 = (x - y) / 1.4142135623730951

    x = t2;  y = t3
    t2 = t2 + t3
    t3 = (x - y) / 1.4142135623730951

    v = [ t0, t2+t3, t1, t3 ]
```

**The divisor tables must be copied verbatim, not recomputed.** Two language
runtimes are not required to agree on the last bit of a cosine, and a divisor
that differs by one ulp can move a coefficient across the threshold and flip a
hash bit.

`DCT_64`, 32 values:

```
1.9993976373924083  1.9945809133573804  1.9849590691974202  1.9705552847778824
1.9514042600770571  1.9275521315908797  1.8990563611860733  1.8659855976694777
1.8284195114070614  1.7864486023910306  1.7401739822174227  1.6897071304994142
1.6351696263031674  1.5766928552532127  1.5144176930129691  1.448494165902934
1.3790810894741339  1.3063456859075537  1.2304631811612539  1.151616382835691
1.0699952397741948  0.9857963844595683  0.8992226593092132  0.8104826280099796
0.7197900730699766  0.627363480797783   0.5334255149497968  0.43820248031373954
0.3419237775206027  0.24482135039843256 0.1471291271993349  0.049082457045824535
```

`DCT_32`, 16 values:

```
1.9975909124103448  1.978353019929562   1.9400625063890882  1.8830881303660416
1.8079785862468867  1.7154572200005442  1.6064150629612899  1.4819022507099182
1.3431179096940369  1.191398608984867   1.0282054883864435  0.8551101868605644
0.6737797067844401  0.48596035980652796 0.2934609489107235  0.09813534865483627
```

`DCT_16`, 8 values:

```
1.9903694533443936  1.9138806714644176  1.76384252869671    1.546020906725474
1.2687865683272912  0.9427934736519956  0.5805693545089246  0.19603428065912154
```

### Step 6 — The threshold

The threshold is what the reference calls `MedianOfPixels`. **It is not the
median**, and it must not be replaced with one.

Quickselect leaves everything below position `k` unsorted, and for an
even-length input the function averages position `k` with whatever happens to
sit at `k-1` — an arbitrary element of the lower partition rather than the
next-smallest value. The threshold is therefore biased low by an amount that
depends on the pivot sequence. Reproduce it including the pivot choice and the
order of the swaps:

```
threshold(coefficients):            # 64 doubles, working on a copy
    n    = 64
    k    = n / 2                    # 32
    low  = 0
    high = n - 1

    if low == high: return seq[k]

    while low < high:
        pivot      = low/2 + high/2         # integer division of each term
        pivotValue = seq[pivot]
        store      = low

        swap(seq[pivot], seq[high])

        for i in low .. high-1:
            if seq[i] < pivotValue:
                swap(seq[store], seq[i])
                store = store + 1

        swap(seq[high], seq[store])

        if k <= store: high = store
        else:          low  = store + 1

    # n is even, so:
    return seq[k-1]/2 + seq[k]/2
```

Note that `pivot` is `low/2 + high/2` with each term truncated separately, which
is not the same as `(low + high)/2` when both are odd. Note also that the final
average is `seq[k-1]/2 + seq[k]/2`, evaluated as two divisions and one addition
rather than `(seq[k-1] + seq[k])/2`.

### Step 7 — Bits

For each coefficient index `i` from 0 to 63:

```
if coefficients[i] > threshold:
    hash |= 1 << (63 - i)
```

Strictly greater than, most significant bit first. **The DC coefficient at index
0 is kept**, not discarded — many descriptions of DCT perceptual hashing drop
it, and doing so here produces a different value.

### Step 8 — Output

The 64-bit result as **16 lowercase hex digits**, zero-padded.

## Casing at the API boundary

prdb validates both hashes case-insensitively against `^[0-9A-Fa-f]{16}$` and
normalises them to **uppercase** on write. This document specifies lowercase
output because that is what the reference implementations produce.

The mismatch matters to clients that keep a local mirror. Comparisons in a local
store are typically byte-for-byte — SQLite's default `BINARY` collation, for
instance — so a mirrored uppercase value never matches a locally computed
lowercase one, and the miss is silent: the file simply stays unidentified.
Convert at the boundary in both directions rather than relying on a collation
setting.

## Comparison

Perceptual hashes are compared by **Hamming distance** — the number of differing
bits, `popcount(a XOR b)` — not for equality. Two encodes of the same content
differ in a handful of bits, and an equality test only ever matches content that
happened to round identically, which discards most of the point.

Stash treats a distance of **8 or fewer bits out of 64** as the same content, and
that is the value to stay with unless a measurement says otherwise. Precision
falls away quickly above it: unrelated videos start colliding not far past that
point.

**The prdb API currently compares `pHash` for equality**, like any other field.
Distance matching is tracked as a separate change and is not in effect yet, so
today a pHash only contributes where an `osHash` would already have matched.

## Test vectors

A claim of compatibility is worth nothing without these. They come in three
levels, each one adding a stage of the chain.

Levels 1 and 2 use procedurally generated images rather than binary fixtures, so
that anyone can regenerate them by running the same formula through the
reference libraries, and so the repository stays free of megabytes of opaque
image data. Both generators produce straight RGBA with alpha 255.

**`noise(seed, w, h)`** — high-frequency content, where a resampler that averages
over the wrong window shows up immediately. A linear congruential generator,
with R, G and B drawn in that order for each pixel, pixels in row-major order:

```
state = (seed * 2654435761 + 12345)             mod 2^32

next():
    state = (state * 1664525 + 1013904223)      mod 2^32
    return (state >> 16) and 0xFF
```

**`gradient(seed, w, h)`** — smooth content, so that a bug which only bites on
image-like input cannot hide behind random pixels. All divisions are integer
divisions truncating toward zero:

```
R = (x * 255 / w + seed * 7)                    mod 256
G = (y * 255 / h + seed * 13)                   mod 256
B = (x * 255 / w + y * 255 / h + seed * 31)     mod 256
```

**`flat(w, h, v)`** — every channel set to `v`.

### Level 1 — a single image

Exercises the resampler, the DCT, the threshold and the bit order.

| Image | Size | Expected |
|---|---|---|
| `noise(1)` | 800×450 | `9d0b303b629cf8d9` |
| `gradient(1)` | 800×450 | `85421fb227ae7ca9` |
| `gradient(3)` | 64×64 | `956d4a8d7ad12953` |
| `gradient(5)` | 33×17 | `95b368d3050bde5c` |
| `noise(9)` | 37×23 | `8dd8dc85c7d84791` |
| `noise(4)` | 65×64 | `9a6367da8e971541` |
| `gradient(11)` | 127×71 | `dbe9c01d5a918357` |
| `gradient(2)` | 1×1 | `8000000000000000` |
| `flat(128)` | 800×450 | `8000000000000000` |

The flat image is the strongest single check on bit order: with no AC energy
every coefficient but the DC one is zero, so exactly one bit may be set and it
must be the most significant.

`gradient(3)` at 64×64 covers the identity shortcut in step 3, and
`gradient(5)` at 33×17 an upscale, where `filterLength` collapses to its
minimum.

### Level 2 — a montage

Adds the montage geometry and, because the input is 5× larger per axis, the
wide-window behaviour of the resampler. Each is 25 tiles of the given size,
tile `i` generated with `seed = i`:

| Tiles | Tile size | Expected |
|---|---|---|
| `noise` | 160×90 | `c1f4572a54f72c98` |
| `gradient` | 160×90 | `d5808a2f7e2f7415` |
| `noise` | 160×120 | `c1fc562254f32e99` |
| `gradient` | 160×67 | `d5808a2f7e2f7c05` |
| `noise` | 200×113 | `c6c8573156f124be` |
| `gradient` | 320×180 | `d5808a2f5e2f7c15` |

The values above were produced by running `corona10/goimagehash` v1.1.0,
`disintegration/imaging` v1.6.2 and `nfnt/resize` at the revision Stash pins
over the same formulas. A failure at either level means the implementation has
stopped being comparable with the rest of the ecosystem — it is not a number to
adjust.

### Level 3 — a video file

Adds frame selection, and therefore ffmpeg. **Not yet published.** These vectors
must name the exact ffmpeg version that produced them, because the frame a seek
lands on is a property of the build as much as of the arguments. Until they
exist, steps 2 through 8 are verifiable and step 1 is not.

## Reference implementation

`Prdb.Hashing`, a C# package in this repository — *in preparation*; this
document lands ahead of it. It is a transcription of the reference chain rather
than a reimplementation, and it reproduces the reference's mistakes — the
resampler, the kept DC coefficient and the threshold above — because a value
that does not match is worth very little.

Other languages are not covered yet. This document, not the C# package, is the
specification: an implementation that agrees with the test vectors is correct
even if it shares no code.

## Open points

- **Level 3 test vectors** do not exist yet, so the ffmpeg stage rests on the
  command line above rather than on a checkable value.
- **Values stored before this specification** are of unknown origin. Whether
  they are kept, marked or discarded is prdb's decision and is not settled here.
