from .firebase_services import db


def getJobPostsById(collectionName, document_ids):
    """
    Fetches documents from the 'jobPosts' collection in Firestore using a list of document IDs.

    Parameters:
    - document_ids (list): A list of document IDs.

    Returns:
    - list: A list of documents (dictionaries) from Firestore.
    """
    # Reference to the 'jobPosts' collection
    job_posts_collection = db.collection(collectionName)

    # Fetch the documents
    documents = []
    for doc_id in document_ids:
        doc_ref = job_posts_collection.document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            documents.append(doc.to_dict())
        else:
            print(f"No document found for ID: {doc_id}")

    return documents
