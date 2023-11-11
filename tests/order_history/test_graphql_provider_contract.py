from typing import Generator, cast

import pytest
from docker.models.images import Image as DockerImage
from pact import Verifier
from tomodachi_testcontainers.utils import get_available_port

from tests.containers import FastAPIContainer
from tests.pact_helpers import get_pact_verifier_options

pytestmark = [pytest.mark.provider(), pytest.mark.pactflow(), pytest.mark.order(2)]


@pytest.fixture(scope="module")
def service_order_history_container(
    testcontainers_docker_image: DockerImage,
) -> Generator[FastAPIContainer, None, None]:
    with (
        FastAPIContainer(
            image=str(testcontainers_docker_image.id),
            edge_port=get_available_port(),
            http_healthcheck_path="/health",
        )
        .with_env("ENVIRONMENT", "autotest")
        .with_env("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        .with_command("uvicorn order_history.fastapi_app:app --host 0.0.0.0")
    ) as container:
        yield cast(FastAPIContainer, container)


@pytest.fixture(scope="module")
def verifier(service_order_history_container: FastAPIContainer) -> Verifier:
    return Verifier(
        provider="service-order-history--graphql",
        provider_base_url=service_order_history_container.get_external_url(),
    )


def test_verify_consumer_contracts(verifier: Verifier, service_order_history_container: FastAPIContainer) -> None:
    code, _ = verifier.verify_with_broker(
        **get_pact_verifier_options(),
        provider_states_setup_url=f"{service_order_history_container.get_external_url()}/_pact/provider_states",
    )
    assert code == 0
