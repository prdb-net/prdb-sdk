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
from uuid import UUID
from warnings import warn

if TYPE_CHECKING:
    from ....models.get_video_filehash_changes_response import GetVideoFilehashChangesResponse
    from ....models.problem_details import ProblemDetails

class ChangesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /videos/filehashes/changes
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ChangesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/videos/filehashes/changes{?PageSize*,Since*,SinceId*,SiteId*,VideoId*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ChangesRequestBuilderGetQueryParameters]] = None) -> Optional[GetVideoFilehashChangesResponse]:
        """
        Returns a seek-paged delta feed of video filehash rows ordered by updatedAtUtc ascending, then id ascending. Includes created, updated, and soft-deleted rows as full payloads. Use since and the returned nextCursor to continue incrementally. Supports optional video ID and site ID filters. Every page carries serverTimeUtc, the server clock read when the page was produced; persist it as the next since when items is empty. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[GetVideoFilehashChangesResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
            "403": ProblemDetails,
            "429": ProblemDetails,
            "503": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.get_video_filehash_changes_response import GetVideoFilehashChangesResponse

        return await self.request_adapter.send_async(request_info, GetVideoFilehashChangesResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ChangesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a seek-paged delta feed of video filehash rows ordered by updatedAtUtc ascending, then id ascending. Includes created, updated, and soft-deleted rows as full payloads. Use since and the returned nextCursor to continue incrementally. Supports optional video ID and site ID filters. Every page carries serverTimeUtc, the server clock read when the page was produced; persist it as the next since when items is empty. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ChangesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ChangesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ChangesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ChangesRequestBuilderGetQueryParameters():
        """
        Returns a seek-paged delta feed of video filehash rows ordered by updatedAtUtc ascending, then id ascending. Includes created, updated, and soft-deleted rows as full payloads. Use since and the returned nextCursor to continue incrementally. Supports optional video ID and site ID filters. Every page carries serverTimeUtc, the server clock read when the page was produced; persist it as the next since when items is empty. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "page_size":
                return "PageSize"
            if original_name == "since":
                return "Since"
            if original_name == "since_id":
                return "SinceId"
            if original_name == "site_id":
                return "SiteId"
            if original_name == "video_id":
                return "VideoId"
            return original_name
        
        # Number of items per page. Defaults to 100, max 1000.
        page_size: Optional[int] = None

        # Inclusive lower-bound timestamp for changes. Use together with `sinceId` to continue from an exact cursor.
        since: Optional[datetime.datetime] = None

        # Optional lower-bound ID tie-breaker for rows with the same `since` timestamp.
        since_id: Optional[UUID] = None

        # Optional. Restrict changes to videos on the specified site.
        site_id: Optional[UUID] = None

        # Optional. Restrict changes to a single video.
        video_id: Optional[UUID] = None

    
    @dataclass
    class ChangesRequestBuilderGetRequestConfiguration(RequestConfiguration[ChangesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

