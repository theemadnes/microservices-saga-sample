import json
import uuid
import os
from dotenv import load_dotenv
from google.cloud import pubsub_v1
from flask import Flask, request, Response, jsonify

load_dotenv()
app = Flask(__name__)
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(os.environ.get('PROJECT_ID'), os.environ.get('TOPIC_FRONTEND'))


@app.route('/')
def index():
    return 'Index Page\n'

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        # TODO: lightweight validation of user existence here
        # add UUID to request JSON
        request.json['uuid'] = str(uuid.uuid4())
        data = json.dumps(request.json).encode("UTF-8")
        print("Publishing " + json.dumps(request.json))
        future = publisher.publish(topic_path, data)
        #return 'called POST\n'
        print(future.result())
        return f"Published messages to {topic_path}." + "\n"
    else:
        return 'called GET\n'

if __name__ == '__main__':

    app.run(
            host='0.0.0.0', port=int(os.environ.get('PORT', 8080)),
            threaded=True)