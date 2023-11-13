module "pact_pacticipant__service-customers--rest" {
  source = "./modules/pacticipant"

  name                     = "service-customers--rest"
  display_name             = "Service Customers (REST)"
  github_organization_name = "filipsnastins"
  github_repository_name   = "consumer-driven-contract-testing-with-pact-python"
}

module "pact_pacticipant_webhooks__service-customers--rest" {
  source = "./modules/pacticipant-webhooks"

  team_uuid              = pact_team.default.uuid
  pacticipant_name       = module.pact_pacticipant__service-customers--rest.name
  github_organization    = module.pact_pacticipant__service-customers--rest.github_organization_name
  github_repository_name = module.pact_pacticipant__service-customers--rest.github_repository_name
  pytest_selector        = "customers__rest"

  depends_on = [module.pact_pacticipant__service-customers--rest]
}
