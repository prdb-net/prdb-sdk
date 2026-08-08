from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.multipart_body import MultipartBody
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID
from warnings import warn

if TYPE_CHECKING:
    from ..models.problem_details import ProblemDetails
    from ..models.submit_video_user_image_response import SubmitVideoUserImageResponse
    from .by_os_hash.by_os_hash_request_builder import ByOsHashRequestBuilder
    from .changes.changes_request_builder import ChangesRequestBuilder
    from .item.item_request_builder import ItemRequestBuilder

class VideoUserImagesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /video-user-images
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new VideoUserImagesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/video-user-images", path_parameters)
    
    def by_id(self,id: UUID) -> ItemRequestBuilder:
        """
        Gets an item from the prdb_sdk.generated.videoUserImages.item collection
        param id: Unique identifier of the item
        Returns: ItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.item_request_builder import ItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["%2Did"] = id
        return ItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def post(self,body: MultipartBody, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[SubmitVideoUserImageResponse]:
        """
        Uploads a JPEG preview image to BunnyCDN, optionally linked to an existing video. When videoId is omitted, images are grouped by basedOnFileWithOsHash. A paired WebVTT file is required when PreviewImageType is SpriteSheet. Creates the VideoUserImage row and initial moderation state through shared moderation orchestration. Requires API key authentication.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[SubmitVideoUserImageResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ..models.problem_details import ProblemDetails

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
        from ..models.submit_video_user_image_response import SubmitVideoUserImageResponse

        return await self.request_adapter.send_async(request_info, SubmitVideoUserImageResponse, error_mapping)
    
    def to_post_request_information(self,body: MultipartBody, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Uploads a JPEG preview image to BunnyCDN, optionally linked to an existing video. When videoId is omitted, images are grouped by basedOnFileWithOsHash. A paired WebVTT file is required when PreviewImageType is SpriteSheet. Creates the VideoUserImage row and initial moderation state through shared moderation orchestration. Requires API key authentication.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "multipart/form-data", body)
        return request_info
    
    def with_url(self,raw_url: str) -> VideoUserImagesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: VideoUserImagesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return VideoUserImagesRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def by_os_hash(self) -> ByOsHashRequestBuilder:
        """
        The byOsHash property
        """
        from .by_os_hash.by_os_hash_request_builder import ByOsHashRequestBuilder

        return ByOsHashRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def changes(self) -> ChangesRequestBuilder:
        """
        The changes property
        """
        from .changes.changes_request_builder import ChangesRequestBuilder

        return ChangesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class VideoUserImagesRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

