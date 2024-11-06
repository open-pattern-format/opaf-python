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


class OPAFChart:

    __DEFINE_NAME__ = "opaf:define_chart"

    CHART_NODES = [
        'action',
        'repeat',
        'row',
    ]

    def __init__(self,
                 name,
                 rows,
                 condition=None):
        self.name = name
        self.rows = rows
        self.condition = condition

    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__DEFINE_NAME__)
        node.setAttribute("name", self.name)

        if self.condition is not None:
            node.setAttribute("condition", self.condition)

        for r in self.rows:
            row = parseString(r).documentElement

            if row.hasAttribute('xmlns:opaf'):
                row.removeAttribute('xmlns:opaf')

            node.appendChild(row)

        return node

    @staticmethod
    def parse(node):
        if not isinstance(node, xml.dom.minidom.Node):
            raise Exception("Unable to parse object of type " + node.__class__)

        if not node.nodeType == xml.dom.Node.ELEMENT_NODE:
            raise Exception("Unexpected node type")

        if not node.nodeName == OPAFChart.__DEFINE_NAME__:
            raise Exception(
                "Expected node with name '"
                + OPAFChart.__DEFINE_NAME__
                + "' and got '"
                + node.nodeName
                + "'"
            )

        # Parse chart elements
        rows = []

        # Name
        name = node.getAttribute("name")

        if ':' in name:
            raise Exception("Chart name '" + name + "' contains invalid character ':'")
        
        # Condition
        condition = None
        if node.hasAttribute("condition"):
            condition = node.getAttribute("condition")

        # Elements
        Utils.check_node(node, OPAFChart.CHART_NODES)

        for child in node.childNodes:
            if child.localName == 'row':
                child.setAttribute("xmlns:opaf", Utils.get_url('namespace'))
                rows.append(child.toxml())

        return OPAFChart(name, rows, condition)
