resource "pact_webhook" "default" {
  team = var.team_uuid

  events = ["contract_requiring_verification_published"]

  description = "[PactFlow] Consumer - contract requiring verification published (POST api.github.com)"

  webhook_consumer = {
    name = var.webhook_consumer_name
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
  "event_type": "[PactFlow] Consumer - contract requiring verification published",
  "client_payload": {
    "pytest_selector": "${var.pytest_selector}",
    "pact_url": "$${pactbroker.pactUrl}",
    "sha": "$${pactbroker.consumerVersionNumber}",
    "branch": "$${pactbroker.consumerVersionBranch}",
    "message": "Verify changed Pact for consumer '$${pactbroker.consumerName}' version '$${pactbroker.consumerVersionNumber}' branch '$${pactbroker.consumerVersionBranch}' by provider '$${pactbroker.providerName}' version '$${pactbroker.providerVersionNumber}' ($${pactbroker.providerVersionDescriptions}) (workflow dispatch)"
  }
}
EOF
  }
}
