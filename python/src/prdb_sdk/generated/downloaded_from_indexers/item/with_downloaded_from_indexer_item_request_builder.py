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
    from ...models.downloaded_from_indexer_response import DownloadedFromIndexerResponse
    from ...models.problem_details import ProblemDetails
    from ...models.update_downloaded_from_indexer_request import UpdateDownloadedFromIndexerRequest
    from .filenames.filenames_request_builder import FilenamesRequestBuilder

class WithDownloadedFromIndexerItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /downloaded-from-indexers/{downloadedFromIndexerId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithDownloadedFromIndexerItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/downloaded-from-indexers/{downloadedFromIndexerId}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Hard-deletes a downloaded-from-indexer entry for the currently authenticated user. Any child filename rows are deleted with it. Returns 404 when the entry does not exist.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "401": ProblemDetails,
            "404": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def put(self,body: UpdateDownloadedFromIndexerRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[DownloadedFromIndexerResponse]:
        """
        Updates a downloaded-from-indexer entry for the currently authenticated user. User ID and video ID are immutable. Returns 409 when the parent uniqueness rule would be violated.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DownloadedFromIndexerResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from ...models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
            "404": ProblemDetails,
            "409": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.downloaded_from_indexer_response import DownloadedFromIndexerResponse

        return await self.request_adapter.send_async(request_info, DownloadedFromIndexerResponse, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Hard-deletes a downloaded-from-indexer entry for the currently authenticated user. Any child filename rows are deleted with it. Returns 404 when the entry does not exist.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: UpdateDownloadedFromIndexerRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Updates a downloaded-from-indexer entry for the currently authenticated user. User ID and video ID are immutable. Returns 409 when the parent uniqueness rule would be violated.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PUT, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> WithDownloadedFromIndexerItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithDownloadedFromIndexerItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithDownloadedFromIndexerItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def filenames(self) -> FilenamesRequestBuilder:
        """
        The filenames property
        """
        from .filenames.filenames_request_builder import FilenamesRequestBuilder

        return FilenamesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithDownloadedFromIndexerItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithDownloadedFromIndexerItemRequestBuilderPutRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

