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
    from ....models.add_downloaded_from_indexer_filename_request import AddDownloadedFromIndexerFilenameRequest
    from ....models.downloaded_from_indexer_response import DownloadedFromIndexerResponse
    from ....models.problem_details import ProblemDetails
    from .item.with_filename_item_request_builder import WithFilenameItemRequestBuilder

class FilenamesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /downloaded-from-indexers/{downloadedFromIndexerId}/filenames
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new FilenamesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/downloaded-from-indexers/{downloadedFromIndexerId}/filenames", path_parameters)
    
    def by_filename_id(self,filename_id: UUID) -> WithFilenameItemRequestBuilder:
        """
        Gets an item from the prdb_sdk.generated.downloadedFromIndexers.item.filenames.item collection
        param filename_id: Unique identifier of the item
        Returns: WithFilenameItemRequestBuilder
        """
        if filename_id is None:
            raise TypeError("filename_id cannot be null.")
        from .item.with_filename_item_request_builder import WithFilenameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["filenameId"] = filename_id
        return WithFilenameItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def post(self,body: AddDownloadedFromIndexerFilenameRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[DownloadedFromIndexerResponse]:
        """
        Adds a single filename row to a downloaded-from-indexer entry owned by the currently authenticated user. Returns 409 when the filename already exists under the parent entry.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DownloadedFromIndexerResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ....models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
            "401": ProblemDetails,
            "403": ProblemDetails,
            "404": ProblemDetails,
            "409": ProblemDetails,
            "429": ProblemDetails,
            "503": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.downloaded_from_indexer_response import DownloadedFromIndexerResponse

        return await self.request_adapter.send_async(request_info, DownloadedFromIndexerResponse, error_mapping)
    
    def to_post_request_information(self,body: AddDownloadedFromIndexerFilenameRequest, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Adds a single filename row to a downloaded-from-indexer entry owned by the currently authenticated user. Returns 409 when the filename already exists under the parent entry.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> FilenamesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: FilenamesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return FilenamesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class FilenamesRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

