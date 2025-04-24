from .gis_document import GISDocument as GISDocument
from .server_extension import (
    _jupyter_server_extension_paths,
    _load_jupyter_server_extension,
)


__version__ = "0.1.0"
load_jupyter_server_extension = _load_jupyter_server_extension
