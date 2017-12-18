"""
Pre-process a location list in xml format
Citing python docs here: https://docs.python.org/2/library/xml.etree.elementtree.html

"""
import xml.etree.ElementTree as ET

class Capitol:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
    def asArray(self):
        return [self.latitude, self.longitude, self.name]

def process(fileLocation="poi.xml", array = False):
    capitols = []
    tree = ET.parse(fileLocation)
    root = tree.getroot()
    for child in root:
        new_capitol = Capitol(child.attrib, child.find('latitude').text, child.find('longitude').text)
        if (array):
            capitols.append(new_capitol.asArray())
        else:
            capitols.append(new_capitol)
    return capitols
