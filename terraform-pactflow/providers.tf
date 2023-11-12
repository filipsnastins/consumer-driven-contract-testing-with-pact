terraform {
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
