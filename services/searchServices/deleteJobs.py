import pprint

from google.cloud import talent_v4beta1
from google.oauth2 import service_account

from google.cloud import talent

credentials = service_account.Credentials.from_service_account_file('../serviceKey2.json')
job_client = talent_v4beta1.JobServiceClient(credentials=credentials)
company_client = talent_v4beta1.CompanyServiceClient(credentials=credentials)
project_id = "top-design-395510"


def list_tenants(project_id):
    """List Tenants"""

    client = talent.TenantServiceClient(credentials=credentials)

    # project_id = 'Your Google Cloud Project ID'

    if isinstance(project_id, bytes):
        project_id = project_id.decode("utf-8")
    parent = f"projects/{project_id}"

    # Iterate over all results
    for response_item in client.list_tenants(parent=parent):
        print(f"Tenant Name: {response_item.name}")
        print(f"External ID: {response_item.external_id}")


# def deleteAllJobs():
#     parent = f"projects/{project_id}"
#     companies = list(company_client.list_companies(parent=parent))
#     print(companies)
#
#     for company in companies:
#         jobs = list(job_client.list_jobs(parent=parent, filter=f'companyName="{company.name}"'))
#         for job in jobs:
#             try:
#                 job_client.delete_job(name=job.name)
#                 print(f"Deleted job: {job.name}")
#             except Exception as e:
#                 print(f"Error deleting job {job.name}: {e}")
#         company_client.delete_company(name=company.name)



