# microservices-saga-sample
Naive attempt at using multiple microservices that implement the saga pattern with idempotency.

> Note: expect no best practices / solid coding patterns / error checking / data validation here - this is a hello world of a handful of services to test out compensating transactions as a learning exercise, and as such is constantly a work in progress.

Rought flow:

person => POST JSON to frontend svc =>
`frontend` svc publishes JSON to pubsub (and tags JSON with UUID) =>
consumed by `order` svc & order created and publish to pubsub when complete =>
consumed by `inventory` svc & inventory updated and publish to pubsub when complete (error if insufficient inventory and publish to error topic) =>
consumed by `payments` svc & payment "invoice" record created (error if initial JSON contains some field to indicate insufficient funds to simulate failure, and publish to error topic) =>
can consume success messages via `gcloud` CLI from `payment-complete` topic \ `payment-complete-sub` subscription

`janitor` is a naive transaction compensator service that listens to error topic and takes compensating actions against the `orders` & `inventory` services to remove stale records if downstream errors are detected. records are stored in either Firestore collections and subcollections, and (with the exception of the `users` collection) are keyed on a UUID assigned by the frontend service, and records in those various collections will get purged during compensation. the UUID also allows for idempotency, as replayed messages will be ignored if an existing record with the same UUID exists.

If running locally, make sure you create virtual environments for each service and install the required packages in each service's `requirements.txt`. I also make heavy use of `dotenv`, and will eventually document all the env vars you need to provide to each service.

### setup

create topics
```
for TOPIC in frontend order-created inventory-updated error payment-created
do
    gcloud pubsub topics create $TOPIC
done
```

create subscriptions
```
gcloud pubsub subscriptions create frontend-sub --topic=frontend
gcloud pubsub subscriptions create order-created-sub --topic=order-created
gcloud pubsub subscriptions create inventory-updated-sub --topic=inventory-updated
gcloud pubsub subscriptions create error-sub --topic=error
gcloud pubsub subscriptions create error-cli-sub --topic=error
gcloud pubsub subscriptions create payment-created-sub --topic=payment-created
```

Populate the user & inventory collections
```
python data-initialization-script/data-init.py
```

### Using this stuff

test POST via curl
```
curl -X POST http://127.0.0.1:8080/order \
   -H 'Content-Type: application/json' \
   -d '{"item":"widget","quantity":50,"user":"jack"}'
```
```
curl -X POST http://127.0.0.1:8080/order \
   -H 'Content-Type: application/json' \
   -d '{"item":"wotsit","quantity":80,"user":"jill"}'
```

Generate an error in the `payments` service by including a `payment-error` key in the JSON payload, which will trigger compensating actions in the upstream services:
```
curl -X POST http://127.0.0.1:8080/order    -H 'Content-Type: application/json'    -d '{"item":"wotsit","quantity":80,"user":"jill", "payment-error":"null"}'
```

Generate an error in the `inventory` service by setting some massive inventory, which will trigger compensating actions in the upstream services:
```
curl -X POST http://127.0.0.1:8080/order    -H 'Content-Type: application/json'    -d '{"item":"wotsit","quantity":500000,"user":"jill"}'
```

Watch for message success by consuming from the `payment-created` topic:
```
gcloud pubsub subscriptions pull payment-created-sub --auto-ack
```

Watch for errors by consuming from the `error` topic (be sure to use the `error-cli-sub` subscription to avoid interupting `janitor`):
```
gcloud pubsub subscriptions pull error-cli-sub --auto-ack
```

### TODO

- add topic output from payments to message success
- add status field to message
- write browser frontend that can also consume the success and failure messages