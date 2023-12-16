#   Copyright 2023 Scott Ware
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from importlib.metadata import version
import xml.dom.minidom
from xml.parsers.expat import ExpatError
from math import *
import uuid

from opaf.lib import OPAFAction, OPAFDocument, Utils


class OPAFPackager:

    def __init__(self, doc=None):
        self.opaf_doc = doc
        self.pkg_doc = xml.dom.minidom.Document()
    
    def package(self):
        # Set root element
        root_element = self.pkg_doc.createElement("pattern")
        root_element.setAttribute("xmlns:opaf", self.opaf_doc.opaf_namespace)
        root_element.setAttribute("pkg_version", version('opaf'))
        root_element.setAttribute("name", self.opaf_doc.name)

        if not self.opaf_doc.unique_id:
            self.opaf_doc.set_unique_id(str(uuid.uuid4()))
        
        root_element.setAttribute("unique_id", self.opaf_doc.unique_id)

        if not self.opaf_doc.version:
            self.opaf_doc.set_version('1.0')
        
        root_element.setAttribute("version", self.opaf_doc.version)

        self.pkg_doc.appendChild(root_element)

        # Actions
        for action in self.opaf_doc.opaf_actions:
            root_element.appendChild(action.to_node())

        # Values
        for value in self.opaf_doc.opaf_values:
            root_element.appendChild(value.to_node())

        # Images
        for image in self.opaf_doc.opaf_images:
            root_element.appendChild(image.to_node())

        # Blocks
        for block in self.opaf_doc.opaf_blocks:
            root_element.appendChild(block.to_node())

        # Components
        for component in self.opaf_doc.opaf_components:
            root_element.appendChild(component.to_node())

        return self.pkg_doc.toxml()