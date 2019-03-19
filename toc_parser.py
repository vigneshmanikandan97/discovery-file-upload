import xmltodict
import pprint
from pathlib import Path
import json

TOC_FILE = 'C:/Users/manikvig/Documents/Work/discovery-file-upload/toc_file.xml'
with open(Path(TOC_FILE)) as toc:
    json.dumps(xmltodict.parse(toc.read()), indent=2)