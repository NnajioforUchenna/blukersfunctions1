from flask import Blueprint, request, jsonify
from flask_cors import CORS

from services.searchServices.aiGetJobPosts import aiGetJobPosts
from services.searchServices.blukersCacheFirestore import getSearchFromCacheFirestore, saveSearch2CacheFirestore
from services.translationServices.translateJobPosts import translateJobPosts
from services.translationServices.languages import languages


sa = Blueprint('sa', __name__, template_folder='templates')
CORS(sa)


@sa.route('/get-job-posts', methods=['POST'])
def get_job_posts():
    data = request.json
    query_name = data.get('query_name',"")
    query_location = data.get('query_location',"")
    # query_location  = query_location + ",Texas"
    page_number = data.get('page_number', 0)
    target_language = data.get('target_language', 'en')

    # Checking firestore cache for job posts
    queryParameter = (query_name + "_" + query_location + "_" + str(page_number) + "_" + target_language).strip().lower().replace(" ", "%20")
    jobPosts = getSearchFromCacheFirestore(queryParameter)

    if jobPosts:
        return jsonify(jobPosts)

    # Call aiGetJobPosts and assign result to jobPosts
    jobPosts = aiGetJobPosts(query_name, query_location, page_number)

    # Check if the target language is English
    if target_language == 'en' or target_language not in languages:
        saveSearch2CacheFirestore(queryParameter, jobPosts)
        return jsonify(jobPosts)
    else:
        translated_job_posts = translateJobPosts(jobPosts, target_language)
        saveSearch2CacheFirestore(queryParameter, translated_job_posts)
        return jsonify(translated_job_posts)
