# contract-testing-pact-python

**WIP**

An example of applying Consumer-Driven Contract Testing (CDC) for testing microservice compatibility in isolation.

## Development

- Generate Protobuf with [buf](https://buf.build)

```bash
brew install bufbuild/buf/buf

cd src/proto
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
curl http://localhost:9701/customer/290210dc-10c8-4eb0-91f0-fb9dfb727513
```

- Create order

```bash
curl -X POST --header "Content-Type: application/json" -d '{
  "customer_id": "290210dc-10c8-4eb0-91f0-fb9dfb727513",
  "order_total": 12399
}' http://localhost:9702/order
```

- Get order

```bash
curl http://localhost:9702/order/dd7ab823-223b-480e-858b-0f9acd6f7314
```
