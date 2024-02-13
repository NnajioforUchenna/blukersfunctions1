from flask import Flask, request, jsonify
from flask_cors import CORS
from services.searchServices.searchWorkers import *
from services.searchServices.searchJobPosts import *
from services.translationServices.translateJobPosts import *

from paymentsApi import pa
from searchApi import sa

app = Flask(__name__)
app.register_blueprint(pa, url_prefix='/payments')
app.register_blueprint(sa, url_prefix='/search')
CORS(app)


@app.get('/')
def hello():
    return 'This is Bulkers API Functions'



@app.post('/searchWorkers')
def searchWorkers():
    body = request.get_json()
    nameRelated = body.get('nameRelated', '').strip().lower()
    locationRelated = body.get('locationRelated', '').strip().lower()

    # Call the searchWorkersByParameter function and get the results
    matched_workers = searchWorkersByParameter(nameRelated, locationRelated)

    # You can format the result as you like, here we are simply returning the matched workers as JSON
    return jsonify(matched_workers)


@app.post('/searchJobPosts')
def searchJobPosts():
    body = request.get_json()
    nameRelated = body.get('nameRelated', '').strip().lower()
    locationRelated = body.get('locationRelated', '').strip().lower()

    # Call the searchJobPostsByParameter function and get the results
    matched_jobposts = searchJobPostsByParameter(nameRelated, locationRelated)

    # You can format the result as you like, here we are simply returning the matched job posts as JSON
    return jsonify(matched_jobposts)


@app.post('/getJobPostsByIdAndTargetLanguage')
def get_job_posts_by_id_and_target_language():
    try:
        # Extract jobId and targetLanguage from the request
        job_id = request.json.get('jobId')
        target_language = request.json.get('targetLanguage')

        # Check if the necessary parameters are provided
        if job_id is None or target_language is None:
            return jsonify({'error': 'jobId and targetLanguage must be provided'}), 400

        # Call the function and get the result
        translated_job_posts = getJobPostsByIdAndTargetLanguage(job_id, target_language)

        # Return the translated job posts as a JSON response
        return jsonify(translated_job_posts), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    app.run(debug=True)