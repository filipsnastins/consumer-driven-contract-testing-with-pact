module "pact_pacticipant__service-orders--sns" {
  source = "./modules/pacticipant"

  name                     = "service-orders--sns"
  display_name             = "Service Orders (SNS)"
  github_organization_name = "filipsnastins"
  github_repository_name   = "consumer-driven-contract-testing-with-pact-python"
}

module "pact_pacticipant_webhooks__service-orders--sns" {
  source = "./modules/pacticipant-webhooks"

  team_uuid              = pact_team.default.uuid
  pacticipant_name       = module.pact_pacticipant__service-orders--sns.name
  github_organization    = module.pact_pacticipant__service-orders--sns.github_organization_name
  github_repository_name = module.pact_pacticipant__service-orders--sns.github_repository_name
  pytest_selector        = "orders__sns"

  depends_on = [module.pact_pacticipant__service-orders--sns]
}
