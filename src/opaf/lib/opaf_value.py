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

class OPAFValue:

    __DEFINE_NAME__ = "opaf:define_value"


    def __init__(self,
                 name,
                 value,
                 config=False,
                 allowed_values=None,
                 description=None,
                 condition=None):
        self.name = name
        self.value = value
        self.config = config
        self.allowed_values = allowed_values
        self.description = description
        self.condition = condition
    
    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__DEFINE_NAME__)
        node.setAttribute("name", self.name)
        node.setAttribute("value", self.value)
        node.setAttribute('config', str(self.config))

        if self.allowed_values:
            node.setAttribute('allowed_values', ','.join(self.allowed_values))

        if self.description:
            node.setAttribute("description", self.description)

        if self.condition:
            node.setAttribute("condition", self.condition)

        return node

    @staticmethod
    def parse(node):
        if not isinstance(node, xml.dom.minidom.Node):
            raise Exception("Unable to parse object of type " + node.__class__)
        
        if not node.nodeType == xml.dom.Node.ELEMENT_NODE:
            raise Exception("Unexpected node type")
        
        if not node.nodeName == OPAFValue.__DEFINE_NAME__:
            raise Exception("Expected node with name '" + OPAFValue.__DEFINE_NAME__ + "' and got '" + node.nodeName + "'")

        # Parse node element
        root_element = node

        # Name
        name = root_element.getAttribute("name")

        # Value
        value = root_element.getAttribute("value")

        # Configurable
        config = False

        if root_element.hasAttribute('config'):
            config = bool(root_element.getAttribute('config'))

        # Allowed Values
        allowed_values = []
        if root_element.hasAttribute('allowed_values'):
            allowed_values = root_element.getAttribute('allowed_values').split(',')

        # Description
        description = None
        if root_element.hasAttribute("description"):
            description = root_element.getAttribute("description")

        # Condition
        condition = None
        if root_element.hasAttribute("condition"):
            condition = root_element.getAttribute("condition")
        
        return OPAFValue(name, value, config, allowed_values, description, condition)