# microservices-saga-sample
Naive attempt at using multiple microservices that implement the saga pattern with idempotency.

Rought flow:

person => POST JSON to frontend svc =>
`frontend` svc publishes JSON to pubsub (and tags JSON with UUID) =>
consumed by `order` svc & order created and publish to pubsub when complete =>
consumed by `inventory` svc & inventory updated and publish to pubsub when complete (error if insufficient inventory and publish to error topic) =>
consumed by `payments` svc & payment "invoice" record created (error if initial JSON contains some field to indicate insufficient funds to simulate failure, and publish to error topic)

`tx-compensator` is a super naive transaction compensator service that listens to error topic and takes compensating actions against `orders`, `inventory` & `payments` to remove stale records. records are stored in either Firestore collections and subcollections, and (with the exception of the `users` collection) are keyed on a UUID assigned by the frontend service, and records in those various collections will get purged during compensation. the UUID also allows for idempotency, as replayed messages will be ignored if an existing record with the same UUID exists.

### setup

create `frontend` topic

```
gcloud pubsub topics create frontend
```

create `frontend-sub` subscription

```
gcloud pubsub subscriptions create frontend-sub --topic=frontend
```

create `order-created` topic

```
gcloud pubsub topics create order-created
```

create `order-created-sub` subscription

```
gcloud pubsub subscriptions create order-created-sub --topic=order-created
```


Using this stuff:
# test POST via curl
curl -X POST http://127.0.0.1:8080/order \
   -H 'Content-Type: application/json' \
   -d '{"item":"widget","quantity":"50","user":"jack"}'

curl -X POST http://127.0.0.1:8080/order \
   -H 'Content-Type: application/json' \
   -d '{"item":"wotsit","quantity":"80","user":"jill"}'

# create sub & output messages
gcloud pubsub subscriptions pull frontend-sub --auto-ack