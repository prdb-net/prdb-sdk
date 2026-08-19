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
    from ...models.fulfill_wanted_videos_batch_request import FulfillWantedVideosBatchRequest
    from ...models.fulfill_wanted_videos_batch_response import FulfillWantedVideosBatchResponse
    from ...models.problem_details import ProblemDetails

class FulfillmentsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /wanted-videos/fulfillments
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new FulfillmentsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/wanted-videos/fulfillments", path_parameters)
    
    async def post(self,body: FulfillWantedVideosBatchRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[FulfillWantedVideosBatchResponse]:
        """
        Marks up to 50 wanted videos of the currently authenticated user as fulfilled or unfulfilled in a single request. Returns one result per video, naming the outcome — updated, unchanged, not on the wanted list, or unknown video — so unknown and unwanted IDs do not fail the request; the status code stays 200. A 400 is only returned for form errors: an empty list, more than 50 entries, a video listed twice, or an invalid enum value. Setting isFulfilled to false clears the fulfilment timestamp, quality, external ID and application. Setting it to true without a fulfilledAtUtc stamps the server time, unless the entry is already fulfilled, in which case its timestamp is kept. Soft-deleted wanted entries are reported as not wanted and are not revived; use POST /wanted-videos/batch for that. The whole request counts as one request against the rate limit. Requires API key authentication.
        param body: Request body for batch-updating the fulfilment state of wanted videos.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[FulfillWantedVideosBatchResponse]
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
        from ...models.fulfill_wanted_videos_batch_response import FulfillWantedVideosBatchResponse

        return await self.request_adapter.send_async(request_info, FulfillWantedVideosBatchResponse, error_mapping)
    
    def to_post_request_information(self,body: FulfillWantedVideosBatchRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Marks up to 50 wanted videos of the currently authenticated user as fulfilled or unfulfilled in a single request. Returns one result per video, naming the outcome — updated, unchanged, not on the wanted list, or unknown video — so unknown and unwanted IDs do not fail the request; the status code stays 200. A 400 is only returned for form errors: an empty list, more than 50 entries, a video listed twice, or an invalid enum value. Setting isFulfilled to false clears the fulfilment timestamp, quality, external ID and application. Setting it to true without a fulfilledAtUtc stamps the server time, unless the entry is already fulfilled, in which case its timestamp is kept. Soft-deleted wanted entries are reported as not wanted and are not revived; use POST /wanted-videos/batch for that. The whole request counts as one request against the rate limit. Requires API key authentication.
        param body: Request body for batch-updating the fulfilment state of wanted videos.
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
    
    def with_url(self,raw_url: str) -> FulfillmentsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: FulfillmentsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return FulfillmentsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class FulfillmentsRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

