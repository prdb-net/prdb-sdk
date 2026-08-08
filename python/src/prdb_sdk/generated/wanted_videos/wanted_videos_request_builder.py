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
from uuid import UUID
from warnings import warn

if TYPE_CHECKING:
    from ..models.list_wanted_videos_response import ListWantedVideosResponse
    from ..models.problem_details import ProblemDetails
    from .batch.batch_request_builder import BatchRequestBuilder
    from .changes.changes_request_builder import ChangesRequestBuilder
    from .get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType
    from .item.with_video_item_request_builder import WithVideoItemRequestBuilder

class WantedVideosRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /wanted-videos
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WantedVideosRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/wanted-videos{?ActorId*,AddedInLastDays*,IsFulfilled*,Page*,PageSize*,Search*,SiteId*,SortBy*,SortDirection*}", path_parameters)
    
    def by_video_id(self,video_id: UUID) -> WithVideoItemRequestBuilder:
        """
        Gets an item from the prdb_sdk.generated.wantedVideos.item collection
        param video_id: Unique identifier of the item
        Returns: WithVideoItemRequestBuilder
        """
        if video_id is None:
            raise TypeError("video_id cannot be null.")
        from .item.with_video_item_request_builder import WithVideoItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["videoId"] = video_id
        return WithVideoItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WantedVideosRequestBuilderGetQueryParameters]] = None) -> Optional[ListWantedVideosResponse]:
        """
        Returns a paged, sortable list of wanted videos for the currently authenticated user. Supports filtering by fulfilment status, site, actor, search term, and recency. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ListWantedVideosResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ..models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
            "403": ProblemDetails,
            "429": ProblemDetails,
            "503": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ..models.list_wanted_videos_response import ListWantedVideosResponse

        return await self.request_adapter.send_async(request_info, ListWantedVideosResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WantedVideosRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paged, sortable list of wanted videos for the currently authenticated user. Supports filtering by fulfilment status, site, actor, search term, and recency. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> WantedVideosRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WantedVideosRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WantedVideosRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def batch(self) -> BatchRequestBuilder:
        """
        The batch property
        """
        from .batch.batch_request_builder import BatchRequestBuilder

        return BatchRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def changes(self) -> ChangesRequestBuilder:
        """
        The changes property
        """
        from .changes.changes_request_builder import ChangesRequestBuilder

        return ChangesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WantedVideosRequestBuilderGetQueryParameters():
        """
        Returns a paged, sortable list of wanted videos for the currently authenticated user. Supports filtering by fulfilment status, site, actor, search term, and recency. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "actor_id":
                return "ActorId"
            if original_name == "added_in_last_days":
                return "AddedInLastDays"
            if original_name == "is_fulfilled":
                return "IsFulfilled"
            if original_name == "page":
                return "Page"
            if original_name == "page_size":
                return "PageSize"
            if original_name == "search":
                return "Search"
            if original_name == "site_id":
                return "SiteId"
            if original_name == "sort_by":
                return "SortBy"
            if original_name == "sort_direction":
                return "SortDirection"
            return original_name
        
        actor_id: Optional[UUID] = None

        added_in_last_days: Optional[int] = None

        is_fulfilled: Optional[bool] = None

        page: Optional[int] = None

        page_size: Optional[int] = None

        search: Optional[str] = None

        site_id: Optional[UUID] = None

        sort_by: Optional[str] = None

        sort_direction: Optional[GetSortDirectionQueryParameterType] = None

    
    @dataclass
    class WantedVideosRequestBuilderGetRequestConfiguration(RequestConfiguration[WantedVideosRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

