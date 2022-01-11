import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from dotenv import load_dotenv
import datetime

# load envvars
load_dotenv()

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': os.environ.get('PROJECT_ID'),
})

db = firestore.client()

# delete payments
payments_ref = db.collection(os.environ.get('COLLECTION_PAYMENTS'))
payments = payments_ref.limit(1000).stream()
deleted = 0
for payment in payments:
    print(f'Deleting payment {payment.id} => {payment.to_dict()}')
    payment.reference.delete()
    deleted = deleted + 1

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

# delete inventory & associated orders
inventory_ref = db.collection(os.environ.get('COLLECTION_INVENTORY'))
items = inventory_ref.limit(1000).stream()
deleted = 0
for item in items:
    orders_ref = item.reference.collection(os.environ.get('COLLECTION_ORDERS'))
    orders = orders_ref.limit(1000).stream()
    for order in orders:
        print(f'Deleting order {order.id} => {order.to_dict()} for item {item.id}')
        order.reference.delete()

    print(f'Deleting item {item.id} => {item.to_dict()}')
    item.reference.delete()
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
    u'note': 'dummy order',
    u'local_created': datetime.datetime.now()
})
doc_ref = db.collection(os.environ.get('COLLECTION_USERS')).document(u'jill')
doc_ref.set({
    u'address': "456 other street"
})
doc_ref = doc_ref.collection(os.environ.get('COLLECTION_ORDERS')).document(u'00000000-4f1c-401d-bc8a-701d3c1e9603')
doc_ref.set({
    u'item': 'wotsit',
    u'quantity': 60,
    u'note': 'dummy order',
    u'local_created': datetime.datetime.now()
})

# set inventory data
doc_ref = db.collection(os.environ.get('COLLECTION_INVENTORY')).document(u'widget')
doc_ref.set({
    u'quantity': 10000,
    u'price_per_unit': 10
})
doc_ref = db.collection(os.environ.get('COLLECTION_INVENTORY')).document(u'wotsit')
doc_ref.set({
    u'quantity': 20000,
    u'price_per_unit': 15
})