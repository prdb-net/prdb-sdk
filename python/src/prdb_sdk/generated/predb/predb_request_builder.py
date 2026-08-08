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
    from ..models.list_pre_db_response import ListPreDbResponse
    from ..models.problem_details import ProblemDetails
    from .get_category_query_parameter_type import GetCategoryQueryParameterType
    from .get_sort_by_query_parameter_type import GetSortByQueryParameterType
    from .get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType
    from .latest.latest_request_builder import LatestRequestBuilder
    from .search_by_video.search_by_video_request_builder import SearchByVideoRequestBuilder

class PredbRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /predb
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new PredbRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/predb{?Category*,Page*,PageSize*,ReleaseDateFrom*,ReleaseDateTo*,Search*,SortBy*,SortDirection*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[PredbRequestBuilderGetQueryParameters]] = None) -> Optional[ListPreDbResponse]:
        """
        Returns a paged list of PreDb entries. Supports filtering by title or release group search, category, and release date range. Default sort is release date descending. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ListPreDbResponse]
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
        from ..models.list_pre_db_response import ListPreDbResponse

        return await self.request_adapter.send_async(request_info, ListPreDbResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[PredbRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paged list of PreDb entries. Supports filtering by title or release group search, category, and release date range. Default sort is release date descending. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> PredbRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: PredbRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return PredbRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def latest(self) -> LatestRequestBuilder:
        """
        The latest property
        """
        from .latest.latest_request_builder import LatestRequestBuilder

        return LatestRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def search_by_video(self) -> SearchByVideoRequestBuilder:
        """
        The searchByVideo property
        """
        from .search_by_video.search_by_video_request_builder import SearchByVideoRequestBuilder

        return SearchByVideoRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class PredbRequestBuilderGetQueryParameters():
        """
        Returns a paged list of PreDb entries. Supports filtering by title or release group search, category, and release date range. Default sort is release date descending. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "category":
                return "Category"
            if original_name == "page":
                return "Page"
            if original_name == "page_size":
                return "PageSize"
            if original_name == "release_date_from":
                return "ReleaseDateFrom"
            if original_name == "release_date_to":
                return "ReleaseDateTo"
            if original_name == "search":
                return "Search"
            if original_name == "sort_by":
                return "SortBy"
            if original_name == "sort_direction":
                return "SortDirection"
            return original_name
        
        category: Optional[GetCategoryQueryParameterType] = None

        page: Optional[int] = None

        page_size: Optional[int] = None

        release_date_from: Optional[datetime.date] = None

        release_date_to: Optional[datetime.date] = None

        search: Optional[str] = None

        sort_by: Optional[GetSortByQueryParameterType] = None

        sort_direction: Optional[GetSortDirectionQueryParameterType] = None

    
    @dataclass
    class PredbRequestBuilderGetRequestConfiguration(RequestConfiguration[PredbRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

