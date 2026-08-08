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
    from ..models.list_actors_response import ListActorsResponse
    from ..models.problem_details import ProblemDetails
    from .batch.batch_request_builder import BatchRequestBuilder
    from .changes.changes_request_builder import ChangesRequestBuilder
    from .get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType
    from .item.actors_item_request_builder import ActorsItemRequestBuilder

class ActorsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /actors
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ActorsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/actors{?CreatedAfter*,CreatedBefore*,Page*,PageSize*,Search*,SortBy*,SortDirection*}", path_parameters)
    
    def by_id(self,id: UUID) -> ActorsItemRequestBuilder:
        """
        Gets an item from the prdb_sdk.generated.actors.item collection
        param id: Unique identifier of the item
        Returns: ActorsItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.actors_item_request_builder import ActorsItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return ActorsItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ActorsRequestBuilderGetQueryParameters]] = None) -> Optional[ListActorsResponse]:
        """
        Returns a paged list of actors. Supports free-text search by name or alias, and sorting by name or creation date. Default page size is 100, maximum is 500. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ListActorsResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ..models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "401": ProblemDetails,
            "403": ProblemDetails,
            "429": ProblemDetails,
            "503": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ..models.list_actors_response import ListActorsResponse

        return await self.request_adapter.send_async(request_info, ListActorsResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ActorsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paged list of actors. Supports free-text search by name or alias, and sorting by name or creation date. Default page size is 100, maximum is 500. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ActorsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ActorsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ActorsRequestBuilder(self.request_adapter, raw_url)
    
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
    class ActorsRequestBuilderGetQueryParameters():
        """
        Returns a paged list of actors. Supports free-text search by name or alias, and sorting by name or creation date. Default page size is 100, maximum is 500. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "created_after":
                return "CreatedAfter"
            if original_name == "created_before":
                return "CreatedBefore"
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
        
        created_after: Optional[datetime.datetime] = None

        created_before: Optional[datetime.datetime] = None

        page: Optional[int] = None

        page_size: Optional[int] = None

        search: Optional[str] = None

        sort_by: Optional[str] = None

        sort_direction: Optional[GetSortDirectionQueryParameterType] = None

    
    @dataclass
    class ActorsRequestBuilderGetRequestConfiguration(RequestConfiguration[ActorsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

