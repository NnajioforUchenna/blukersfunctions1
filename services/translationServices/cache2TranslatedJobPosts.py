from services.dbServices.firebase_services import *
import time
from services.translationServices.languages import languages


# Getting all Jobs from Firebase
jobs_collection = db.collection('cache')
cache = jobs_collection.get()

print(f"Total Jobs: {len(cache)}")


def saveJobPost2Translated(documentId, JobPost):
    try:
        doc_ref = db.collection(u'TranslatedJobPosts').document(documentId)
        doc_ref.set(JobPost)
        print(f"Job Post {documentId} saved to translated")
    except Exception as e:
        print(f"Error: {e}")


count = 0
for jobPost in cache:

    # get the last 2 chars of the jobPostId id
    last_2_chars = jobPost.id[-2:]

    if last_2_chars != 'en' and last_2_chars in languages:
        print(f"Job Post: {jobPost.id}")
        JobPosts = jobPost.to_dict()['jobPosts']
        if JobPosts:
            for JobPost in JobPosts:
                documentId = JobPost['jobPostId'] + "_" + last_2_chars
                print(f"Document Id: {documentId}")
                # saveJobPost2Translated(documentId, JobPost)
                count += 1
        print('_____________________________')
        print('')

print(f"Total Job Posts: {count}")
collection = db.collection('TranslatedJobPosts')
translated = collection.get()

print(f"Total Jobs: {len(translated)}")





