# contract-testing-pact-python

**WIP**

An example of applying Consumer-Driven Contract Testing (CDC) for testing microservice compatibility in isolation.

## Development

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

- Pact Broker URL: <https://filipsnastins.pactflow.io>

- Create customer

```bash
curl -X POST --header "Content-Type: application/json" -d '{
  "name": "John Doe"
}' http://localhost:9701/customer
```

- Get customer

```bash
curl http://localhost:9701/customer/cf265033-8e25-42ba-a938-23fcb8f9797b
```

- Create order

```bash
curl -X POST --header "Content-Type: application/json" -d '{
  "customer_id": "5bf06495-39e9-4f01-81f1-a9c1dd219105",
  "order_total": 12399
}' http://localhost:9702/order
```

- Get order

```bash
curl http://localhost:9702/order/8fccc85c-bbdd-47fb-b6c9-c5ed9a8d88df
```
