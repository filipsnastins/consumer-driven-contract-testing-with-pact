resource "pact_user" "default" {
  name   = "John Doe"
  active = true
  email  = "john.doe@example.com"
  type   = "user"

  lifecycle {
    prevent_destroy = true
  }
}
