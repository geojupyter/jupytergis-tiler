import httpx
import tornado
from jupyter_server.base.handlers import JupyterHandler


class JupyterGISHandler(JupyterHandler):
    @tornado.web.authenticated
    async def get(self, path):
        params = {key: val[0].decode() for key, val in self.request.arguments.items()}
        server_url = params.pop("server_url")
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{server_url}/{path}", params=params)
            self.set_status(r.status_code)
            if content_type := r.headers.get("content-type"):
                self.set_header("Content-Type", content_type)
            self.write(r.content)
