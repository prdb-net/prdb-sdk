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
    from ...models.get_indexer_filehash_changes_response import GetIndexerFilehashChangesResponse
    from ...models.problem_details import ProblemDetails
    from .get_indexer_source_query_parameter_type import GetIndexerSourceQueryParameterType

class ChangesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /indexer-filehashes/changes
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ChangesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/indexer-filehashes/changes{?IndexerId*,IndexerSource*,PageSize*,Since*,SinceId*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ChangesRequestBuilderGetQueryParameters]] = None) -> Optional[GetIndexerFilehashChangesResponse]:
        """
        Returns a seek-paged delta feed of indexer filehash rows ordered by updatedAtUtc ascending, then id ascending. Includes created, updated, and soft-deleted rows as full payloads. Use since and the returned nextCursor to continue incrementally. Supports optional indexer source and indexer ID filters. Every page carries serverTimeUtc, the server clock read when the page was produced; persist it as the next since when items is empty. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[GetIndexerFilehashChangesResponse]
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
        from ...models.get_indexer_filehash_changes_response import GetIndexerFilehashChangesResponse

        return await self.request_adapter.send_async(request_info, GetIndexerFilehashChangesResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ChangesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a seek-paged delta feed of indexer filehash rows ordered by updatedAtUtc ascending, then id ascending. Includes created, updated, and soft-deleted rows as full payloads. Use since and the returned nextCursor to continue incrementally. Supports optional indexer source and indexer ID filters. Every page carries serverTimeUtc, the server clock read when the page was produced; persist it as the next since when items is empty. Requires API key authentication.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ChangesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ChangesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ChangesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ChangesRequestBuilderGetQueryParameters():
        """
        Returns a seek-paged delta feed of indexer filehash rows ordered by updatedAtUtc ascending, then id ascending. Includes created, updated, and soft-deleted rows as full payloads. Use since and the returned nextCursor to continue incrementally. Supports optional indexer source and indexer ID filters. Every page carries serverTimeUtc, the server clock read when the page was produced; persist it as the next since when items is empty. Requires API key authentication.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "indexer_id":
                return "IndexerId"
            if original_name == "indexer_source":
                return "IndexerSource"
            if original_name == "page_size":
                return "PageSize"
            if original_name == "since":
                return "Since"
            if original_name == "since_id":
                return "SinceId"
            return original_name
        
        indexer_id: Optional[str] = None

        indexer_source: Optional[GetIndexerSourceQueryParameterType] = None

        page_size: Optional[int] = None

        since: Optional[datetime.datetime] = None

        since_id: Optional[UUID] = None

    
    @dataclass
    class ChangesRequestBuilderGetRequestConfiguration(RequestConfiguration[ChangesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

