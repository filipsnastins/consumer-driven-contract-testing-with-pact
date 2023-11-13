module "webhook__consumer__contract_requiring_verification_published" {
  source = "../webhook--consumer--contract-requiring-verification-published"

  team_uuid              = var.team_uuid
  webhook_consumer_name  = var.pacticipant_name
  github_organization    = var.github_organization
  github_repository_name = var.github_repository_name
  pytest_selector        = var.pytest_selector
}

module "webhook__provider__contract_requiring_verification_published" {
  source = "../webhook--provider--contract-requiring-verification-published"

  team_uuid              = var.team_uuid
  webhook_provider_name  = var.pacticipant_name
  github_organization    = var.github_organization
  github_repository_name = var.github_repository_name
  pytest_selector        = var.pytest_selector
}
