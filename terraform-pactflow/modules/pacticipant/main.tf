resource "pact_pacticipant" "default" {
  name           = var.name
  display_name   = var.display_name
  repository_url = "github.com/${var.github_organization_name}/${var.github_repository_name}"
  main_branch    = var.main_branch
}
