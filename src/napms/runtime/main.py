from napms.runtime.composition import build_local_dev_http_api
from napms.runtime.config import load_http_runtime_config
from napms.runtime.http_api import configure_json_logging


config = load_http_runtime_config()
configure_json_logging()
app = build_local_dev_http_api(config=config)


def run() -> None:
    import uvicorn

    uvicorn.run(
        "napms.runtime.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=False,
    )
