module "pact_pacticipant__service-customers--sns" {
  source = "./modules/pacticipant"

  name                     = "service-customers--sns"
  display_name             = "Service Customers (SNS)"
  github_organization_name = "filipsnastins"
  github_repository_name   = "consumer-driven-contract-testing-with-pact-python"
}

module "pact_pacticipant_webhooks__service-customers--sns" {
  source = "./modules/pacticipant-webhooks"

  team_uuid                = pact_team.default.uuid
  webhook_provider_name    = module.pact_pacticipant__service-customers--sns.name
  github_organization      = module.pact_pacticipant__service-customers--sns.github_organization_name
  github_repository_name   = module.pact_pacticipant__service-customers--sns.github_repository_name
  pytest_provider_selector = "customers"

  depends_on = [module.pact_pacticipant__service-customers--sns]
}
