import json
from watson_developer_cloud import DiscoveryV1
from discovery_helper import listCollections, getCollection

if __name__ == "__main__":
    # Production Instance Creds
    API_KEY = '<YOUR_API_KEY>'
    ENV_ID = '<YOUR_ENVIRONMENT_ID>'
    API_URL = '<YOUR_API_URL>'

    discovery = DiscoveryV1(version="<VERSION>", url = API_URL, iam_apikey = API_KEY)

    # this will list all collections
    collections = listCollections(ENV_ID)

    # your code here