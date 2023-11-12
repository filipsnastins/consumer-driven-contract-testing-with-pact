resource "pact_team" "default" {
  name = "Default"

  users = [
    pact_user.default.uuid,
  ]

  pacticipants = [
    module.pact_pacticipant__frontend--graphql.name,
    module.pact_pacticipant__frontend--rest.name,
    module.pact_pacticipant__service-customers--rest.name,
    module.pact_pacticipant__service-customers--sns.name,
    module.pact_pacticipant__service-order-history--graphql.name,
    module.pact_pacticipant__service-order-history--sns.name,
    module.pact_pacticipant__service-orders--rest.name,
    module.pact_pacticipant__service-orders--sns.name,
  ]

  lifecycle {
    prevent_destroy = true
  }
}
