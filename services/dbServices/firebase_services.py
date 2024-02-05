import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
service_key_path = os.path.join(current_directory, 'serviceKey.json')

cred = credentials.Certificate(service_key_path)

# cred = credentials.Certificate('serviceKey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'blukers-development.appspot.com'
})

db = firestore.client()
