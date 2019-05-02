import json
from pathlib import Path

import xmltodict

# Path of toc.xml
TOC_XML = '<PATH/*.xml>'


def parseXML(xml):
    """
    params: path of the XML file to be converted to JSON
    returns: parsed XML to JSON (as string)
    """
    with open(Path(TOC_XML)) as toc:
        toc_json = json.dumps(xmltodict.parse(toc.read()), indent=2)
        toc_json = toc_json.replace('@', '')
        return toc_json


def cleanerUtil(json_file):
    path_junk = 'http://help.central.arubanetworks.com/latest/documentation/online_help'
    refined_htm = htm.replace(path_junk, '')
    return json.loads(toc_json), refined_htm


def getHtmlLabel(htm_file, json_file, value_to_find):
    for k, v in json_file.items():
        while json_file[k] != value_to_find:
            json_file = json_file[k]
            print(json_file)


if __name__ == "__main__":

    # Converting TOC XML into JSON
    toc_json = parseXML(TOC_XML)

    # Getting labels from TOC JSON
    htm = 'http://help.central.arubanetworks.com/latest/documentation/online_help/Content/public_cloud/get_started/supported_switches.htm'
    toc_dict, refined_htm = cleanerUtil(toc_json)
    label = getHtmlLabel(htm, toc_dict, refined_htm)
