topics = frontend order-created inventory-updated error payment-created
subfolders = data-initialization-script frontend inventory janitor orders payments

create-topics:
	for TOPIC in $(topics);															\
	do																				\
		gcloud pubsub topics create $$TOPIC --project $$PROJECT_ID;					\
	done;

create-subscriptions:
	for TOPIC in $(topics);																					\
	do																										\
		gcloud pubsub subscriptions create $$TOPIC-sub --topic=$$TOPIC --project $$PROJECT_ID;				\
	done;
