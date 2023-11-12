variable "name" {
  type = string
}

variable "display_name" {
  type = string
}

variable "main_branch" {
  type    = string
  default = "main"
}

variable "github_organization_name" {
  type = string
}

variable "github_repository_name" {
  type = string
}
