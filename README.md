# contract-testing-pact-python

**WIP**

An example of applying Consumer-Driven Contract Testing (CDC) for testing microservice compatibility in isolation.

## Development

### Start local environment

- Generate Protobuf with [buf](https://buf.build)

```bash
brew install bufbuild/buf/buf

cd src/adapters/proto
buf generate .
```

- Run applications and Pact Broker locally with Docker Compose

```bash
docker compose up
```

### URLs

- Pact Broker URL: <http://localhost:9292>

- DynamoDB Admin: <http://localhost:8001>

- Order history GraphQL sandbox: <http://localhost:9703/graphql>

### Sample requests

- Create customer

```bash
curl -X POST --header "Content-Type: application/json" -d '{
  "name": "John Doe"
}' http://localhost:9701/customer
```

- Get customer

```bash
curl http://localhost:9701/customer/4dc8d1ed-9737-48fa-8e3f-ec2b272b7cac
```

- Create order

```bash
curl -X POST --header "Content-Type: application/json" -d '{
  "customer_id": "4dc8d1ed-9737-48fa-8e3f-ec2b272b7cac",
  "order_total": 12399
}' http://localhost:9702/order
```

- Get order

```bash
curl http://localhost:9702/order/8fccc85c-bbdd-47fb-b6c9-c5ed9a8d88df
```

- Get order history for all customers

```bash
curl -X POST -H "Content-Type: application/json" -d '{"query": "{getAllCustomers {id name orders {id orderTotal state}}}"}' http://localhost:9703/graphql
```

### Format and lint code, and run tests

```bash
poetry run format

poetry run lint

poetry run test
poetry run test-ci
```
