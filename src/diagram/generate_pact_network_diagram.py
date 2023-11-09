"""Generate a network diagram of the Pact Broker integrations.

Pacticipants must be named in the following format:
    <consumer_name>--<protocol>

Note that communication protocol is denoted by double dashes (--).

Example namings:
    - frontend--graphql
    - frontend--rest
    - service-customers--sns
    - service-order-history--sns
    - service-orders--sns

The diagram is generated in the DOT format, which can be converted to an image using Graphviz.
Read more at: https://docs.pact.io/pact_broker/network_graph

Usage:
    generate_pact_network_diagram.py [-h] pact_broker_url network_output_file

Example usage:
    python -m diagram.generate_pact_network_diagram http://localhost:9292 docs/pact/network.dot

Create PNG image from DOT file:
    dot docs/pact/network.dot -odocs/pact/network.png -Tpng

Create SVG image from DOT file:
    dot docs/pact/network.dot -odocs/pact/network.svg -Tsvg

Putting it all together:
    python -m diagram.generate_pact_network_diagram http://localhost:9292 docs/pact/network.dot && \
    dot docs/pact/network.dot -odocs/pact/network.png -Tpng && \
    dot docs/pact/network.dot -odocs/pact/network.svg -Tsvg
"""
import argparse
import string
from dataclasses import dataclass
from pathlib import Path

import jinja2
import requests

PROTOCOL_LETTER_CASE_MAP = {
    "graphql": "GraphQL",
}


@dataclass(frozen=True)
class Pacticipant:
    name: str
    label: str

    @staticmethod
    def create(name: str) -> "Pacticipant":
        name = _split_pacticipant_name(name)
        label = string.capwords(name.replace("-", " "))
        return Pacticipant(name=name, label=label)


@dataclass(frozen=True)
class Integration:
    consumer: Pacticipant
    provider: Pacticipant
    protocol: str

    @staticmethod
    def create(consumer_name: str, provider_name: str) -> "Integration":
        consumer = Pacticipant.create(consumer_name)
        provider = Pacticipant.create(provider_name)
        protocol = _map_integration_protocol(consumer_name=consumer_name, provider_name=provider_name)
        return Integration(consumer, provider, protocol)


def _split_pacticipant_name(name: str) -> str:
    split = name.split("--")
    assert (
        len(split) == 2
    ), f"Pacticipant name '{name}' must end with the protocol denoted by --, e.g. 'service-orders--sns'"
    return split[0]


def _map_integration_protocol(consumer_name: str, provider_name: str) -> str:
    _, protocol_consumer = consumer_name.split("--")
    _, protocol_provider = provider_name.split("--")
    assert (
        protocol_consumer == protocol_provider
    ), f"Consumer '{consumer_name}' and provider '{provider_name}' must have the same protocols"
    return PROTOCOL_LETTER_CASE_MAP.get(protocol_consumer) or protocol_consumer.upper()


def get_pact_pacticipants(pact_broker_url: str) -> list[Pacticipant]:
    response = requests.get(f"{pact_broker_url}/pacticipants", headers={"Accept": "application/hal+json"})
    response.raise_for_status()
    pacticipants = list(
        {Pacticipant.create(name=pacticipant["name"]) for pacticipant in response.json()["_embedded"]["pacticipants"]}
    )
    return sorted(pacticipants, key=lambda pacticipant: pacticipant.name)


def get_pact_integrations(pact_broker_url: str) -> list[Integration]:
    response = requests.get(f"{pact_broker_url}/integrations", headers={"Accept": "application/hal+json"})
    response.raise_for_status()
    integrations = list(
        {
            Integration.create(
                consumer_name=integration["consumer"]["name"], provider_name=integration["provider"]["name"]
            )
            for integration in response.json()["_embedded"]["integrations"]
        }
    )
    return sorted(
        integrations,
        key=lambda integration: (integration.consumer.name, integration.provider.name, integration.protocol),
    )


def generate_pact_network_diagram(pacticipants: list[Pacticipant], integrations: list[Integration]) -> str:
    with open(Path(__file__).parent / "pact_network_diagram.jinja2") as file:
        template = jinja2.Template(file.read())
        return template.render(pacticipants=pacticipants, integrations=integrations)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pact_broker_url", help="Pact Broker URL")
    parser.add_argument("network_output_file", help="Path to network diagram output file (.dot format)")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    pacticipants = get_pact_pacticipants(args.pact_broker_url)
    integrations = get_pact_integrations(args.pact_broker_url)
    network = generate_pact_network_diagram(pacticipants, integrations)

    with open(args.network_output_file, "wt") as file:
        file.write(network)
