from asyncio import Event, Lock, Task, create_task
from functools import partial
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlencode

from anycorn import Config, serve
from anyio import connect_tcp, create_task_group
from fastapi import FastAPI
from jupytergis import GISDocument as _GISDocument
from jupytergis_lab.notebook.gis_document import OBJECT_FACTORY
from jupytergis_lab.notebook.objects import LayerType, SourceType
from titiler.xarray.factory import TilerFactory
from titiler.xarray.extensions import VariablesExtension


class GISDocument(_GISDocument):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._tile_server_task: Task | None = None
        self._tile_server_started = Event()
        self._tile_server_shutdown = Event()
        self._tile_server_lock = Lock()

    async def _start_tile_server(self):
        self._tile_server_app = FastAPI()
        config = Config()
        config.bind = "127.0.0.1:0"
        async with create_task_group() as tg:
            binds = await tg.start(
                partial(
                    serve,
                    self._tile_server_app,
                    config,
                    shutdown_trigger=self._tile_server_shutdown.wait,
                    mode="asgi",
                )
            )
            self._tile_server_url = binds[0]
            host, _port = binds[0][len("http://") :].split(":")
            port = int(_port)
            while True:
                try:
                    await connect_tcp(host, port)
                except OSError:
                    pass
                else:
                    self._tile_server_started.set()
                    break

    def _include_tile_server_router(self, source_id: str):
        tiler = TilerFactory(
            router_prefix=f"/{source_id}",
            extensions=[
                VariablesExtension(),
            ],
        )
        self._tile_server_app.include_router(tiler.router, prefix=f"/{source_id}")

    async def start_tile_server(self):
        async with self._tile_server_lock:
            if not self._tile_server_started.is_set():
                self._tile_server_task = create_task(self._start_tile_server())
                await self._tile_server_started.wait()

    async def stop_tile_server(self):
        async with self._tile_server_lock:
            if self._tile_server_started.is_set():
                self._tile_server_shutdown.set()

    async def add_tiler_layer(
        self,
        path: str,
        variable: str,
        colormap_name: str = "viridis",
        rescale: tuple[float, float] | None = None,
        scale: int = 1,
        name: str = "Tiler Layer",
        opacity: float = 1,
    ):
        await self.start_tile_server()

        _url = f"file://{Path(path).absolute()}"
        params = {
            "server_url": self._tile_server_url,
            "url": _url,
            "scale": str(scale),
            "colormap_name": colormap_name,
            "variable": variable,
        }
        if rescale is not None:
            params["rescale"] = f"{rescale[0]},{rescale[1]}"
        source_id = str(uuid4())
        url = (
            f"/jupytergis_tiler/{source_id}/tiles/WebMercatorQuad/"
            + "{z}/{x}/{y}.png?"
            + urlencode(params)
        )
        source = {
            "type": SourceType.RasterSource,
            "name": f"{name} Source",
            "parameters": {
                "url": url,
                "minZoom": 0,
                "maxZoom": 24,
            },
        }
        self._add_source(OBJECT_FACTORY.create_source(source, self), id=source_id)
        layer = {
            "type": LayerType.RasterLayer,
            "name": name,
            "visible": True,
            "parameters": {"source": source_id, "opacity": opacity},
        }
        self._include_tile_server_router(source_id)
        return self._add_layer(OBJECT_FACTORY.create_layer(layer, self))
