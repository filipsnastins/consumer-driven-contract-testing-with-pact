# pact-tomodachi-contract-testing

- Generate Protobuf with [buf](https://buf.build)

```bash
brew install bufbuild/buf/buf

cd src/proto
buf generate .
```

- Run applications locally with Docker Compose

```bash
docker compose up
```

- Create order

```bash
curl -X POST --header "Content-Type: application/json" -d '{
  "customer_id": "97c05e79-5902-451f-b96e-f06c8fc3ed68",
  "order_total": 12399
}' http://localhost:9702/orders
```
