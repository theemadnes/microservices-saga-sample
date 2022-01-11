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
        error_topic_path = publisher.topic_path(os.environ.get('PROJECT_ID'), os.environ.get('TOPIC_ERROR'))
        data = json.dumps(msg).encode("UTF-8")
        
        # create payment document
        payment_ref = db.collection(os.environ.get('COLLECTION_PAYMENTS')).document(msg['uuid'])
        # first check if payment exists
        payment = payment_ref.get()
        if payment.exists:
            print(f"Document {msg['uuid']} already exists. Ignoring.")
        # check to see if error condition
        elif 'payment-error' in msg.keys():
            print(f"Payment error detected for order {msg['uuid']}. Issuing error message to {error_topic_path}")
            future = publisher.publish(error_topic_path, data)
            print(future.result())
        # looks good, so write payment doc to payments collection
        else:
            print(f"Writing to document {msg['uuid']} in collection {os.environ.get('COLLECTION_PAYMENTS')}.")
            payment_ref.set({
                'item': msg['item'],
                'quantity': msg['quantity'],
                'user': msg['user'],
                'local_created': datetime.datetime.now()
            })

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

    receive_messages(os.environ.get('PROJECT_ID'), os.environ.get('SUBSCRIPTION_INVENTORY_UPDATED'), None)