import os
import re
from pathlib import Path

def find(path, regex):
    htm_files = []
    for root, directories, files in os.walk(path):
        for f in files:
            if re.search(regex, f):
                htm_files.append(os.path.join(root.replace('C:/Users/manikvig/Desktop/content', ''), f))
    return htm_files

# TEST CODE
# find('C:/Users/manikvig/Desktop/content', '\w*\.htm')