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
    from ..models.list_favorite_actors_response import ListFavoriteActorsResponse
    from ..models.problem_details import ProblemDetails
    from .changes.changes_request_builder import ChangesRequestBuilder
    from .get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType
    from .item.with_actor_item_request_builder import WithActorItemRequestBuilder

class FavoriteActorsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /favorite-actors
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new FavoriteActorsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/favorite-actors{?Page*,PageSize*,Search*,SortBy*,SortDirection*}", path_parameters)
    
    def by_actor_id(self,actor_id: UUID) -> WithActorItemRequestBuilder:
        """
        Gets an item from the prdb_sdk.generated.favoriteActors.item collection
        param actor_id: Unique identifier of the item
        Returns: WithActorItemRequestBuilder
        """
        if actor_id is None:
            raise TypeError("actor_id cannot be null.")
        from .item.with_actor_item_request_builder import WithActorItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["actorId"] = actor_id
        return WithActorItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[FavoriteActorsRequestBuilderGetQueryParameters]] = None) -> Optional[ListFavoriteActorsResponse]:
        """
        Returns a paged, sortable list of actors the currently authenticated user has favorited. Supports filtering by search term. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ListFavoriteActorsResponse]
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
        from ..models.list_favorite_actors_response import ListFavoriteActorsResponse

        return await self.request_adapter.send_async(request_info, ListFavoriteActorsResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[FavoriteActorsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paged, sortable list of actors the currently authenticated user has favorited. Supports filtering by search term. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> FavoriteActorsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: FavoriteActorsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return FavoriteActorsRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def changes(self) -> ChangesRequestBuilder:
        """
        The changes property
        """
        from .changes.changes_request_builder import ChangesRequestBuilder

        return ChangesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class FavoriteActorsRequestBuilderGetQueryParameters():
        """
        Returns a paged, sortable list of actors the currently authenticated user has favorited. Supports filtering by search term. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "page":
                return "Page"
            if original_name == "page_size":
                return "PageSize"
            if original_name == "search":
                return "Search"
            if original_name == "sort_by":
                return "SortBy"
            if original_name == "sort_direction":
                return "SortDirection"
            return original_name
        
        # 1-based page number. Defaults to 1.
        page: Optional[int] = None

        # Number of items per page. Defaults to 100, max 500.
        page_size: Optional[int] = None

        # Optional search term matched against actor name.
        search: Optional[str] = None

        # Field to sort by. Supported values: `favoritedAtUtc`, `name`. Defaults to `favoritedAtUtc`.
        sort_by: Optional[str] = None

        # Sort direction: `asc` or `desc`. Defaults to `desc`.
        sort_direction: Optional[GetSortDirectionQueryParameterType] = None

    
    @dataclass
    class FavoriteActorsRequestBuilderGetRequestConfiguration(RequestConfiguration[FavoriteActorsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

