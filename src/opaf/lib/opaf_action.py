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

from opaf.lib import Utils
from xml.dom.minidom import parseString


class OPAFAction:

    __NAME__ = "opaf:action"
    __DEFINE_NAME__ = "opaf:define_action"

    def __init__(self,
                 name,
                 custom=False,
                 params={},
                 elements=None):
        self.name = name
        self.custom = custom
        self.params = params
        self.elements = elements

    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__DEFINE_NAME__)
        node.setAttribute("name", self.name)
        node.setAttribute("custom", str(self.custom).lower())

        if len(self.params) > 0:
            node.setAttribute("params", Utils.params_to_str(self.params))

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

        if not node.nodeName == OPAFAction.__DEFINE_NAME__:
            raise Exception(
                "Expected node with name '"
                + OPAFAction.__DEFINE_NAME__
                + "' and got '" + node.nodeName
                + "'"
            )

        # Parse node element
        params = {}
        elements = []

        # Name
        name = node.getAttribute("name")

        # Params
        if node.hasAttribute("params"):
            params_attr = node.getAttribute("params")

            if params_attr:
                for param in params_attr.split(" "):
                    if '=' in param:
                        param = param.split('=')
                        params[param[0]] = Utils.str_to_num(param[1])
                    else:
                        params[param] = None

        # Elements
        actions = node.getElementsByTagName("action")

        for action in actions:
            elements.append(action.toxml())

        custom = False
        if node.hasAttribute("custom"):
            custom = node.getAttribute("custom").lower() == "true"
        

        return OPAFAction(name, custom, params, elements)
