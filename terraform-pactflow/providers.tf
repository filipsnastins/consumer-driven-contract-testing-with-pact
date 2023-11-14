terraform {
  required_version = "<= 1.5.5"

  required_providers {
    pact = {
      source  = "pactflow/pact"
      version = "0.9.1"
    }
  }
}

provider "pact" {
  host         = var.pact_host
  access_token = var.pact_access_token
}
