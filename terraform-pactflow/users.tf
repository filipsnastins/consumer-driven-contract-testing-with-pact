resource "pact_user" "default" {
  name   = var.default_user_name
  active = true
  email  = var.default_user_email
  type   = "user"
}
