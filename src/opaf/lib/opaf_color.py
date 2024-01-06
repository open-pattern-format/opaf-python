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

import re
import xml.dom.minidom


class OPAFColor:

    __DEFINE_NAME__ = "opaf:define_color"

    __HEX_COLORS__ = {
        'black': '#000000',
        'silver': '#C0C0C0',
        'white': '#FFFFFF',
        'red': '#FF0000',
        'purple': '#800080',
        'green': '#008000',
        'yellow': '#FFFF00',
        'blue': '#0000FF',
    }

    def __init__(self,
                 name,
                 value):
        self.name = name
        self.value = value

    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__DEFINE_NAME__)
        node.setAttribute("name", self.name)
        node.setAttribute("value", self.value)

        return node

    @staticmethod
    def to_hex(value):
        if not OPAFColor.is_valid(value):
            raise Exception("'" + value + "' is not a valid hex rgb color string")

        if value in OPAFColor.__HEX_COLORS__:
            value = OPAFColor.__HEX_COLORS__[value]

        return value.lower()

    @staticmethod
    def is_valid(value):
        hex_str = re.compile(r'#[a-fA-F0-9]{6}$')

        if value in OPAFColor.__HEX_COLORS__:
            return True

        return hex_str.match(value)

    @staticmethod
    def parse(node):
        if not isinstance(node, xml.dom.minidom.Node):
            raise Exception("Unable to parse object of type " + node.__class__)

        if not node.nodeType == xml.dom.Node.ELEMENT_NODE:
            raise Exception("Unexpected node type")

        if not node.nodeName == OPAFColor.__DEFINE_NAME__:
            raise Exception(
                "Expected node with name '"
                + OPAFColor.__DEFINE_NAME__
                + "' and got '"
                + node.nodeName
                + "'"
            )

        # Parse node element
        root_element = node

        # Name
        name = root_element.getAttribute('name')

        # Color
        value = root_element.getAttribute('value').strip().lower()
        value = OPAFColor.to_hex(value)

        return OPAFColor(name, value)
