from services.dbServices.firebase_services import db

cache_collection = db.collection('cache')


def saveSearch2CacheFirestore(queryParameter, jobPosts):
    """
    Saves a list of job posts to Firestore using the query parameter as the document ID.

    Parameters:
    - queryParameter (str): The query parameter used to fetch the job posts.
    - jobPosts (list): A list of job posts (dictionaries) to save to Firestore.

    Returns:
    - None
    """
    try:
        # Save the list of job posts to Firestore using the query parameter as the document ID
        cache_collection.document(queryParameter).set({'jobPosts': jobPosts})
    except Exception as e:
        print(f"Error saving data to cache: {e}")


def getSearchFromCacheFirestore(queryParameter):
    """
    Fetches a list of job posts from Firestore using the query parameter as the document ID.

    Parameters:
    - queryParameter (str): The query parameter used to fetch the job posts.

    Returns:
    - list: A list of job posts (dictionaries) from Firestore.
    """
    try:
        # Fetch the document from Firestore using the query parameter as the document ID
        doc = cache_collection.document(queryParameter).get()

        # If the document was found, return the list of job posts
        if doc.exists:
            return doc.to_dict()['jobPosts']
    except Exception as e:
        print(f"Error fetching data from cache: {e}")

    # Return an empty list if the document wasn't found or if there was an error
    return []
