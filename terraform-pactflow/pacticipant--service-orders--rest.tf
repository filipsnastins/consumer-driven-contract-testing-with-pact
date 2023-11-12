module "pact_pacticipant__service-orders--rest" {
  source = "./modules/pacticipant"

  name                     = "service-orders--rest"
  display_name             = "Service Orders (REST)"
  github_organization_name = "filipsnastins"
  github_repository_name   = "consumer-driven-contract-testing-with-pact-python"
}

module "pact_pacticipant_webhooks__service-orders--rest" {
  source = "./modules/pacticipant-webhooks"

  team_uuid                = pact_team.default.uuid
  webhook_provider_name    = module.pact_pacticipant__service-orders--rest.name
  github_organization      = module.pact_pacticipant__service-orders--rest.github_organization_name
  github_repository_name   = module.pact_pacticipant__service-orders--rest.github_repository_name
  pytest_provider_selector = "orders"

  depends_on = [module.pact_pacticipant__service-orders--rest]
}
