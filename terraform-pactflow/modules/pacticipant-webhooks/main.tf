module "webhook__consumer_contract_requiring_verification_published" {
  source = "../webhook--consumer-contract-requiring-verification-published"

  team_uuid              = var.team_uuid
  webhook_provider_name  = var.pacticipant_name
  github_organization    = var.github_organization
  github_repository_name = var.github_repository_name
  pytest_selector        = var.pytest_selector
}
