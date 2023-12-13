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
import uuid

from xml.dom.minidom import parseString

from opaf.lib import Utils

class OPAFComponent:

    __NAME__ = "opaf:component"

    def __init__(self,
                 name,
                 uid=None,
                 elements=None,
                 condition=None):
        self.name = name
        self.uid = uid
        self.elements = elements
        self.condition = condition
    
    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__NAME__)
        node.setAttribute("name", self.name)
        node.setAttribute("unique_id", self.uid)

        if not self.condition == None:
            node.setAttribute("condition", self.condition)

        for e in self.elements:
            element = parseString(e).documentElement

            if element.hasAttribute('xmlns:opaf'):
                element.removeAttribute('xmlns:opaf')

            node.appendChild(element)

        return node

    @staticmethod
    def parse(node):
        if not isinstance(node, xml.dom.minidom.Node):
            raise Exception("Unable to parse object of type " + node.__class__)
        
        if not node.nodeType == xml.dom.Node.ELEMENT_NODE:
            raise Exception("Unexpected node type")
        
        if not node.nodeName == OPAFComponent.__NAME__:
            raise Exception("Expected node with name '" + OPAFComponent.__NAME__ + "' and got '" + node.nodeName + "'")

        # Parse node element
        elements = []

        # Name
        name = node.getAttribute("name")

        # Unique ID
        if node.hasAttribute("unique_id"):
            uid = node.getAttribute("unique_id")
        else:
            uid = str(uuid.uuid4())

        # Condition
        condition = None
        if node.hasAttribute("condition"):
            condition = node.getAttribute("condition")

        # Elements
        Utils.check_node(node)
        
        for child in node.childNodes:
            child.setAttribute("xmlns:opaf", Utils.get_url('namespace'))
            elements.append(child.toxml())
                
        return OPAFComponent(name, uid=uid, elements=elements, condition=condition)