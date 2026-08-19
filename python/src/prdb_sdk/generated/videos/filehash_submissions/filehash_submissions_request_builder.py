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
    from ...models.problem_details import ProblemDetails
    from ...models.submit_video_filehashes_request import SubmitVideoFilehashesRequest
    from ...models.submit_video_filehashes_response import SubmitVideoFilehashesResponse

class FilehashSubmissionsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /videos/filehash-submissions
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new FilehashSubmissionsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/videos/filehash-submissions", path_parameters)
    
    async def post(self,body: SubmitVideoFilehashesRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[SubmitVideoFilehashesResponse]:
        """
        Submits up to 200 assignments of a file hash to a video, on behalf of the authenticated user. Intended for assignments a person confirmed in a client's UI — exactly the cases automatic detection missed. Each entry needs a videoId and an osHash; the osHash is the only aggregation key, so an entry carrying only a pHash cannot be used. A pHash must be computed exactly as described under Perceptual hashes in the API description; a value from any other procedure is stored but can never be matched. The filename is optional and may be withheld; the endpoint works without it. Every entry gets its own outcome and the status stays 200: an unknown videoId is reported as videoNotFound, and an assignment that contradicts an existing one is stored as conflicted rather than overwriting it. Submissions are recorded in their own table. They appear in no read endpoint and change no lookup result; whether they ever enter the aggregated hash set is decided by the scraper's aggregation job, not here. Clients must make this strictly opt-in and off by default — that is a client-side obligation the API cannot enforce. Requires API key authentication.
        param body: Request body for submitting confirmed hash-to-video assignments.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[SubmitVideoFilehashesResponse]
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
        from ...models.submit_video_filehashes_response import SubmitVideoFilehashesResponse

        return await self.request_adapter.send_async(request_info, SubmitVideoFilehashesResponse, error_mapping)
    
    def to_post_request_information(self,body: SubmitVideoFilehashesRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Submits up to 200 assignments of a file hash to a video, on behalf of the authenticated user. Intended for assignments a person confirmed in a client's UI — exactly the cases automatic detection missed. Each entry needs a videoId and an osHash; the osHash is the only aggregation key, so an entry carrying only a pHash cannot be used. A pHash must be computed exactly as described under Perceptual hashes in the API description; a value from any other procedure is stored but can never be matched. The filename is optional and may be withheld; the endpoint works without it. Every entry gets its own outcome and the status stays 200: an unknown videoId is reported as videoNotFound, and an assignment that contradicts an existing one is stored as conflicted rather than overwriting it. Submissions are recorded in their own table. They appear in no read endpoint and change no lookup result; whether they ever enter the aggregated hash set is decided by the scraper's aggregation job, not here. Clients must make this strictly opt-in and off by default — that is a client-side obligation the API cannot enforce. Requires API key authentication.
        param body: Request body for submitting confirmed hash-to-video assignments.
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
    
    def with_url(self,raw_url: str) -> FilehashSubmissionsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: FilehashSubmissionsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return FilehashSubmissionsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class FilehashSubmissionsRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

