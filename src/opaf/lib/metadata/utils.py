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



SUPPORTED_NODES = [
    'color',
    'description',
    'designer',
    'element',
    'gauge',
    'image',
    'link',
    'measurement',
    'needles',
    'published',
    'title',
    'schematic',
    'section',
    'size',
    'table',
    'tag',
    'technique',
    'text',
    'yarn'
]

TEXT_NODES = [
    'description',
    'published',
    'tag',
    'title'
]


def check_node(node):
    if not node.hasChildNodes():
        return node

    for child in list(node.childNodes):        
        if not child.nodeType == xml.dom.Node.ELEMENT_NODE:
            node.removeChild(child)
            continue

        if not child.localName in SUPPORTED_NODES:
            raise Exception("Node with name '" + child.tagName + "' not recognized")
        
        if child.localName in TEXT_NODES:
            continue

        if child.hasChildNodes():
            check_node(child)
    
    return node
