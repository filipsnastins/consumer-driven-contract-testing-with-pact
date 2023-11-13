# TODOs

- [ ] Documentation in README

  - [ ] Motivation of contract testing, and especially consumer-driven contract testing
  - [ ] Breaking change examples - how pact would catch them
  - [x] Running in CI
  - [ ] Using 'Can I Deploy'?
  - [ ] Configuring the Pact Broker and PactFlow with Terraform

- [ ] Pytest

  - [ ] When verifying Pact Provider contract, use PACT_URL from environment
        to verify only given changed consumer Pact

- [ ] CI

  - [x] Two types of webhooks and workflows
    - Consumer contract changed
    - Provider contract changed
  - [x] pytest_selector include protocol name

- [ ] Terraform
  - [ ] When done, remove my name, email and default PactFlow URL
