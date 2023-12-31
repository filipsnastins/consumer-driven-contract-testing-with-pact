import os
from typing import TypedDict, TypeVar, cast
from urllib.parse import urljoin

import git
import pact
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message as ProtoMessage
from pact.matchers import Matcher, get_generated_values

ProtoType = TypeVar("ProtoType", bound=ProtoMessage)


class PactConsumerSelectorMainBranch(TypedDict):
    mainBranch: bool


class PactConsumerSelectorMatchingBranch(TypedDict):
    matchingBranch: bool


class PactConsumerSelectorDeployed(TypedDict):
    deployed: bool


class PactConsumerSelectorReleased(TypedDict):
    released: bool


class PactConsumerSelectorDeployedOrReleased(TypedDict):
    deployedOrReleased: bool


class PactConsumerSelectorLatest(TypedDict):
    latest: bool


PactConsumerSelectorsType = list[
    PactConsumerSelectorMainBranch
    | PactConsumerSelectorMatchingBranch
    | PactConsumerSelectorDeployed
    | PactConsumerSelectorReleased
    | PactConsumerSelectorDeployedOrReleased
    | PactConsumerSelectorLatest
]


class PactVerifierOptions(TypedDict):
    broker_url: str
    broker_username: str | None
    broker_password: str | None
    broker_token: str | None
    consumer_version_selectors: PactConsumerSelectorsType
    publish_verification_results: bool
    publish_version: str
    provider_version_branch: str
    enable_pending: bool
    include_wip_pacts_since: str | None
    verbose: bool


class Verifier(pact.Verifier):
    def verify_pacts(  # pylint: disable=arguments-differ
        self, *pact_urls: str, provider_states_setup_url: str | None = None
    ) -> None:
        return_code, _ = super().verify_pacts(
            *pact_urls,
            provider_states_setup_url=self._compose_provider_states_setup_url(provider_states_setup_url),
            **get_verify_with_pact_url_options(),
        )
        assert return_code == 0, f"Expected returned_code = 0, actual = {return_code}"

    def verify_with_broker(  # pylint: disable=arguments-differ
        self, provider_states_setup_url: str | None = None
    ) -> None:
        return_code, _ = super().verify_with_broker(
            provider_states_setup_url=self._compose_provider_states_setup_url(provider_states_setup_url),
            **get_pact_verify_with_broker_options(),
        )
        assert return_code == 0, f"Expected returned_code = 0, actual = {return_code}"

    def _compose_provider_states_setup_url(self, provider_states_setup_url: str | None) -> str | None:
        if provider_states_setup_url is None:
            return None
        return urljoin(self.provider_base_url, provider_states_setup_url)


class MessageProvider(pact.MessageProvider):
    provider: pact.MessageProvider

    def verify(self) -> None:
        verifier = self._create_verifier()
        verifier.verify_pacts(f"{self.pact_dir}/{self._pact_file()}")

    def verify_with_broker(self) -> None:  # pylint: disable=arguments-differ
        verifier = self._create_verifier()
        if pact_url := os.getenv("PACT_URL"):
            verifier.verify_pacts(pact_url)
        else:
            verifier.verify_with_broker()

    def _create_verifier(self) -> Verifier:
        return Verifier(provider=self.provider, provider_base_url=self._proxy_url())


def get_verify_with_pact_url_options() -> PactVerifierOptions:
    repo = git.Repo()
    broker_token = os.getenv("PACT_BROKER_TOKEN")
    return PactVerifierOptions(
        broker_url=os.getenv("PACT_BROKER_BASE_URL", "http://localhost:9292"),
        broker_username=None if broker_token else os.getenv("PACT_BROKER_USERNAME", "pactbroker"),
        broker_password=None if broker_token else os.getenv("PACT_BROKER_PASSWORD", "pactbroker"),
        broker_token=broker_token,
        consumer_version_selectors=[],
        publish_verification_results=bool(os.getenv("PACT_PUBLISH_VERIFICATION_RESULTS")),
        publish_version=os.getenv("GIT_COMMIT") or repo.head.object.hexsha,
        provider_version_branch=os.getenv("GIT_BRANCH") or repo.active_branch.name,
        enable_pending=False,
        include_wip_pacts_since=None,
        verbose=bool(os.getenv("PACT_VERBOSE")),
    )


def get_pact_verify_with_broker_options() -> PactVerifierOptions:
    options = get_verify_with_pact_url_options()
    options["consumer_version_selectors"] = [{"mainBranch": True}, {"deployedOrReleased": True}]
    options["enable_pending"] = True
    return options


def create_proto_from_pact(proto_class: type[ProtoType], expected_message: dict | Matcher) -> ProtoType:
    generated_values = cast(dict, get_generated_values(expected_message))
    return ParseDict(generated_values, proto_class())


def proto_to_dict(data: ProtoMessage) -> dict:
    return MessageToDict(data, preserving_proto_field_name=True)
