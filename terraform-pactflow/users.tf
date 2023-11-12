resource "pact_user" "default" {
  name   = "Filips Nastins"
  active = true
  email  = "nastinsfilips@gmail.com"
  type   = "user"

  lifecycle {
    prevent_destroy = true
  }
}
