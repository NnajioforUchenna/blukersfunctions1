from google.cloud.firestore_v1 import FieldFilter
from html import escape
from google.cloud import translate_v2 as translate
from services.dbServices.firebase_services import db
import os
from html import unescape
from xml.etree import ElementTree as ET
from pathlib import Path


def getJobPostsById(job_id):
    job_posts_ref = db.collection('jobPosts')

    # Query for documents where jobId is in the jobIds list
    query_ref = job_posts_ref.where(filter=FieldFilter('jobIds', 'array_contains', job_id))

    # Execute the query
    job_posts = query_ref.stream()

    # Collect the results into a list
    result = []
    for job_post in job_posts:
        result.append(job_post.to_dict())

    return result


def convertJobPostsToDocument(jobPosts):
    html = "<JobPosts>"

    for jobPost in jobPosts:
        html += "<JobPost>"

        html += f"<jobTitle>{escape(jobPost.get('jobTitle', ''))}</jobTitle>"
        html += f"<jobDescription>{escape(jobPost.get('jobDescription', ''))}</jobDescription>"
        html += f"<requirements>{escape(jobPost.get('requirements', ''))}</requirements>"

        # Check if 'skills' key exists and is a list, else default to an empty list
        skills = jobPost.get('skills', [])
        html += f"<skills>{', '.join(escape(skill) for skill in skills)}</skills>"

        html += "</JobPost>"

    html += "</JobPosts>"
    return html


def translateDocument(document, target_language):
    # Define the path to the key file
    key_file_path = Path('../../serviceKey2.json')

    # Set the environment variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(key_file_path)

    # Instantiate a client
    translate_client = translate.Client()

    # Translate the HTML document
    translation = translate_client.translate(
        document,
        target_language=target_language,
        format_='html'  # Specify the input format as HTML
    )

    return translation['translatedText']


def convertDocumentToJobPosts(document):
    jobPosts = []

    try:
        # Parse the HTML string as an XML document
        root = ET.fromstring(document)
    except ET.ParseError as e:
        print(f"Error parsing document: {e}")
        return jobPosts

    # Iterate through the "JobPost" elements
    for jobPost in root.findall('JobPost'):
        try:
            # Extract the properties of each job post
            jobTitle = unescape(jobPost.find('jobTitle').text or "")
            jobDescription = unescape(jobPost.find('jobDescription').text or "")
            requirements = unescape(jobPost.find('requirements').text or "")
            skills_text = jobPost.find('skills').text or ""
            skills = [unescape(skill) for skill in skills_text.split(', ')]

            # Create a dictionary representing the job post and append it to the list
            jobPosts.append({
                'jobTitle': jobTitle,
                'jobDescription': jobDescription,
                'requirements': requirements,
                'skills': skills,
            })
        except AttributeError as e:
            print(f"Error processing job post: {e}. Skipping this entry.")

    return jobPosts


def refillTranslatedParameters(jobPosts, translated_jobPosts):
    # Check if the lengths of the two lists are not equal
    if len(jobPosts) != len(translated_jobPosts):
        print("Lengths of jobPosts and translated_jobPosts are not equal. Aborting operation.")
        return

    # Create a copy of the original jobPosts list to modify
    modified_jobPosts = jobPosts.copy()

    # Iterate through the original and translated lists together using zip
    for original, translated in zip(modified_jobPosts, translated_jobPosts):
        # Replace the specified parameters in the original job post with the values from the translated job post
        original['jobTitle'] = translated['jobTitle']
        original['jobDescription'] = translated['jobDescription']
        original['skills'] = translated['skills']
        original['requirements'] = translated['requirements']

    return modified_jobPosts


def getJobPostsByIdAndTargetLanguage(jobId, targetLanguage):
    # Step 1: Get job posts by ID
    jobPosts = getJobPostsById(jobId)

    # Step 2: Convert job posts to HTML document
    document = convertJobPostsToDocument(jobPosts)

    # Step 3: Translate the document to the target language
    translated_document = translateDocument(document, targetLanguage)

    # Step 4: Convert the translated document back to job posts
    translated_jobPosts = convertDocumentToJobPosts(translated_document)

    # Step 5: Refill the translated parameters
    final_jobPosts = refillTranslatedParameters(jobPosts, translated_jobPosts)

    return final_jobPosts


def separateJobPosts(job_posts, target_language):
    alreadyTranslatedJobPosts = []
    toBeTranslatedJobPosts = []
    for job_post in job_posts:
        print(job_post)
        documentId = job_post['jobPostId'] + '_' + target_language
        translatedJobPost = db.collection('TranslatedJobPosts').document(documentId).get().to_dict()
        if translatedJobPost is None:
            toBeTranslatedJobPosts.append(job_post)
        else:
            alreadyTranslatedJobPosts.append(translatedJobPost)

    return alreadyTranslatedJobPosts, toBeTranslatedJobPosts


def saveJobPost2Translated(documentId, JobPost):
    try:
        doc_ref = db.collection(u'TranslatedJobPosts').document(documentId)
        doc_ref.set(JobPost)
        print(f"Job Post {documentId} saved to translated")
    except Exception as e:
        print(f"Error: {e}")


def saveTranslatedJobPosts(final_jobPosts, target_language):
    for jobPosts in final_jobPosts:
        documentId = jobPosts['jobPostId'] + '_' + target_language
        saveJobPost2Translated(documentId, jobPosts)


def translateJobPosts(job_posts, target_language):
    # final job posts
    final_jobPosts = []
    # Check for already translated job posts
    alreadyTranslatedJobPosts, toBeTranslatedJobPosts = separateJobPosts(job_posts, target_language)

    # Step 2: Convert job posts to HTML document
    if len(toBeTranslatedJobPosts) > 0:
        document = convertJobPostsToDocument(toBeTranslatedJobPosts)

        # Step 3: Translate the document to the target language
        translated_document = translateDocument(document, target_language)

        # Step 4: Convert the translated document back to job posts
        translated_jobPosts = convertDocumentToJobPosts(translated_document)

        # Step 5: Refill the translated parameters
        final_jobPosts = refillTranslatedParameters(toBeTranslatedJobPosts, translated_jobPosts)

        # Save the translated job posts to firestore
        saveTranslatedJobPosts(final_jobPosts, target_language)

    # Merge already translated job posts with the new ones
    final_jobPosts = final_jobPosts + alreadyTranslatedJobPosts

    return final_jobPosts