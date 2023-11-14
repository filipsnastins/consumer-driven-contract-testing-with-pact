variable "pact_host" {
  type = string
}

variable "pact_access_token" {
  type      = string
  sensitive = true
}

variable "default_user_name" {
  type = string
}

variable "default_user_email" {
  type = string
}
