import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('cockatoos-5a170-firebase-adminsdk-ty1da-3f70ecdad4.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def write_article_to_db(title, document, indexes):
    doc_ref = db.collection(u'articles').document(title)
    doc_ref.set({
        u'article': document,
        u'indexes': indexes
    })

if __name__ == '__main__':
    doc_ref = db.collection(u'articles').document()
    doc_ref.set({
        u'first': u'qq',
        u'last': [0, 3, 5, 6]
    })