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
    from ...models.own_review_state import OwnReviewState
    from ...models.problem_details import ProblemDetails
    from ...models.rating_page_of_own_rating_item import RatingPageOfOwnRatingItem
    from ...models.rating_sort_by import RatingSortBy
    from ...models.rating_target_type import RatingTargetType
    from .get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType

class MineRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /ratings/mine
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new MineRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/ratings/mine{?cursor*,fromUtc*,hasText*,pageSize*,reviewState*,search*,sortBy*,sortDirection*,stars*,toUtc*,type*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[MineRequestBuilderGetQueryParameters]] = None) -> Optional[RatingPageOfOwnRatingItem]:
        """
        Searches target names and filters by type, stars, original-date interval (from inclusive/to exclusive), text presence and owner-visible moderation state. Sort by Date or Stars asc/desc. Opaque seek cursors bind to account, all filters and page size; preserve filters while paging. Returns existing current ratings, never historical versions, other users' texts or internal moderation reasons. Not cached. No delta feed is provided.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[RatingPageOfOwnRatingItem]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
            "403": ProblemDetails,
            "404": ProblemDetails,
            "409": ProblemDetails,
            "429": ProblemDetails,
            "500": ProblemDetails,
            "503": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.rating_page_of_own_rating_item import RatingPageOfOwnRatingItem

        return await self.request_adapter.send_async(request_info, RatingPageOfOwnRatingItem, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[MineRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Searches target names and filters by type, stars, original-date interval (from inclusive/to exclusive), text presence and owner-visible moderation state. Sort by Date or Stars asc/desc. Opaque seek cursors bind to account, all filters and page size; preserve filters while paging. Returns existing current ratings, never historical versions, other users' texts or internal moderation reasons. Not cached. No delta feed is provided.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> MineRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: MineRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return MineRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class MineRequestBuilderGetQueryParameters():
        """
        Searches target names and filters by type, stars, original-date interval (from inclusive/to exclusive), text presence and owner-visible moderation state. Sort by Date or Stars asc/desc. Opaque seek cursors bind to account, all filters and page size; preserve filters while paging. Returns existing current ratings, never historical versions, other users' texts or internal moderation reasons. Not cached. No delta feed is provided.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "from_utc":
                return "fromUtc"
            if original_name == "has_text":
                return "hasText"
            if original_name == "page_size":
                return "pageSize"
            if original_name == "review_state":
                return "reviewState"
            if original_name == "sort_by":
                return "sortBy"
            if original_name == "sort_direction":
                return "sortDirection"
            if original_name == "to_utc":
                return "toUtc"
            if original_name == "cursor":
                return "cursor"
            if original_name == "search":
                return "search"
            if original_name == "stars":
                return "stars"
            if original_name == "type":
                return "type"
            return original_name
        
        cursor: Optional[str] = None

        from_utc: Optional[datetime.datetime] = None

        has_text: Optional[bool] = None

        page_size: Optional[int] = None

        review_state: Optional[OwnReviewState] = None

        search: Optional[str] = None

        sort_by: Optional[RatingSortBy] = None

        sort_direction: Optional[GetSortDirectionQueryParameterType] = None

        stars: Optional[int] = None

        to_utc: Optional[datetime.datetime] = None

        type: Optional[RatingTargetType] = None

    
    @dataclass
    class MineRequestBuilderGetRequestConfiguration(RequestConfiguration[MineRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

