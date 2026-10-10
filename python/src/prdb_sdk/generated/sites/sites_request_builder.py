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
    from ..models.list_sites_response import ListSitesResponse
    from ..models.problem_details import ProblemDetails
    from .changes.changes_request_builder import ChangesRequestBuilder
    from .get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType
    from .item.sites_item_request_builder import SitesItemRequestBuilder

class SitesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /sites
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new SitesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/sites{?ClassicOnly*,Page*,PageSize*,PlatformId*,Search*,SortBy*,SortDirection*}", path_parameters)
    
    def by_id(self,id: UUID) -> SitesItemRequestBuilder:
        """
        Gets an item from the prdb_sdk.generated.sites.item collection
        param id: Unique identifier of the item
        Returns: SitesItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.sites_item_request_builder import SitesItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return SitesItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[SitesRequestBuilderGetQueryParameters]] = None) -> Optional[ListSitesResponse]:
        """
        Returns a paged list of sites ordered by title ascending. Supports filtering by search term matched against site title. The full list fits in a single request at pageSize=1000. Every response carries a weak ETag covering the matched rows and the paging, sorting and search parameters; send it back as If-None-Match to get 304 Not Modified while nothing changed. Because the shared read-only output cache does not vary by If-None-Match, a request that hits the cache is answered with 200 and a body instead of 304 — that is expected, not an error. Sites carry no alias names, and matching a file name to a site happens exclusively server-side in POST /videos/identify. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ListSitesResponse]
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
        from ..models.list_sites_response import ListSitesResponse

        return await self.request_adapter.send_async(request_info, ListSitesResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[SitesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paged list of sites ordered by title ascending. Supports filtering by search term matched against site title. The full list fits in a single request at pageSize=1000. Every response carries a weak ETag covering the matched rows and the paging, sorting and search parameters; send it back as If-None-Match to get 304 Not Modified while nothing changed. Because the shared read-only output cache does not vary by If-None-Match, a request that hits the cache is answered with 200 and a body instead of 304 — that is expected, not an error. Sites carry no alias names, and matching a file name to a site happens exclusively server-side in POST /videos/identify. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> SitesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: SitesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return SitesRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def changes(self) -> ChangesRequestBuilder:
        """
        The changes property
        """
        from .changes.changes_request_builder import ChangesRequestBuilder

        return ChangesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class SitesRequestBuilderGetQueryParameters():
        """
        Returns a paged list of sites ordered by title ascending. Supports filtering by search term matched against site title. The full list fits in a single request at pageSize=1000. Every response carries a weak ETag covering the matched rows and the paging, sorting and search parameters; send it back as If-None-Match to get 304 Not Modified while nothing changed. Because the shared read-only output cache does not vary by If-None-Match, a request that hits the cache is answered with 200 and a body instead of 304 — that is expected, not an error. Sites carry no alias names, and matching a file name to a site happens exclusively server-side in POST /videos/identify. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "classic_only":
                return "ClassicOnly"
            if original_name == "page":
                return "Page"
            if original_name == "page_size":
                return "PageSize"
            if original_name == "platform_id":
                return "PlatformId"
            if original_name == "search":
                return "Search"
            if original_name == "sort_by":
                return "SortBy"
            if original_name == "sort_direction":
                return "SortDirection"
            return original_name
        
        # Restrict to classic sites without a publishing platform. Cannot be combined with platformId.
        classic_only: Optional[bool] = None

        # 1-based page number.
        page: Optional[int] = None

        # Number of items per page. Defaults to 20, max 1000 — the full list fits in one page.
        page_size: Optional[int] = None

        # Restrict to one publishing platform UUID.
        platform_id: Optional[UUID] = None

        # Optional search term matched against site title.
        search: Optional[str] = None

        # Field to sort by. Supported values: `title` (default).
        sort_by: Optional[str] = None

        # Sort direction: `asc` (default) or `desc`.
        sort_direction: Optional[GetSortDirectionQueryParameterType] = None

    
    @dataclass
    class SitesRequestBuilderGetRequestConfiguration(RequestConfiguration[SitesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

