module "pact_pacticipant__service-order-history--sns" {
  source = "./modules/pacticipant"

  name                     = "service-order-history--sns"
  display_name             = "Service Order History (SNS)"
  github_organization_name = "filipsnastins"
  github_repository_name   = "consumer-driven-contract-testing-with-pact-python"
}

module "pact_pacticipant_webhooks__service-order-history--sns" {
  source = "./modules/pacticipant-webhooks"

  team_uuid                = pact_team.default.uuid
  webhook_provider_name    = module.pact_pacticipant__service-order-history--sns.name
  github_organization      = module.pact_pacticipant__service-order-history--sns.github_organization_name
  github_repository_name   = module.pact_pacticipant__service-order-history--sns.github_repository_name
  pytest_provider_selector = "order_history"

  depends_on = [module.pact_pacticipant__service-order-history--sns]
}
