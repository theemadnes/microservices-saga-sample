topics = frontend order-created inventory-updated error payment-created
subfolders = data-initialization-script frontend inventory janitor orders payments

define NEWLINE

endef

create-topics:
	-for TOPIC in $(topics);															\
	do																				\
		gcloud pubsub topics create $$TOPIC --project $$PROJECT_ID;					\
	done;

create-subscriptions:
	-for TOPIC in $(topics);																					\
	do																										\
		gcloud pubsub subscriptions create $$TOPIC-sub --topic=$$TOPIC --project $$PROJECT_ID;				\
	done;

generate-dotenv-files:
	- for SUBFOLDER in $(subfolders); \
	do \
		echo PROJECT_ID=$$PROJECT_ID$(NEWLINE) > $$SUBFOLDER/.env;\
		echo PORT=8080$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo TOPIC_ERROR=error$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo TOPIC_FRONTEND=frontend$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo TOPIC_INVENTORY_UPDATED=inventory-updated$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo TOPIC_ORDER_CREATED=order-created$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo TOPIC_PAYMENT_CREATED=payment-created$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo COLLECTION_INVENTORY=inventory$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo COLLECTION_ORDERS=orders$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo COLLECTION_PAYMENTS=payments$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo COLLECTION_USERS=users$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo SUBSCRIPTION_ERROR=error-sub$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo SUBSCRIPTION_FRONTEND=frontend-sub$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo SUBSCRIPTION_INVENTORY_UPDATED=inventory-updated-sub$(NEWLINE) >> $$SUBFOLDER/.env;\
		echo SUBSCRIPTION_ORDER_CREATED=order-created-sub >> $$SUBFOLDER/.env;\
	done;