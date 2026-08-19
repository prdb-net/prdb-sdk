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
    from ....models.latest_video_filehashes_response import LatestVideoFilehashesResponse
    from ....models.problem_details import ProblemDetails
    from .get_sort_by_query_parameter_type import GetSortByQueryParameterType
    from .get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType

class LatestRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /videos/filehashes/latest
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new LatestRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/videos/filehashes/latest{?CreatedFrom*,CreatedTo*,IsVerified*,Page*,PageSize*,SiteId*,SortBy*,SortDirection*,UpdatedFrom*,UpdatedTo*,VideoId*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[LatestRequestBuilderGetQueryParameters]] = None) -> Optional[LatestVideoFilehashesResponse]:
        """
        Returns a paged list of active video filehash entries, including rows linked to videos and rows whose videoId is null. Supports up to 5000 rows per request, sorting by createdAtUtc, updatedAtUtc, submissionCount, or filesize, and filtering by video ID, site ID, verification state, and inclusive created/updated date ranges. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[LatestVideoFilehashesResponse]
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
        from ....models.latest_video_filehashes_response import LatestVideoFilehashesResponse

        return await self.request_adapter.send_async(request_info, LatestVideoFilehashesResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[LatestRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paged list of active video filehash entries, including rows linked to videos and rows whose videoId is null. Supports up to 5000 rows per request, sorting by createdAtUtc, updatedAtUtc, submissionCount, or filesize, and filtering by video ID, site ID, verification state, and inclusive created/updated date ranges. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> LatestRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: LatestRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return LatestRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class LatestRequestBuilderGetQueryParameters():
        """
        Returns a paged list of active video filehash entries, including rows linked to videos and rows whose videoId is null. Supports up to 5000 rows per request, sorting by createdAtUtc, updatedAtUtc, submissionCount, or filesize, and filtering by video ID, site ID, verification state, and inclusive created/updated date ranges. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "created_from":
                return "CreatedFrom"
            if original_name == "created_to":
                return "CreatedTo"
            if original_name == "is_verified":
                return "IsVerified"
            if original_name == "page":
                return "Page"
            if original_name == "page_size":
                return "PageSize"
            if original_name == "site_id":
                return "SiteId"
            if original_name == "sort_by":
                return "SortBy"
            if original_name == "sort_direction":
                return "SortDirection"
            if original_name == "updated_from":
                return "UpdatedFrom"
            if original_name == "updated_to":
                return "UpdatedTo"
            if original_name == "video_id":
                return "VideoId"
            return original_name
        
        # Optional. Return only filehashes created at or after this timestamp (UTC).
        created_from: Optional[datetime.datetime] = None

        # Optional. Return only filehashes created at or before this timestamp (UTC).
        created_to: Optional[datetime.datetime] = None

        # Optional. Filter by verification state. Omit for both verified and unverified entries.
        is_verified: Optional[bool] = None

        # 1-based page number. Defaults to 1.
        page: Optional[int] = None

        # Number of items per page. Defaults to 20, max 5000.
        page_size: Optional[int] = None

        # Optional. Restrict results to videos on the specified site.
        site_id: Optional[UUID] = None

        # Field to sort by. Supported values: `createdAtUtc` (default), `updatedAtUtc`, `submissionCount`, `filesize`.
        sort_by: Optional[GetSortByQueryParameterType] = None

        # Sort direction: `desc` (default) or `asc`.
        sort_direction: Optional[GetSortDirectionQueryParameterType] = None

        # Optional. Return only filehashes updated at or after this timestamp (UTC).
        updated_from: Optional[datetime.datetime] = None

        # Optional. Return only filehashes updated at or before this timestamp (UTC).
        updated_to: Optional[datetime.datetime] = None

        # Optional. Restrict results to a single video.
        video_id: Optional[UUID] = None

    
    @dataclass
    class LatestRequestBuilderGetRequestConfiguration(RequestConfiguration[LatestRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

