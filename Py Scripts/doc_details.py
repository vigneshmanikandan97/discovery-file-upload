import json
from watson_developer_cloud import DiscoveryV1
from discovery_helper import listCollections, getCollection

if __name__ == "__main__":
    # Production Instance Creds
    API_KEY = 'bEyrHwAUKTw4pwmehUFyQ1SYLD7ubOLPnTU3iXTOkVNW'
    ENV_ID = 'd1d4bd73-06eb-4c69-ac07-8d7aadac76d4'
    API_URL = 'https://gateway-wdc.watsonplatform.net/discovery/api'

    discovery = DiscoveryV1(version="2019-03-25", url = API_URL, iam_apikey = API_KEY)

    # this will list all collections
    collections = listCollections(ENV_ID)

    # your code here