resource "pact_webhook" "default" {
  team = var.team_uuid

  events = ["contract_requiring_verification_published"]

  description = "Contract requiring verification published (api.github.com)"

  webhook_provider = {
    name = var.webhook_provider_name
  }

  request {
    url    = "https://api.github.com/repos/${var.github_organization}/${var.github_repository_name}/dispatches"
    method = "POST"
    headers = {
      "Content-Type"  = "application/json",
      "Accept"        = "application/vnd.github.everest-preview+json",
      "Authorization" = "Bearer $${user.GitHubToken}"

    }
    body = <<EOF
{
  "event_type": "Pact: contract requiring verification published",
  "client_payload": {
    "pytest_provider_selector": "${var.pytest_provider_selector}",
    "pact_url": "$${pactbroker.pactUrl}",
    "sha": "$${pactbroker.providerVersionNumber}",
    "branch": "$${pactbroker.providerVersionBranch}",
    "message": "Verify changed pact for '$${pactbroker.consumerName}' version '$${pactbroker.consumerVersionNumber}' branch '$${pactbroker.consumerVersionBranch}' by '$${pactbroker.providerVersionNumber}' ($${pactbroker.providerVersionDescriptions}) (user run)"
  }
}
EOF
  }
}
