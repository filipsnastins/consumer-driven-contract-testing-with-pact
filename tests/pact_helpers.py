import os
from typing import TypedDict, TypeVar, cast

import git
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
    verbose: bool


def get_pact_verifier_options() -> PactVerifierOptions:
    repo = git.Repo()
    broker_token = os.getenv("PACT_BROKER_TOKEN")
    return PactVerifierOptions(
        broker_url=os.getenv("PACT_BROKER_BASE_URL", "http://localhost:9292"),
        broker_username=None if broker_token else os.getenv("PACT_BROKER_USERNAME", "pactbroker"),
        broker_password=None if broker_token else os.getenv("PACT_BROKER_PASSWORD", "pactbroker"),
        broker_token=broker_token,
        consumer_version_selectors=[
            {"mainBranch": True},
            {"matchingBranch": True},
            {"deployedOrReleased": True},
        ],
        publish_verification_results=True if os.getenv("PACT_PUBLISH_VERIFICATION_RESULTS") else False,
        publish_version=os.getenv("GIT_COMMIT") or repo.head.object.hexsha,
        provider_version_branch=os.getenv("GIT_BRANCH") or repo.active_branch.name,
        enable_pending=True,
        verbose=True,
    )


def create_proto_from_pact(proto_class: type[ProtoType], expected_message: dict | Matcher) -> ProtoType:
    generated_values = cast(dict, get_generated_values(expected_message))
    return ParseDict(generated_values, proto_class())


def proto_to_dict(data: ProtoMessage) -> dict:
    return MessageToDict(data, preserving_proto_field_name=True)
