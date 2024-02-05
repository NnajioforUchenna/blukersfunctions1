import pprint

import google.cloud.talent_v4beta1 as talent
from google.oauth2 import service_account
from services.dbServices.getDocumentsByIds import getJobPostsById
import time
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
service_key_path = os.path.join(current_directory, 'serviceKey2.json')

credentials = service_account.Credentials.from_service_account_file(service_key_path)
projectID = "top-design-395510"


def search_jobs(query_name, query_location, page_token=None):
    # Building JobQuery Based on the parameters given
    job_query = talent.JobQuery()

    if query_name and not query_location:
        job_query.query = query_name

    if query_location and not query_name:
        job_query.query = query_location

    if query_name and query_location:
        job_query.query = query_name
        job_query.location_filters = [
            talent.LocationFilter(
                address=query_location,
                distance_in_miles=50.0  # You can adjust this as per your requirement
            )
        ]

    client = talent.JobServiceClient(credentials=credentials)
    parent = f"projects/{projectID}"

    request_metadata = {
        "domain": "www.example.com",
        "session_id": "Hashed session identifier",
        "user_id": "Hashed user identifier"
    }

    # Set up Custom Ranking
    custom_ranking_info = talent.SearchJobsRequest.CustomRankingInfo(
        importance_level=talent.SearchJobsRequest.CustomRankingInfo.ImportanceLevel.EXTREME,
        ranking_expression="collection_priority"
    )

    request = talent.SearchJobsRequest(
        parent=parent,
        request_metadata=request_metadata,
        job_query=job_query,
        custom_ranking_info=custom_ranking_info,
        order_by="custom_ranking desc"

    )

    # Add page_token to the request if it's present
    if page_token:
        request.page_token = page_token

    results = []
    response = client.search_jobs(request=request)

    for response_item in response.matching_jobs:
        job = response_item.job
        job_post_id = None
        # Extracting jobPostId
        for key, value in job.custom_attributes.items():
            if key == "jobPostId":
                job_post_id = value.string_values[0]
                break
        if job_post_id:
            results.append(job_post_id)
    # print_job_details(job)
    # print(response.total_size)
    return results, response.next_page_token


def search_all_jobs(query_name, query_location):
    all_results = []
    page_token = None

    while True:
        results, next_page_token = search_jobs(query_name, query_location, page_token)
        all_results.extend(results)

        # Check if there's a next page. If not, break out of the loop.
        if not next_page_token:
            break

        # if len(all_results) > 500 break
        if len(all_results) > 500:
            break

        page_token = next_page_token

    return all_results
