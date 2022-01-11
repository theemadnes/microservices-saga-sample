create-topics:
	for TOPIC in frontend order-created inventory-updated error payment-created;	\
	do																				\
		gcloud pubsub topics create $$TOPIC --project $$PROJECT_ID;					\
	done;

create-subscriptions:
	gcloud pubsub subscriptions create frontend-sub --topic=frontend --project $$PROJECT_ID; \
	gcloud pubsub subscriptions create order-created-sub --topic=order-created --project $$PROJECT_ID; \
	gcloud pubsub subscriptions create inventory-updated-sub --topic=inventory-updated --project $$PROJECT_ID; \
	gcloud pubsub subscriptions create error-sub --topic=error --project $$PROJECT_ID; \
	gcloud pubsub subscriptions create error-cli-sub --topic=error --project $$PROJECT_ID; \
	gcloud pubsub subscriptions create payment-created-sub --topic=payment-created --project $$PROJECT_ID