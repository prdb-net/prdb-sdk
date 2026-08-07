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
    from ....models.problem_details import ProblemDetails
    from ....models.unlinked_video_filehashes_response import UnlinkedVideoFilehashesResponse
    from .get_sort_by_query_parameter_type import GetSortByQueryParameterType
    from .get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType

class UnlinkedRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /videos/filehashes/unlinked
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new UnlinkedRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/videos/filehashes/unlinked{?Page*,PageSize*,SortBy*,SortDirection*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[UnlinkedRequestBuilderGetQueryParameters]] = None) -> Optional[UnlinkedVideoFilehashesResponse]:
        """
        Returns a paged list of active filehash entries that are not linked to any video. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[UnlinkedVideoFilehashesResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.unlinked_video_filehashes_response import UnlinkedVideoFilehashesResponse

        return await self.request_adapter.send_async(request_info, UnlinkedVideoFilehashesResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[UnlinkedRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a paged list of active filehash entries that are not linked to any video. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> UnlinkedRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: UnlinkedRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return UnlinkedRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class UnlinkedRequestBuilderGetQueryParameters():
        """
        Returns a paged list of active filehash entries that are not linked to any video. Requires API key authentication.
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
            if original_name == "sort_by":
                return "SortBy"
            if original_name == "sort_direction":
                return "SortDirection"
            return original_name
        
        page: Optional[int] = None

        page_size: Optional[int] = None

        sort_by: Optional[GetSortByQueryParameterType] = None

        sort_direction: Optional[GetSortDirectionQueryParameterType] = None

    
    @dataclass
    class UnlinkedRequestBuilderGetRequestConfiguration(RequestConfiguration[UnlinkedRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

