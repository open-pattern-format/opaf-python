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

from math import *
from xml.dom.minidom import parseString

from opaf.lib import OPAFHelpers, Utils


class OPAFCompiler:

    __PROTECTED_ATTRS__ = ['xmlns:opaf', 'condition', 'name', 'repeat']

    def __init__(self, doc, values):
        self.opaf_doc = doc
        self.compiled_doc = xml.dom.minidom.Document()
        self.custom_values = values
        self.global_values = {}

    def __process_values(self):
        for v in self.opaf_doc.opaf_values:
            # Check condition
            if v.condition:
                if not Utils.evaluate_condition(v.condition, self.global_values):
                    continue

            if v.config:
                if v.name in self.custom_values:
                    # Check allowed values
                    if v.allowed_values:
                        if not self.custom_values[v.name] in v.allowed_values:
                            raise Exception(
                                '"' +
                                self.custom_values[v.name] +
                                '" is not a valid value for "' +
                                v.name +
                                '". Allowed values are ' +
                                str(v.allowed_values)
                            )

                    self.global_values[v.name] = Utils.str_to_num(self.custom_values[v.name])
                    continue

            self.global_values[v.name] = Utils.str_to_num(Utils.evaluate_expr(v.value, self.global_values))

    def __process_opaf_row_round(self, node, name, values):
        new_element = self.compiled_doc.createElement(name)

        # Copy attributes
        if node.hasAttributes():
            for i in range(0, node.attributes.length):
                attr = node.attributes.item(i)

                # Check protected attributes
                if not attr.name in self.__PROTECTED_ATTRS__:
                    new_element.setAttribute(attr.name, attr.value)

        nodes = []

        for child in node.childNodes:
            nodes += self.__process_opaf_node(child, values)

        for n in nodes:
            new_element.appendChild(n)

        return [new_element]

    def __process_opaf_helper(self, node, values):
        name = node.getAttribute("name")

        # Check helper
        if not hasattr(OPAFHelpers, name):
            raise Exception('opaf helper "' + name + '" is not defined')

        # Process parameters
        params = {}
        
        for i in range(0, node.attributes.length):
            attr = node.attributes.item(i)

            # Check protected attributes
            if attr.name in self.__PROTECTED_ATTRS__:
                continue

            params[attr.name] = Utils.str_to_num(Utils.evaluate_expr(attr.value, values), True)

        # Get function
        helper = getattr(OPAFHelpers, name)
        nodes =  helper(self.opaf_doc, params)

        return nodes

    def __process_opaf_action(self, node, values):
        # Get action object
        name = node.getAttribute('name')
        action = self.opaf_doc.get_opaf_action(name)

        nodes = Utils.evaluate_action_node(action, values)

        return nodes

    def __process_opaf_image(self, node):
        name = node.getAttribute('name')

        # Check image is defined
        self.opaf_doc.get_opaf_image(name)

        new_element = self.compiled_doc.createElement('image')
        new_element.setAttribute('name', name)

        if node.hasAttribute('tag'):
            new_element.setAttribute('tag', node.getAttribute('tag'))

        if node.hasAttribute('caption'):
            new_element.setAttribute('caption', node.getAttribute('caption'))

        return [new_element]

    def __process_opaf_block(self, node, values):
        # Get block object
        name = node.getAttribute('name')
        block = self.opaf_doc.get_opaf_block(name)

        # Repeat
        repeat = 1
    
        if node.hasAttribute('repeat'):
            repeat = int(Utils.str_to_num(Utils.evaluate_expr(node.getAttribute('repeat'), values), True))

        # Process parameters
        params = block.params.copy()
    
        for i in range(0, node.attributes.length):
            attr = node.attributes.item(i)

            # Check protected attributes
            if attr.name in self.__PROTECTED_ATTRS__:
                continue

            params[attr.name] = Utils.str_to_num(Utils.evaluate_expr(attr.value, values), True)
        
        # Check parameters
        for p in params:
            if params[p] == '':
                raise Exception('Parameter "' + p + '" is not defined for block "' + name + '"')

        # Add default params
        params['repeat_total'] = repeat

        # Process elements the required number of times handling repeats
        node_arrays = []

        for i in range(0, repeat):
            nodes = []
            params['repeat'] = i + 1

            for e in block.elements:
                element = parseString(e).documentElement
                nodes += self.__process_opaf_node(element, params)
            
            node_arrays.append(nodes)
        
        if Utils.contains_duplicates(node_arrays):
            sorted_nodes, repeats = Utils.sort_node_array(node_arrays)

            node_arrays = []

            for na in zip(sorted_nodes, repeats):
                if na[1] > 1:
                    repeat_element = self.compiled_doc.createElement("repeat")
                    repeat_element.setAttribute("count", str(na[1]))

                    for n in na[0]:
                        repeat_element.appendChild(n)
                    
                    node_arrays.append([repeat_element])
                else:
                    node_arrays.append(na[0])

        # Combine node arrays
        nodes = []

        for narr in node_arrays:
            nodes += narr

        return nodes
    
    def __process_opaf_node(self, node, values):
        compiled_nodes = []

        if Utils.evaluate_node_condition(node, values):
            if node.tagName == 'opaf:action':
                compiled_nodes += self.__process_opaf_action(node, values)
            
            elif node.tagName == 'opaf:block':
                compiled_nodes += self.__process_opaf_block(node, values)

            elif node.tagName == 'opaf:round':
                compiled_nodes += self.__process_opaf_row_round(node, 'round', values)
                
            elif node.tagName == 'opaf:row':
                compiled_nodes += self.__process_opaf_row_round(node, 'row', values)

            elif node.tagName == 'opaf:helper':
                compiled_nodes += self.__process_opaf_helper(node, values)

            elif node.tagName == 'opaf:image':
                compiled_nodes += self.__process_opaf_image(node)

        return compiled_nodes
        
    def __process_component(self, component):
        component_element = self.compiled_doc.createElement("component")
        component_element.setAttribute("name", component.name)
        component_element.setAttribute("unique_id", component.uid)

        compiled_nodes = []

        for e in component.elements:
            element = parseString(e).documentElement
            compiled_nodes += self.__process_opaf_node(element, self.global_values)

        for node in compiled_nodes:
            component_element.appendChild(node)

        return component_element


    def compile(self):
        if not self.opaf_doc:
            raise Exception("OPAF document is not set. Nothing to compile")

        if not self.opaf_doc.pkg_version:
            raise Exception("OPAF document has not been packaged. Compilation aborted.")
        
        # Evaluate global values
        self.__process_values()

        # Set root element
        root_element = self.compiled_doc.createElement("pattern")
        root_element.setAttribute("name", self.opaf_doc.name)
        root_element.setAttribute("unique_id", self.opaf_doc.unique_id)
        root_element.setAttribute("version", self.opaf_doc.version)

        self.compiled_doc.appendChild(root_element)

        # Process components
        for component in self.opaf_doc.opaf_components:
            if component.condition:
                if not self.__evaluate_condition(component.condition):
                    continue

            component_element = self.__process_component(component)
            root_element.appendChild(component_element)

        return self.compiled_doc.toxml()