import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from dotenv import load_dotenv

# load envvars
load_dotenv()

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': os.environ.get('PROJECT_ID'),
})

db = firestore.client()

# delete users & their orders
users_ref = db.collection(os.environ.get('COLLECTION_USERS'))
users = users_ref.limit(1000).stream()
deleted = 0
for user in users:
    orders_ref = user.reference.collection(os.environ.get('COLLECTION_ORDERS'))
    orders = orders_ref.limit(1000).stream()
    for order in orders:
        print(f'Deleting order {order.id} => {order.to_dict()} from user {user.id}')
        order.reference.delete()

    print(f'Deleting user {user.id} => {user.to_dict()}')
    user.reference.delete()
    deleted = deleted + 1

# delete inventory
coll_ref = db.collection(os.environ.get('COLLECTION_INVENTORY'))
docs = coll_ref.limit(1000).stream()
deleted = 0
for doc in docs:
    print(f'Deleting doc {doc.id} => {doc.to_dict()}')
    doc.reference.delete()
    deleted = deleted + 1

# set user data w/ orders
doc_ref = db.collection(os.environ.get('COLLECTION_USERS')).document(u'jack')
doc_ref.set({
    u'address': "123 fake street"
})
doc_ref = doc_ref.collection(os.environ.get('COLLECTION_ORDERS')).document(u'00000000-3321-4927-bac1-2750a1d16017')
doc_ref.set({
    u'item': 'widget',
    u'quantity': 50,
    u'note': 'dummy order'
})
doc_ref = db.collection(os.environ.get('COLLECTION_USERS')).document(u'jill')
doc_ref.set({
    u'address': "456 other street"
})
doc_ref = doc_ref.collection(os.environ.get('COLLECTION_ORDERS')).document(u'00000000-4f1c-401d-bc8a-701d3c1e9603')
doc_ref.set({
    u'item': 'wotsit',
    u'quantity': 60,
    u'note': 'dummy order'
})

# set inventory data
doc_ref = db.collection(os.environ.get('COLLECTION_INVENTORY')).document(u'widget')
doc_ref.set({
    u'quantity': 10000
})
doc_ref = db.collection(os.environ.get('COLLECTION_INVENTORY')).document(u'wotsit')
doc_ref.set({
    u'quantity': 20000
})