variable "pact_host" {
  type    = string
  default = "https://filipsnastins.pactflow.io"
}

variable "pact_access_token" {
  type      = string
  sensitive = true
}
