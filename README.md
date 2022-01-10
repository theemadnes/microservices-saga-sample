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