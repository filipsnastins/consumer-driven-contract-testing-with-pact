from typing import Generator, cast

import pytest
from docker.models.images import Image as DockerImage
from tomodachi_testcontainers import MotoContainer, TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port

from tests.pact_helpers import Verifier

pytestmark = [pytest.mark.orders__rest(), pytest.mark.provider(), pytest.mark.order(2)]


@pytest.fixture(scope="module")
def service_orders_container(
    testcontainers_docker_image: DockerImage, moto_container: MotoContainer
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(
            image=str(testcontainers_docker_image.id),
            edge_port=get_available_port(),
        )
        .with_env("ENVIRONMENT", "autotest")
        .with_env("DYNAMODB_TABLE_NAME", "autotest-orders")
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_ENDPOINT_URL", moto_container.get_internal_url())
        .with_command("tomodachi run src/orders/tomodachi_app.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest.fixture(scope="module")
def verifier(service_orders_container: TomodachiContainer) -> Verifier:
    return Verifier(
        provider="service-orders--rest",
        provider_base_url=service_orders_container.get_external_url(),
    )


def test_verify_consumer_contracts(verifier: Verifier) -> None:
    verifier.verify_with_broker(provider_states_setup_url="/_pact/provider_states")
