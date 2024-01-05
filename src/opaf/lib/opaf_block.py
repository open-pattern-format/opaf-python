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


class OPAFBlock:

    __NAME__ = "opaf:block"
    __DEFINE_NAME__ = "opaf:define_block"

    def __init__(self,
                 name,
                 elements,
                 params={}):
        self.name = name
        self.elements = elements
        self.params = params

    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__DEFINE_NAME__)
        node.setAttribute("name", self.name)

        if len(self.params) > 0:
            node.setAttribute("params", Utils.params_to_str(self.params))

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

        if not node.nodeName == OPAFBlock.__DEFINE_NAME__:
            raise Exception(
                "Expected node with name '"
                + OPAFBlock.__DEFINE_NAME__
                + "' and got '"
                + node.nodeName
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
                        params[param] = ''

        # Elements
        Utils.check_node(node)

        for child in node.childNodes:
            child.setAttribute("xmlns:opaf", Utils.get_url('namespace'))
            elements.append(child.toxml())

        return OPAFBlock(name, elements, params)
