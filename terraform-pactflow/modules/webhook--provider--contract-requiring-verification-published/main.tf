resource "pact_webhook" "default" {
  team = var.team_uuid

  events = ["contract_requiring_verification_published"]

  description = "[PactFlow] Provider - contract requiring verification published (POST api.github.com)"

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
  "event_type": "[PactFlow] Provider - contract requiring verification published",
  "client_payload": {
    "pytest_selector": "${var.pytest_selector}",
    "pact_url": "$${pactbroker.pactUrl}",
    "sha": "$${pactbroker.providerVersionNumber}",
    "branch": "$${pactbroker.providerVersionBranch}",
    "message": "Verify changed Pact for provider '$${pactbroker.providerName}' version '$${pactbroker.providerVersionNumber}' branch '$${pactbroker.providerVersionBranch}' by consumer '$${pactbroker.consumerName}' version '$${pactbroker.consumerVersionNumber}' branch '$${pactbroker.consumerVersionBranch}' ($${pactbroker.providerVersionDescriptions}) (workflow dispatch)"
  }
}
EOF
  }
}
