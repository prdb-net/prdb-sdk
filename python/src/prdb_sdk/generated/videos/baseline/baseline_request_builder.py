from __future__ import annotations
import datetime
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
    from ...models.baseline_document_too_large_response import BaselineDocumentTooLargeResponse
    from ...models.problem_details import ProblemDetails
    from ...models.video_baseline_response import VideoBaselineResponse

class BaselineRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /videos/baseline
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new BaselineRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/videos/baseline{?CreatedBefore*,CreatedFrom*,Cursor*,PageSize*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[BaselineRequestBuilderGetQueryParameters]] = None) -> Optional[VideoBaselineResponse]:
        """
        Returns complete Video detail documents ordered by (createdAtUtc, id). Example: /videos/baseline?createdFrom=2026-10-01T00:00:00Z&createdBefore=2026-10-22T00:00:00Z&pageSize=1000. The half-open creation range is at most 90 days. Persist each page and opaque nextCursor atomically; retain the same range on resume. Up to 1000 documents, 4 MiB JSON and 20000 related rows per page; a single document is limited to 2 MiB and 2000 related rows. A 413 identifies an exceptional document: fetch it with GET /videos/{videoId}, persist it, then use the supplied nextCursor. This is a mutable bounded scan, not an immutable snapshot. After completion, read /videos/changes from changesSince (inclusive, without sinceId), including tombstones and merges, until caught up. Apply only newer revisions by ID, filter live rows to the creation range, and follow merge survivors. Changes arriving during the scan are reconciled there. The handoff inherits the feed's settle-delay and writer timestamp/commit assumptions. Each page costs one existing hourly/monthly request unit; it is not quota-exempt. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[VideoBaselineResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ...models.baseline_document_too_large_response import BaselineDocumentTooLargeResponse
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
            "403": ProblemDetails,
            "413": BaselineDocumentTooLargeResponse,
            "429": ProblemDetails,
            "503": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.video_baseline_response import VideoBaselineResponse

        return await self.request_adapter.send_async(request_info, VideoBaselineResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[BaselineRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns complete Video detail documents ordered by (createdAtUtc, id). Example: /videos/baseline?createdFrom=2026-10-01T00:00:00Z&createdBefore=2026-10-22T00:00:00Z&pageSize=1000. The half-open creation range is at most 90 days. Persist each page and opaque nextCursor atomically; retain the same range on resume. Up to 1000 documents, 4 MiB JSON and 20000 related rows per page; a single document is limited to 2 MiB and 2000 related rows. A 413 identifies an exceptional document: fetch it with GET /videos/{videoId}, persist it, then use the supplied nextCursor. This is a mutable bounded scan, not an immutable snapshot. After completion, read /videos/changes from changesSince (inclusive, without sinceId), including tombstones and merges, until caught up. Apply only newer revisions by ID, filter live rows to the creation range, and follow merge survivors. Changes arriving during the scan are reconciled there. The handoff inherits the feed's settle-delay and writer timestamp/commit assumptions. Each page costs one existing hourly/monthly request unit; it is not quota-exempt. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> BaselineRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: BaselineRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return BaselineRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class BaselineRequestBuilderGetQueryParameters():
        """
        Returns complete Video detail documents ordered by (createdAtUtc, id). Example: /videos/baseline?createdFrom=2026-10-01T00:00:00Z&createdBefore=2026-10-22T00:00:00Z&pageSize=1000. The half-open creation range is at most 90 days. Persist each page and opaque nextCursor atomically; retain the same range on resume. Up to 1000 documents, 4 MiB JSON and 20000 related rows per page; a single document is limited to 2 MiB and 2000 related rows. A 413 identifies an exceptional document: fetch it with GET /videos/{videoId}, persist it, then use the supplied nextCursor. This is a mutable bounded scan, not an immutable snapshot. After completion, read /videos/changes from changesSince (inclusive, without sinceId), including tombstones and merges, until caught up. Apply only newer revisions by ID, filter live rows to the creation range, and follow merge survivors. Changes arriving during the scan are reconciled there. The handoff inherits the feed's settle-delay and writer timestamp/commit assumptions. Each page costs one existing hourly/monthly request unit; it is not quota-exempt. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "created_before":
                return "CreatedBefore"
            if original_name == "created_from":
                return "CreatedFrom"
            if original_name == "cursor":
                return "Cursor"
            if original_name == "page_size":
                return "PageSize"
            return original_name
        
        # Exclusive catalogue creation upper bound. Keep unchanged on resume.
        created_before: Optional[datetime.datetime] = None

        # Inclusive catalogue creation lower bound. Keep unchanged on resume.
        created_from: Optional[datetime.datetime] = None

        # Opaque continuation from the preceding page; persist with its documents.
        cursor: Optional[str] = None

        # Maximum documents, 1–1000; byte and work caps may produce a shorter page.
        page_size: Optional[int] = None

    
    @dataclass
    class BaselineRequestBuilderGetRequestConfiguration(RequestConfiguration[BaselineRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

