import pprint
import time
import random
import traceback

from google.api_core.exceptions import AlreadyExists
from google.cloud import talent_v4beta1
from google.oauth2 import service_account
from services.dbServices.firebase_services import *
from services.helperFunctions import remove_special_characters, hash_dict
from services.searchServices.persistRecords import is_record_written, write_record

credentials = service_account.Credentials.from_service_account_file('../../serviceKey2.json')
job_client = talent_v4beta1.JobServiceClient(credentials=credentials)
company_client = talent_v4beta1.CompanyServiceClient(credentials=credentials)
project_id = "blukerserver"
tenant_id = "Blukers-Jobs"  # Replace with your Tenant ID if using tenancy, otherwise, you might not need this line

# Getting all Created Companies to Avoid Duplicates
parent = f"projects/{project_id}"


def getAllCompanies(projectID):
    companies_dict = {}
    projParent = f"projects/{projectID}"
    companies = list(company_client.list_companies(parent=projParent))
    for company in companies:
        companies_dict[company.external_id] = company.name
    return companies_dict


def create_custom_attribute(values):
    custom_attribute = talent_v4beta1.CustomAttribute()
    custom_attribute.filterable = True

    if isinstance(values, str):
        values = remove_special_characters(values)
        custom_attribute.string_values.append(values)
    elif isinstance(values, (int, float)):
        custom_attribute.long_values.append(values)
    elif isinstance(values, list):
        for value in values:
            if isinstance(value, str):
                value = remove_special_characters(value)
                custom_attribute.string_values.append(value)
            elif isinstance(value, (int, float)):
                custom_attribute.long_values.append(value)
            else:
                print(f"Unsupported value type {type(value)} in list. Only strings and numbers are allowed.")
    else:
        print(f"Unsupported type {type(values)}. Only strings, numbers, and lists are allowed.")
    return custom_attribute


def create_company_if_not_exists(display_name):
    external_id = remove_special_characters(display_name).replace(" ", "").lower()

    # If company doesn't exist, create it
    company = {
        "display_name": display_name,
        "external_id": external_id
    }

    try:
        response = company_client.create_company(parent=parent, company=company)
        return response.name
    except Exception as e:
        # print(f"Error: {e}")
        name = f"projects/{project_id}/jobs/{external_id}"
        response = job_client.get_job(name=name)
        print(f"Company already exists: {response.company}")
        return response.company


def format_address(address_dict):
    city = address_dict.get('city', '').strip()
    state = address_dict.get('state', '').strip()
    country = address_dict.get('country', '')

    return f"{city}, {state}, {country}"


def uploadJobPost2CloudTalentSolution(job_data):
    collection_priority_value = 1

    custom_attrs = {
        'jobPostId': create_custom_attribute(job_data['jobPostId']),
        'collection_priority': create_custom_attribute(collection_priority_value),
    }

    title = remove_special_characters(job_data['jobTitle'])
    requisition_id = remove_special_characters(job_data['jobPostId'])
    description = remove_special_characters(job_data['jobDescription'])
    company_name = job_data['companyName']
    addresses = [format_address(job_data['address'])] # for ScrappedTexas Jobs Add [0]

    # Get Company Name
    external_id = remove_special_characters(company_name).replace(" ", "").lower()
    if external_id in companyDict:
        company_id = companyDict[external_id]
    else:
        company_id = create_company_if_not_exists(company_name)
        companyDict[external_id] = company_id

    talent_job = talent_v4beta1.Job(
        company=company_id,
        title=title,
        description=description,
        requisition_id=requisition_id,
        custom_attributes=custom_attrs,
        language_code="en-us",
        addresses=addresses
    )

    try:
        job_client.create_job(parent=f"projects/{project_id}", job=talent_job)
    except AlreadyExists as e:
        print(f"Job with requisition ID {requisition_id} already exists. Skipping.")


def get_date():
    # Get the current date and time
    now = time.time_ns() // 1_000_000

    # Generate a random number of seconds, not more than 24 hours
    random_seconds = random.randint(0, 84600)

    # Calculate the new date and time by adding the random number of seconds to now
    random_date = now - random_seconds

    return random_date

# Getting all Jobs from Firebase
jobs_collection = db.collection('ScrappedJobs')
jobs = jobs_collection.get()

print(f"Total jobs: {len(jobs)}")

count = 0
companyDict = getAllCompanies(project_id)
for job in jobs:
    job_data = job.to_dict()
    job_data['dateCreated'] = get_date()
    count += 1
    hashKey = hash_dict(job_data)
    if not is_record_written(hashKey):
        try:
            uploadJobPost2CloudTalentSolution(job_data)
            print(f"Uploaded job {count}. {job_data['jobPostId']}")
            write_record(hashKey)
        except Exception as e:
            print(f"Error uploading job {count}. {job_data['jobPostId']}. Skipping.")
            # Optionally, print the type of exception for clarity
            print(f"Exception type: {type(e).__name__}")

    else:
        print(f"Record {count} already written")