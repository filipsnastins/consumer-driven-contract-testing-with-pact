module "webhook__contract_requiring_verification_published" {
  source = "../webhook--contract-requiring-verification-published"

  team_uuid                = var.team_uuid
  webhook_provider_name    = var.webhook_provider_name
  github_organization      = var.github_organization
  github_repository_name   = var.github_repository_name
  pytest_provider_selector = var.pytest_provider_selector
}
