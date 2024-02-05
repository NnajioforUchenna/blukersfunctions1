import json
from google.oauth2 import service_account
import os
import redis

current_directory = os.path.dirname(os.path.abspath(__file__))
service_key_path = os.path.join(current_directory, 'serviceKey2.json')

credentials = service_account.Credentials.from_service_account_file(service_key_path)

redis_host = os.environ.get("REDISHOST", "localhost")
redis_port = int(os.environ.get("REDISPORT", 6379))
redis_client = redis.StrictRedis(host=redis_host, port=redis_port)


def saveSearch2Cache(queryParameter, jobPosts):
    try:
        # Serialize the list of job posts to a JSON string
        jobPosts_str = json.dumps(jobPosts)

        # Save the JSON string to Redis using the query parameter as the key
        redis_client.set(queryParameter, jobPosts_str)
    except Exception as e:
        print(f"Error saving data to cache: {e}")


def getSearchFromCache(queryParameter):
    try:
        # Fetch the stored value from Redis using the query parameter as the key
        jobPosts_str = redis_client.get(queryParameter)

        # If the key was found in Redis, deserialize the JSON string back to a list of dictionaries
        if jobPosts_str:
            return json.loads(jobPosts_str.decode('utf-8'))
    except Exception as e:
        print(f"Error fetching data from cache: {e}")

    # Return an empty list if the key wasn't found or if there was an error
    return []


# Delete data from the current database
# redis_client.flushdb()
