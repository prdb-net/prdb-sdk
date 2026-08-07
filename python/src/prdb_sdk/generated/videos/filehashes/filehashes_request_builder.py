from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .batch.batch_request_builder import BatchRequestBuilder
    from .changes.changes_request_builder import ChangesRequestBuilder
    from .latest.latest_request_builder import LatestRequestBuilder
    from .lookup.lookup_request_builder import LookupRequestBuilder
    from .unlinked.unlinked_request_builder import UnlinkedRequestBuilder

class FilehashesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /videos/filehashes
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new FilehashesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/videos/filehashes", path_parameters)
    
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
    
    @property
    def latest(self) -> LatestRequestBuilder:
        """
        The latest property
        """
        from .latest.latest_request_builder import LatestRequestBuilder

        return LatestRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def lookup(self) -> LookupRequestBuilder:
        """
        The lookup property
        """
        from .lookup.lookup_request_builder import LookupRequestBuilder

        return LookupRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def unlinked(self) -> UnlinkedRequestBuilder:
        """
        The unlinked property
        """
        from .unlinked.unlinked_request_builder import UnlinkedRequestBuilder

        return UnlinkedRequestBuilder(self.request_adapter, self.path_parameters)
    

