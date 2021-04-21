from configparser import ConfigParser

cp = ConfigParser()

print("Read file: {}".format(cp.read('wdu-config.ini')[0]))
print("Available sections: {}".format(cp.sections()))

def getDiscoveryHelperConfig(param):
    """
    Get Discovery Helper configuration:
    @param - use any of the params available to you under discovery-helper section in the wdu-config.ini
    @return - string containing config data
    """
    if 'discovery-helper' in cp.sections():
        print("getting discovery helper config..")
        return cp.get('discovery-helper', param)

def getS3Config(param):
    """
    Get s3 configuration:
    @param - use any of the params available to you under s3-utils section in the wdu-config.ini
    @return - string containing config data
    """
    if 's3-utils' in cp.sections():
        print("getting s3 config..")
        return cp.get('s3-utils', param)

def getTocConfig(param):
    """
    Get TOC configuration:
    @param - use any of the params available to you under toc-parser section in the wdu-config.ini
    @return - string containing config data
    """
    if 'toc-parser' in cp.sections():
        print("getting toc config..")
        return cp.get('toc-parser', param)