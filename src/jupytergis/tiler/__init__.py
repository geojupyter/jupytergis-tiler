from .gis_document import GISDocument as GISDocument
from .server_extension import (
    _jupyter_server_extension_paths,
    _load_jupyter_server_extension,
)


load_jupyter_server_extension = _load_jupyter_server_extension
