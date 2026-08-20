from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.api_client_builder import enable_backing_store_for_serialization_writer_factory, register_default_deserializer, register_default_serializer
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.serialization import ParseNodeFactoryRegistry, SerializationWriterFactoryRegistry
from kiota_serialization_form.form_parse_node_factory import FormParseNodeFactory
from kiota_serialization_form.form_serialization_writer_factory import FormSerializationWriterFactory
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory
from kiota_serialization_multipart.multipart_serialization_writer_factory import MultipartSerializationWriterFactory
from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from kiota_serialization_text.text_serialization_writer_factory import TextSerializationWriterFactory
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .actors.actors_request_builder import ActorsRequestBuilder
    from .favorite_actors.favorite_actors_request_builder import FavoriteActorsRequestBuilder
    from .favorite_sites.favorite_sites_request_builder import FavoriteSitesRequestBuilder
    from .health.health_request_builder import HealthRequestBuilder
    from .predb.predb_request_builder import PredbRequestBuilder
    from .rate_limit.rate_limit_request_builder import RateLimitRequestBuilder
    from .sites.sites_request_builder import SitesRequestBuilder
    from .user_identity.user_identity_request_builder import UserIdentityRequestBuilder
    from .videos.videos_request_builder import VideosRequestBuilder
    from .video_user_images.video_user_images_request_builder import VideoUserImagesRequestBuilder
    from .wanted_videos.wanted_videos_request_builder import WantedVideosRequestBuilder

class PrdbClient(BaseRequestBuilder):
    """
    The main entry point of the SDK, exposes the configuration and the fluent API.
    """
    def __init__(self,request_adapter: RequestAdapter) -> None:
        """
        Instantiates a new PrdbClient and sets the default values.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        if request_adapter is None:
            raise TypeError("request_adapter cannot be null.")
        super().__init__(request_adapter, "{+baseurl}", None)
        register_default_serializer(JsonSerializationWriterFactory)
        register_default_serializer(TextSerializationWriterFactory)
        register_default_serializer(FormSerializationWriterFactory)
        register_default_serializer(MultipartSerializationWriterFactory)
        register_default_deserializer(JsonParseNodeFactory)
        register_default_deserializer(TextParseNodeFactory)
        register_default_deserializer(FormParseNodeFactory)
        if not self.request_adapter.base_url:
            self.request_adapter.base_url = "https://api.prdb.net"
        self.path_parameters["base_url"] = self.request_adapter.base_url
    
    @property
    def actors(self) -> ActorsRequestBuilder:
        """
        The actors property
        """
        from .actors.actors_request_builder import ActorsRequestBuilder

        return ActorsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def favorite_actors(self) -> FavoriteActorsRequestBuilder:
        """
        The favoriteActors property
        """
        from .favorite_actors.favorite_actors_request_builder import FavoriteActorsRequestBuilder

        return FavoriteActorsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def favorite_sites(self) -> FavoriteSitesRequestBuilder:
        """
        The favoriteSites property
        """
        from .favorite_sites.favorite_sites_request_builder import FavoriteSitesRequestBuilder

        return FavoriteSitesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def health(self) -> HealthRequestBuilder:
        """
        The health property
        """
        from .health.health_request_builder import HealthRequestBuilder

        return HealthRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def predb(self) -> PredbRequestBuilder:
        """
        The predb property
        """
        from .predb.predb_request_builder import PredbRequestBuilder

        return PredbRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def rate_limit(self) -> RateLimitRequestBuilder:
        """
        The rateLimit property
        """
        from .rate_limit.rate_limit_request_builder import RateLimitRequestBuilder

        return RateLimitRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def sites(self) -> SitesRequestBuilder:
        """
        The sites property
        """
        from .sites.sites_request_builder import SitesRequestBuilder

        return SitesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def user_identity(self) -> UserIdentityRequestBuilder:
        """
        The userIdentity property
        """
        from .user_identity.user_identity_request_builder import UserIdentityRequestBuilder

        return UserIdentityRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def video_user_images(self) -> VideoUserImagesRequestBuilder:
        """
        The videoUserImages property
        """
        from .video_user_images.video_user_images_request_builder import VideoUserImagesRequestBuilder

        return VideoUserImagesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def videos(self) -> VideosRequestBuilder:
        """
        The videos property
        """
        from .videos.videos_request_builder import VideosRequestBuilder

        return VideosRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def wanted_videos(self) -> WantedVideosRequestBuilder:
        """
        The wantedVideos property
        """
        from .wanted_videos.wanted_videos_request_builder import WantedVideosRequestBuilder

        return WantedVideosRequestBuilder(self.request_adapter, self.path_parameters)
    

