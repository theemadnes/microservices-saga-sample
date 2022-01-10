# microservices-saga-sample
Naive attempt at using multiple microservices that implement the saga pattern with idempotency.

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



Using this stuff:
# test POST via curl
curl -X POST http://127.0.0.1:8080/order \
   -H 'Content-Type: application/json' \
   -d '{"item":"widget","quantity":"50","user":"jack"}'

curl -X POST http://127.0.0.1:8080/order \
   -H 'Content-Type: application/json' \
   -d '{"item":"wotsit","quantity":"80","user":"jill"}'

# create sub & output messages
gcloud pubsub subscriptions create frontend-sub --topic=frontend
gcloud pubsub subscriptions pull frontend-sub --auto-ack