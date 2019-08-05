from watson_developer_cloud import DiscoveryV1


API_KEY = '<YOUR_API_KEY>'
ENV_ID = '<YOUR_ENVIRONMENT_ID>'
API_URL = '<YOUR_API_URL>'

discovery = DiscoveryV1(
    version="<VERSION>",
    url = API_URL,
    iam_apikey = API_KEY
)

configs = discovery.list_configurations(ENV_ID).get_result()
configs = configs.get('configurations')

for config in configs:

    if config['name'] != 'Default Configuration':
        print(discovery.delete_configuration(ENV_ID, config['configuration_id']).get_result())

    else:
        print('Only default configuration is available..')

collections = discovery.list_collections(ENV_ID).get_result()
collections = collections.get('collections')

if len(collections) > 0:

    for collection in collections:
        print(discovery.delete_collection(ENV_ID, collection.get('collection_id')).get_result())

else:
    print('No collections available..')
