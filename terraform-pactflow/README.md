# PactFlow (PactBroker) Configuration with Terraform

Example Terraform project for configuring [PactFlow](https://pactflow.io/).

The Terraform definitions automate configuration of:

- Creation of user accounts and teams.
- Creation of Pacticipants.
- Configuration of Webhooks.

For more information about the Pact Broker Terraform Provider,
[check out the documentation on the Pact website](https://docs.pact.io/pact_broker/terraform_provider) or
[the Terraform Registry](https://registry.terraform.io/providers/pactflow/pact).

## Configuring the PactFlow instance

- Create a free account on <https://pactflow.io>

- Install Terraform with [tfenv](https://github.com/tfutils/tfenv).
  Terraform version will be read from [.terraform-version](.terraform-version) file.

```bash
brew install tfenv
tfenv install
```

- Create a [Pactflow read/write API token](https://docs.pactflow.io/#configuring-your-api-token)
  and export environment variables:

```bash
export TF_VAR_pact_host=https://<your-account-name>.pactflow.io
 export TF_VAR_pact_access_token=<your-read-write-api-token>

export TF_VAR_default_user_name=<your-first-and-last-name>  # Name with which you registered on pactflow.io
export TF_VAR_default_user_email=<your-email>
```

- Init Terraform modules

```bash
terraform init
```

- We'll have to import default user and team to Terraform resources because Pact Terraform provider
  doesn't support [data sources](https://developer.hashicorp.com/terraform/language/data-sources).

- Import default user to Terraform state.
  You can find your user `uuid` through the HAL browser with `GET /admin/users` at
  <https://your-account-name.pactflow.io/hal-browser/browser.html#https://your-account-name.pactflow.io/admin/users>.
  Read more about importing `pact_user` resource at
  [registry.terraform.io](https://registry.terraform.io/providers/pactflow/pact/latest/docs/resources/user#importing).

```bash
terraform import pact_user.default <your-user-uuid>
```

- Import default team to Terraform state.
  Your can find the default team `uuid` through the HAL browser with `GET /admin/teams` at
  <https://your-account-name.pactflow.io/hal-browser/browser.html#https://your-account-name.pactflow.io/admin/teams>.
  Read more about importing `pact_team` resource at
  [registry.terraform.io](https://registry.terraform.io/providers/pactflow/pact/latest/docs/resources/team#importing).

```bash
terraform import pact_team.default <default-team-uuid>
```

- Run Terraform apply to create the rest of the resources

```bash
terraform apply
```

## Development

- Lint

```bash
brew install tflint
brew install tfsec

tflint
tfsec
```
