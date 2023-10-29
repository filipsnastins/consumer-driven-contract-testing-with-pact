from multiprocessing import Process
from typing import Generator

import pytest
import uvicorn
from pact import Verifier
from tomodachi_testcontainers.utils import get_available_port, wait_for_http_healthcheck
from yarl import URL

from order_history.fastapi_app import app

pytestmark = pytest.mark.order(2)

DEFAULT_OPTS = {
    "broker_url": "http://localhost:9292",
    "broker_username": "pactbroker",
    "broker_password": "pactbroker",
    "publish_verification_results": True,
    "publish_version": "0.0.1",
}


def run_server(host: str, port: int) -> None:
    uvicorn.run(app, host=host, port=port)


@pytest.fixture(scope="module")
def provider_url() -> URL:
    return URL(f"http://localhost:{get_available_port()}")


@pytest.fixture(scope="module")
def verifier(provider_url: URL) -> Generator[Verifier, None, None]:
    proc = Process(
        target=run_server,
        kwargs={"host": provider_url.host, "port": provider_url.port},
        daemon=True,
    )
    proc.start()
    wait_for_http_healthcheck(url=f"{provider_url}/health")
    yield Verifier(
        provider="service-order-history--graphql",
        provider_base_url=provider_url,
    )
    proc.kill()


def test_verify_consumer_contracts(verifier: Verifier, provider_url: URL) -> None:
    code, _ = verifier.verify_with_broker(
        **DEFAULT_OPTS,
        provider_states_setup_url=f"{provider_url}/_pact/provider_states",
    )
    assert code == 0
