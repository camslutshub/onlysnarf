# for easily interacting with changeable page elements

from ..util.settings import Settings
from ..elements.driver import ELEMENTS as driverElements
from ..elements.login import ELEMENTS as loginElements
from ..elements.profile import ELEMENTS as profileElements

ONLYFANS_ELEMENTS = []
ONLYFANS_ELEMENTS.extend(driverElements)
ONLYFANS_ELEMENTS.extend(loginElements)
ONLYFANS_ELEMENTS.extend(profileElements)

# represents elements the webdriver sortof looks for
class Element:
    def __init__(self, name=None, classes=[], text=[], id=[]):
        self.name = name
        self.classes = classes
        self.text = text
        self.id = id

    def getClass(self):
        if self.classes and len(self.classes) > 0:
            return self.classes[0]
        return ""

    def getClasses(self):
        return self.classes

    def getText(self):
        if self.text and len(self.text) > 0:
            return self.text[0]
        return ""

    def getTexts(self):
        return self.text

    def getId(self):
        if self.id and len(self.id) > 0:
            return self.id[0]

    @staticmethod
    def get_element_by_name(name):
        Settings.dev_print("getting element: {}".format(name))
        if name == None:
            Settings.err_print("missing element name")
            return None
        global ONLYFANS_ELEMENTS
        for element in ONLYFANS_ELEMENTS:
            # element = Element(name=element["name"], classes=element["classes"], text=element["text"], id=element["id"])
            if str(element["name"]) == str(name):
                Settings.dev_print("prepped ele: {}".format(element["name"]))
                return Element(name=element["name"], classes=element["classes"], text=element["text"], id=element["id"])
        Settings.warn_print("missing element fetch - {}".format(name))
        return None