resource "pact_webhook" "default" {
  team = var.team_uuid

  events = ["contract_requiring_verification_published"]

  description = "Pact: Consumer contract requiring verification published (POST api.github.com)"

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
  "event_type": "Pact: Consumer contract requiring verification published",
  "client_payload": {
    "pact_url": "$${pactbroker.pactUrl}",
    "sha": "$${pactbroker.providerVersionNumber}",
    "branch": "$${pactbroker.providerVersionBranch}",
    "pytest_selector": "${var.pytest_selector}",
    "message": "Verify changed Pact for consumer '$${pactbroker.consumerName}' version '$${pactbroker.consumerVersionNumber}' branch '$${pactbroker.consumerVersionBranch}' by provider '$${pactbroker.providerName}' version '$${pactbroker.providerVersionNumber}' branch '$${pactbroker.providerVersionBranch}' ($${pactbroker.providerVersionDescriptions}) (workflow dispatch)"
  }
}
EOF
  }
}
