module "pact_pacticipant__frontend--rest" {
  source = "./modules/pacticipant"

  name                     = "frontend--rest"
  display_name             = "Frontend (REST)"
  github_organization_name = "filipsnastins"
  github_repository_name   = "consumer-driven-contract-testing-with-pact-python"
}

module "pact_pacticipant_webhooks__frontend--rest" {
  source = "./modules/pacticipant-webhooks"

  team_uuid                = pact_team.default.uuid
  webhook_provider_name    = module.pact_pacticipant__frontend--rest.name
  github_organization      = module.pact_pacticipant__frontend--rest.github_organization_name
  github_repository_name   = module.pact_pacticipant__frontend--rest.github_repository_name
  pytest_provider_selector = "frontend"

  depends_on = [module.pact_pacticipant__frontend--rest]
}
