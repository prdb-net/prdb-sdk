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
    from ...models.problem_details import ProblemDetails
    from ...models.search_pre_db_by_video_response import SearchPreDbByVideoResponse

class SearchByVideoRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /predb/search-by-video
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new SearchByVideoRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/predb/search-by-video{?Q*,ReleaseDate*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[SearchByVideoRequestBuilderGetQueryParameters]] = None) -> Optional[SearchPreDbByVideoResponse]:
        """
        Searches canonical PreDb titles and returns matching linked PreDb entries grouped by video. 'q' (min 3 characters) is required unless 'releaseDate' is provided, in which case 'q' is optional. Each group includes video and site details. Capped at 500 video groups, no paging.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[SearchPreDbByVideoResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
            "403": ProblemDetails,
            "429": ProblemDetails,
            "503": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.search_pre_db_by_video_response import SearchPreDbByVideoResponse

        return await self.request_adapter.send_async(request_info, SearchPreDbByVideoResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[SearchByVideoRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Searches canonical PreDb titles and returns matching linked PreDb entries grouped by video. 'q' (min 3 characters) is required unless 'releaseDate' is provided, in which case 'q' is optional. Each group includes video and site details. Capped at 500 video groups, no paging.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> SearchByVideoRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: SearchByVideoRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return SearchByVideoRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class SearchByVideoRequestBuilderGetQueryParameters():
        """
        Searches canonical PreDb titles and returns matching linked PreDb entries grouped by video. 'q' (min 3 characters) is required unless 'releaseDate' is provided, in which case 'q' is optional. Each group includes video and site details. Capped at 500 video groups, no paging.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "q":
                return "Q"
            if original_name == "release_date":
                return "ReleaseDate"
            return original_name
        
        q: Optional[str] = None

        release_date: Optional[datetime.date] = None

    
    @dataclass
    class SearchByVideoRequestBuilderGetRequestConfiguration(RequestConfiguration[SearchByVideoRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

