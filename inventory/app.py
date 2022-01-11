import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from google.cloud import pubsub_v1
import os
import datetime
import json
from dotenv import load_dotenv

# load envvars
load_dotenv()

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': os.environ.get('PROJECT_ID'),
})

# connect to Firestore
db = firestore.client()

def receive_messages(
    project_id: str, subscription_id: str, timeout: float = None) -> None:
    """Receives messages from a pull subscription."""
    # [START pubsub_subscriber_async_pull]
    # [START pubsub_quickstart_subscriber]
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1

    # TODO(developer)
    # project_id = "your-project-id"
    # subscription_id = "your-subscription-id"
    # Number of seconds the subscriber should listen for messages
    # timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.\n")
        msg = json.loads(message.data.decode("utf-8"))

        # prep pubsub
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(os.environ.get('PROJECT_ID'), os.environ.get('TOPIC_INVENTORY_UPDATED'))
        error_topic_path = publisher.topic_path(os.environ.get('PROJECT_ID'), os.environ.get('TOPIC_ERROR'))

        # update inventory & create orders record
        item_ref = db.collection(os.environ.get('COLLECTION_INVENTORY')).document(msg['item'])
        # first check if item exists
        item = item_ref.get()
        if item.exists:
            print(f"Item {msg['item']} exists. Continuing.")
            order_ref = item_ref.collection(os.environ.get('COLLECTION_ORDERS')).document(msg['uuid'])
            #check for existing document with same uuid
            order = order_ref.get()
            if not order.exists:
                # check & update quantity
                if item.to_dict()['quantity'] >= msg['quantity']:
                    item_ref.update({u'quantity': (item.to_dict()['quantity'] - msg['quantity'])})
                    print(f"Quantity for {msg['item']} updated.")
                    # write to orders subcollection
                    print(f"Writing to document {msg['uuid']} in inventory subcollection {os.environ.get('COLLECTION_ORDERS')}.")
                    order_ref.set({
                        'item': msg['item'],
                        'quantity': msg['quantity'],
                        'user': msg['user'],
                        'local_created': datetime.datetime.now(),
                        'price_per_unit': item.to_dict()['price_per_unit']
                    })
                    # publish to inventory-updated topic
                    msg['price_per_unit'] = item.to_dict()['price_per_unit']
                    data = json.dumps(msg).encode("UTF-8")
                    print(f"Publishing message to {topic_path}:\n{json.dumps(msg)}")
                    future = publisher.publish(topic_path, data)
                    print(future.result())
                else:
                    msg['status'] = f"Insufficient inventory for {msg['item']} to fulfill order {msg['uuid']}. Issuing error message to {error_topic_path}"
                    print(msg['status'])
                    data = json.dumps(msg).encode("UTF-8")
                    future = publisher.publish(error_topic_path, data)
                    print(future.result())                    
            else:
                print(f"Document {msg['uuid']} already exists. Ignoring.")

        else: 
            msg['status'] = f"Item {msg['item']} does not exist. Issuing error message to {error_topic_path}"
            print(msg['status'])
            data = json.dumps(msg).encode("UTF-8")
            future = publisher.publish(error_topic_path, data)
            print(future.result())

        # confirm message
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.
    # [END pubsub_subscriber_async_pull]
    # [END pubsub_quickstart_subscriber]


if __name__ == '__main__':

    receive_messages(os.environ.get('PROJECT_ID'), os.environ.get('SUBSCRIPTION_ORDER_CREATED'), None)