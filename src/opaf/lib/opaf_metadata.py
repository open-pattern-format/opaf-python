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

import xml.dom.minidom

from xml.dom.minidom import parseString

from opaf.lib import Utils
from opaf.lib.metadata import MetadataUtils


class OPAFMetadata:

    __NAME__ = "opaf:metadata"

    def __init__(self,
                 elements=[]):
        self.elements = elements
    
    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__NAME__)

        for e in self.elements:
            element = parseString(e).documentElement
            node.appendChild(element)

        return node

    @staticmethod
    def parse(node):
        if not isinstance(node, xml.dom.minidom.Node):
            raise Exception("Unable to parse object of type " + node.__class__)
        
        if not node.nodeType == xml.dom.Node.ELEMENT_NODE:
            raise Exception("Unexpected node type")
        
        if not node.nodeName == OPAFMetadata.__NAME__:
            raise Exception("Expected node with name '" + OPAFMetadata.__NAME__ + "' and got '" + node.nodeName + "'")

        # Check metadata
        MetadataUtils.check_node(node)

        # Parse node element
        elements = []
        
        # Elements
        for child in node.childNodes:
            elements.append(child.toxml())
        
        return OPAFMetadata(elements)