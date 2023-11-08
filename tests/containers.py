from typing import Any

from tomodachi_testcontainers.containers.common import WebContainer


class FastAPIContainer(WebContainer):
    def __init__(
        self,
        image: str,
        internal_port: int = 8000,
        edge_port: int = 8000,
        http_healthcheck_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            image=image,
            internal_port=internal_port,
            edge_port=edge_port,
            http_healthcheck_path=http_healthcheck_path,
            **kwargs,
        )

    def log_message_on_container_start(self) -> str:
        return f"FastAPI service: http://localhost:{self.edge_port}"
