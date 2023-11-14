from typing import Generator, cast

import pytest
from docker.models.images import Image as DockerImage
from tomodachi_testcontainers import MotoContainer, TomodachiContainer
from tomodachi_testcontainers.utils import get_available_port

from tests.pact_helpers import Verifier

pytestmark = [pytest.mark.customers__rest(), pytest.mark.provider(), pytest.mark.pactflow(), pytest.mark.order(2)]


@pytest.fixture(scope="module")
def service_customers_container(
    testcontainers_docker_image: DockerImage, moto_container: MotoContainer
) -> Generator[TomodachiContainer, None, None]:
    with (
        TomodachiContainer(
            image=str(testcontainers_docker_image.id),
            edge_port=get_available_port(),
        )
        .with_env("ENVIRONMENT", "autotest")
        .with_env("DYNAMODB_TABLE_NAME", "autotest-customers")
        .with_env("AWS_REGION", "us-east-1")
        .with_env("AWS_ACCESS_KEY_ID", "testing")
        .with_env("AWS_SECRET_ACCESS_KEY", "testing")
        .with_env("AWS_ENDPOINT_URL", moto_container.get_internal_url())
        .with_command("tomodachi run src/customers/tomodachi_app.py --production")
    ) as container:
        yield cast(TomodachiContainer, container)


@pytest.fixture(scope="module")
def verifier(service_customers_container: TomodachiContainer) -> Verifier:
    return Verifier(
        provider="service-customers--rest",
        provider_base_url=service_customers_container.get_external_url(),
    )


def test_verify_consumer_contracts(verifier: Verifier, service_customers_container: TomodachiContainer) -> None:
    code, _ = verifier.verify_with_broker(
        provider_states_setup_url=f"{service_customers_container.get_external_url()}/_pact/provider_states",
    )
    assert code == 0
