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


class OPAFValue:

    __DEFINE_NAME__ = "opaf:define_value"

    def __init__(self,
                 name,
                 value,
                 uid=None,
                 condition=None):
        self.uid = uid
        self.name = name
        self.value = value
        self.condition = condition

    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__DEFINE_NAME__)
        node.setAttribute("unique_id", self.uid)
        node.setAttribute("name", self.name)
        node.setAttribute("value", self.value)

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
            raise Exception(
                "Expected node with name '"
                + OPAFValue.__DEFINE_NAME__
                + "' and got '"
                + node.nodeName
                + "'"
            )

        # Name
        name = node.getAttribute("name")

        # Value
        value = node.getAttribute("value")

        # Unique ID
        if node.hasAttribute("unique_id"):
            uid = node.getAttribute("unique_id")
        else:
            uid = str(uuid.uuid4())

        # Condition
        condition = None
        if node.hasAttribute("condition"):
            condition = node.getAttribute("condition")

        return OPAFValue(
            name,
            value,
            uid,
            condition
        )
