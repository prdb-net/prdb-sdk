from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from ...models.identify_videos_request import IdentifyVideosRequest
    from ...models.identify_videos_response import IdentifyVideosResponse
    from ...models.problem_details import ProblemDetails

class IdentifyRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /videos/identify
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new IdentifyRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/videos/identify", path_parameters)
    
    async def post(self,body: IdentifyVideosRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[IdentifyVideosResponse]:
        """
        Identifies up to 200 local files in one request and returns one result per file, mapped back by the client-assigned ref and in input order. Each file walks an identification ladder and the first rung that matches wins: OS hash, then perceptual hash (compared for equality), then a stored file name, then the file name without its extension as a scene release title, and finally the site read out of the file name. A pHash must be computed exactly as described under Perceptual hashes in the API description; a value from any other procedure skips that rung silently rather than failing, so send none if in doubt. matchedBy names the rung and confidence says how far the result can be trusted, so a client can decide which files it may file automatically and which it must show to a person. When a rung matches several videos equally well, the server does not guess: videoId is null, confidence is ambiguous and every candidate is listed. A file that matches nothing is a result with confidence none, not an error. Set includeVideoDetails to receive the full video document per matched file; it is off by default because 200 full documents is a large response. The whole request counts as one request against the rate limit. Nothing sent to this endpoint is stored. Requires API key authentication.
        param body: Request body for identifying local files against the prdb catalogue.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[IdentifyVideosResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
            "403": ProblemDetails,
            "429": ProblemDetails,
            "503": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.identify_videos_response import IdentifyVideosResponse

        return await self.request_adapter.send_async(request_info, IdentifyVideosResponse, error_mapping)
    
    def to_post_request_information(self,body: IdentifyVideosRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Identifies up to 200 local files in one request and returns one result per file, mapped back by the client-assigned ref and in input order. Each file walks an identification ladder and the first rung that matches wins: OS hash, then perceptual hash (compared for equality), then a stored file name, then the file name without its extension as a scene release title, and finally the site read out of the file name. A pHash must be computed exactly as described under Perceptual hashes in the API description; a value from any other procedure skips that rung silently rather than failing, so send none if in doubt. matchedBy names the rung and confidence says how far the result can be trusted, so a client can decide which files it may file automatically and which it must show to a person. When a rung matches several videos equally well, the server does not guess: videoId is null, confidence is ambiguous and every candidate is listed. A file that matches nothing is a result with confidence none, not an error. Set includeVideoDetails to receive the full video document per matched file; it is off by default because 200 full documents is a large response. The whole request counts as one request against the rate limit. Nothing sent to this endpoint is stored. Requires API key authentication.
        param body: Request body for identifying local files against the prdb catalogue.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> IdentifyRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: IdentifyRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return IdentifyRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class IdentifyRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

