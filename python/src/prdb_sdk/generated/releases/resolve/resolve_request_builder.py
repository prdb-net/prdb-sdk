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
    from ...models.rate_limit_problem_response import RateLimitProblemResponse
    from ...models.resolve_releases_request import ResolveReleasesRequest
    from ...models.resolve_releases_response import ResolveReleasesResponse
    from ...models.validation_problem_details import ValidationProblemDetails

class ResolveRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /releases/resolve
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ResolveRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/releases/resolve", path_parameters)
    
    async def post(self,body: ResolveReleasesRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[ResolveReleasesResponse]:
        """
        Read-only local resolution of 1–200 release titles, with optional source namespace/key, positive 64-bit byte size, UTC posting instant and category hints. Returns exactly one result per unique ref in input order. Batch correlation/syntax errors return 400; other invalid entry fields return invalid alongside valid entries. Only resolved identities are automationEligible and carry one active Video plus Site/Actor IDs. Candidates are alternatives, capped at 20; packs are unsupported. Verified source/canonical evidence is required for automation. Unknown origins and heuristics never acquire entry authority. Versions bind relevant input/knowledge, not evaluation time or refs. Recheck at recheckAfterUtc: unresolved cases after six hours, an unknown OnlyFans/Fansly release posted within the last 24 hours after 30 minutes, resolved pending acquisitions after 24 hours, and retryLater at the given time. Eligibility says nothing about content rights, quality, local ownership or availability. Incomplete credits do not prove an Actor's absence. No supplied URL is fetched, no canonical/user/review records are written and no file/hash confirmation is inferred. After download use real file hashes with videos/identify. JSON only, body at most 1 MiB. The whole batch consumes one normal request through the existing API-key/subscription/quota gate.
        param body: Local, read-only resolution of 1–200 release metadata records.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ResolveReleasesResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ...models.problem_details import ProblemDetails
        from ...models.rate_limit_problem_response import RateLimitProblemResponse
        from ...models.validation_problem_details import ValidationProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ValidationProblemDetails,
            "401": RateLimitProblemResponse,
            "403": RateLimitProblemResponse,
            "413": ProblemDetails,
            "415": ProblemDetails,
            "429": RateLimitProblemResponse,
            "500": ProblemDetails,
            "503": RateLimitProblemResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.resolve_releases_response import ResolveReleasesResponse

        return await self.request_adapter.send_async(request_info, ResolveReleasesResponse, error_mapping)
    
    def to_post_request_information(self,body: ResolveReleasesRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Read-only local resolution of 1–200 release titles, with optional source namespace/key, positive 64-bit byte size, UTC posting instant and category hints. Returns exactly one result per unique ref in input order. Batch correlation/syntax errors return 400; other invalid entry fields return invalid alongside valid entries. Only resolved identities are automationEligible and carry one active Video plus Site/Actor IDs. Candidates are alternatives, capped at 20; packs are unsupported. Verified source/canonical evidence is required for automation. Unknown origins and heuristics never acquire entry authority. Versions bind relevant input/knowledge, not evaluation time or refs. Recheck at recheckAfterUtc: unresolved cases after six hours, an unknown OnlyFans/Fansly release posted within the last 24 hours after 30 minutes, resolved pending acquisitions after 24 hours, and retryLater at the given time. Eligibility says nothing about content rights, quality, local ownership or availability. Incomplete credits do not prove an Actor's absence. No supplied URL is fetched, no canonical/user/review records are written and no file/hash confirmation is inferred. After download use real file hashes with videos/identify. JSON only, body at most 1 MiB. The whole batch consumes one normal request through the existing API-key/subscription/quota gate.
        param body: Local, read-only resolution of 1–200 release metadata records.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json, application/problem+json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> ResolveRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ResolveRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ResolveRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ResolveRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

