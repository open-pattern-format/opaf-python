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

import uuid
import xml.dom.minidom


class OPAFConfig:

    __DEFINE_NAME__ = "opaf:define_config"

    def __init__(self,
                 name,
                 value,
                 required=False,
                 allowed_values=None,
                 description=None):
        self.name = name
        self.value = value
        self.required = required
        self.allowed_values = allowed_values
        self.description = description

    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__DEFINE_NAME__)
        node.setAttribute("name", self.name)
        node.setAttribute("value", self.value)
        node.setAttribute('required', str(self.required).lower())

        if self.allowed_values:
            node.setAttribute('allowed_values', ','.join(self.allowed_values))

        if self.description:
            node.setAttribute("description", self.description)

        return node

    @staticmethod
    def parse(node):
        if not isinstance(node, xml.dom.minidom.Node):
            raise Exception("Unable to parse object of type " + node.__class__)

        if not node.nodeType == xml.dom.Node.ELEMENT_NODE:
            raise Exception("Unexpected node type")

        if not node.nodeName == OPAFConfig.__DEFINE_NAME__:
            raise Exception(
                "Expected node with name '"
                + OPAFConfig.__DEFINE_NAME__
                + "' and got '"
                + node.nodeName
                + "'"
            )

        # Name
        name = node.getAttribute("name")

        # Value
        value = node.getAttribute("value")

        # Required
        required = False

        if node.hasAttribute('required'):
            required = node.getAttribute('required').lower() == 'true'

        # Allowed Values
        allowed_values = []
        if node.hasAttribute('allowed_values'):
            allowed_values = node.getAttribute('allowed_values').split(',')
            allowed_values = map(str.strip, allowed_values)

        # Description
        description = None
        if node.hasAttribute("description"):
            description = node.getAttribute("description")

        return OPAFConfig(
            name,
            value,
            required,
            allowed_values,
            description
        )
