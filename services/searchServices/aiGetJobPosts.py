from services.searchServices.blukersCacheFirestore import getSearchFromCacheFirestore, saveSearch2CacheFirestore
from services.searchServices.blukersCacheRedis import getSearchFromCache, saveSearch2Cache
from services.dbServices.getDocumentsByIds import getJobPostsById
from services.searchServices.searchCloudTalentSolutionJobs import search_jobs, search_all_jobs
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(2)


def get_jobs_by_page(jobPosts, pageNumber, items_per_page=10):
    start_index = pageNumber * items_per_page
    end_index = start_index + items_per_page
    return jobPosts[start_index:end_index]


def aiGetJobPosts(query_name, query_location, page_number):
    # step 1: get keywords from query_name and query_location
    keyword = (query_name + "_" + query_location).strip().lower().replace(" ", "%20")

    # step 2: Check Whether the key Word exist in redis MemoryStore
    jobPosts = getSearchFromCacheFirestore(keyword)

    # step 3: if the key word exist in redis MemoryStore, return the result
    if jobPosts:
        jobPostsIds = get_jobs_by_page(jobPosts, page_number)
        JobPostsDetails = getJobPostsById("ScrappedJobs", jobPostsIds)
        print("got job posts from firestore")
        return JobPostsDetails
    else:
        # query Cloud Talent Solution api
        result = search_jobs(query_name, query_location)
        jobPostsIds, nextPage = result[0], result[1]
        # step 4: if the key word does not exist, call Cloud Talent Solution api and store the result in redis
        # MemoryStore asynchronously
        executor.submit(queryCTSandStoreInMemoryStore, query_name, query_location)
        # asyncio.create_task(queryCTSandStoreInMemoryStore(query_name, query_location))

        #return first set of jobPosts to User
        JobPostsDetails = getJobPostsById("ScrappedJobs", jobPostsIds)
        print("got job posts from Cloud Talent Solution")
        return JobPostsDetails


def queryCTSandStoreInMemoryStore(query_name, query_location):
    allJobPostsByParamter = search_all_jobs(query_name, query_location)
    keyword = (query_name + "_" + query_location).strip().lower().replace(" ", "%20")
    saveSearch2CacheFirestore(keyword, allJobPostsByParamter)
