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

import base64
import math
import xml.dom.minidom
import uuid

from xml.dom.minidom import parseString

from opaf.lib import (
    OPAFColor,
    Utils
)


class OPAFCompiler:

    __PROTECTED_ATTRS__ = [
        'xmlns:opaf',
        'condition',
        'name',
    ]

    def __init__(self, doc, configs={}, colors={}):
        self.opaf_doc = doc
        self.compiled_doc = xml.dom.minidom.Document()
        self.custom_config = configs
        self.custom_colors = colors
        self.global_values = {}

    def __process_configs(self, parent):
        for c in self.opaf_doc.opaf_configs:
            if c.name in self.custom_config:
                # Check allowed values
                if c.allowed_values:
                    if not self.custom_config[c.name] in c.allowed_values:
                        raise Exception(
                            '"' +
                            self.custom_config[c.name] +
                            '" is not a valid value for "' +
                            c.name +
                            '"'
                        )

                self.global_values[c.name] = Utils.str_to_num(
                    self.custom_config[c.name]
                )

                continue
            else:
                self.global_values[c.name] = Utils.str_to_num(
                    Utils.evaluate_expr(
                        c.value,
                        self.global_values
                    )
                )

            # Add config to project
            config_element = self.compiled_doc.createElement('config')
            config_element.setAttribute('name', c.name)
            config_element.setAttribute("value", str(self.global_values[c.name]))
            parent.appendChild(config_element)

    def __process_values(self, parent):
        for v in self.opaf_doc.opaf_values:
            # Check condition
            if v.condition:
                if not Utils.evaluate_condition(v.condition, self.global_values):
                    continue

            self.global_values[v.name] = Utils.str_to_num(
                Utils.evaluate_expr(
                    v.value,
                    self.global_values
                )
            )

    def __process_colors(self, parent):
        for c in self.opaf_doc.opaf_colors:
            color_element = self.compiled_doc.createElement('color')
            color_element.setAttribute('name', c.name)

            # Determine value to use
            value = c.value

            if c.name in self.custom_colors:
                value = OPAFColor.to_hex(self.custom_colors[c.name].lower())

            color_element.setAttribute('value', value)

            parent.appendChild(color_element)

    def __process_charts(self, parent):
        for chart in self.opaf_doc.opaf_charts:
            chart_nodes = []

            chart_element = self.compiled_doc.createElement('chart')
            chart_element.setAttribute('name', chart.name)

            for r in chart.rows:
                row = parseString(r).documentElement
                chart_nodes += self.__process_opaf_node(row, self.global_values)

            for n in chart_nodes:
                chart_element.appendChild(n.cloneNode(True))

            parent.appendChild(chart_element)

    def __process_opaf_instruction(self, node, values):
        new_element = self.compiled_doc.createElement('instruction')

        # Update global values
        values.update(self.global_values)

        # Check type attribute
        if node.hasAttribute('name'):
            new_element.setAttribute(
                'name',
                Utils.evaluate_expr(node.getAttribute('name'), values)
            )

        nodes = []

        for child in node.childNodes:
            nodes += self.__process_opaf_node(child, values)

        for n in nodes:
            new_element.appendChild((n.cloneNode(deep=True)))

        return [new_element]

    def __process_opaf_repeat(self, node, values):
        new_element = self.compiled_doc.createElement('repeat')

        # Check type attribute
        if not node.hasAttribute('count'):
            raise Exception("Repeat attribute 'count' is missing")

        # Update global values
        values.update(self.global_values)

        # Copy attributes
        if node.hasAttributes():
            for i in range(0, node.attributes.length):
                attr = node.attributes.item(i)

                # Check protected attributes
                if attr.name not in self.__PROTECTED_ATTRS__:
                    new_element.setAttribute(
                        attr.name,
                        Utils.evaluate_expr(attr.value, values)
                    )

        nodes = []

        for child in node.childNodes:
            nodes += self.__process_opaf_node(child, values)

        for n in nodes:
            new_element.appendChild((n.cloneNode(deep=True)))

        return [new_element]

    def __process_opaf_row(self, node, values):
        new_element = self.compiled_doc.createElement('row')

        # Check type attribute
        if not node.hasAttribute('type'):
            raise Exception("Row attribute 'type' is missing")

        # Update global values
        values.update(self.global_values)

        # Copy attributes
        if node.hasAttributes():
            for i in range(0, node.attributes.length):
                attr = node.attributes.item(i)

                # Check protected attributes
                if attr.name not in self.__PROTECTED_ATTRS__:
                    new_element.setAttribute(
                        attr.name,
                        Utils.evaluate_expr(attr.value, values)
                    )

        nodes = []

        for child in node.childNodes:
            nodes += self.__process_opaf_node(child, values)

        for n in nodes:
            new_element.appendChild((n.cloneNode(deep=True)))

        # Calculate row count
        count = Utils.get_stitch_count(nodes)

        new_element.setAttribute('count', str(count))

        return [new_element]

    def __process_opaf_action(self, node, values):
        # Get action object
        name = node.getAttribute('name')
        action = self.opaf_doc.get_opaf_action(name)

        # Process parameters
        params = action.params.copy()

        for i in range(0, node.attributes.length):
            attr = node.attributes.item(i)

            # Check protected attributes
            if attr.name in self.__PROTECTED_ATTRS__:
                continue

            params[attr.name] = Utils.str_to_num(
                Utils.evaluate_expr(
                    attr.value,
                    values
                )
            )

        # Check parameters
        for p in params:
            if params[p] == '':
                raise Exception(
                    'Parameter "'
                    + p
                    + '" is not defined for action "'
                    + name
                    + '"'
                )

        # Process color
        if 'color' in params:
            if params['color'] not in self.opaf_doc.get_opaf_colors():
                raise Exception('color "' + params['color'] + '" is not defined')

        # Process action elements
        nodes = []

        for e in action.elements:
            element = parseString(e).documentElement

            # Handle condition
            if element.hasAttribute('condition'):
                if not Utils.evaluate_condition(
                    element.getAttribute('condition'),
                    params
                ):
                    continue

                element.removeAttribute('condition')

            for i in range(0, element.attributes.length):
                attr = element.attributes.item(i)
                element.setAttribute(attr.name, Utils.evaluate_expr(attr.value, params))
            
            # Chart attribute
            if 'chart' in params:
                element.setAttribute('chart', params['chart'])

            nodes.append(element)

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

        # Add global values
        values.update(self.global_values)

        # Process parameters
        params = block.params.copy()

        for i in range(0, node.attributes.length):
            attr = node.attributes.item(i)

            # Check protected attributes
            if attr.name in self.__PROTECTED_ATTRS__:
                continue

            params[attr.name] = Utils.str_to_num(
                Utils.evaluate_expr(
                    attr.value,
                    values
                )
            )

        # Check parameters
        for p in params:
            if params[p] == '':
                raise Exception(
                    'Parameter "'
                    + p
                    + '" is not defined for block "'
                    + name
                    + '"'
                )

        params.update(self.global_values)

        # Process elements the required number of times handling repeats
        nodes = []

        for e in block.elements:
            element = parseString(e).documentElement
            nodes += self.__process_opaf_node(element, params)

        return nodes

    def __process_opaf_text(self, node, values):
        text_element = self.compiled_doc.createElement('text')

        if node.hasAttribute('data'):
            text_element.setAttribute(
                'data',
                Utils.evaluate_expr(
                    node.getAttribute('data'),
                    values
                )
            )

        return text_element

    def __process_opaf_node(self, node, values):
        compiled_nodes = []

        if Utils.evaluate_node_condition(node, values):
            if node.tagName == 'opaf:action':
                compiled_nodes += self.__process_opaf_action(node, values)

            elif node.tagName == 'opaf:block':
                compiled_nodes += self.__process_opaf_block(node, values)

            elif node.tagName == 'opaf:instruction':
                compiled_nodes += self.__process_opaf_instruction(node, values)

            elif node.tagName == 'opaf:repeat':
                compiled_nodes += self.__process_opaf_repeat(node, values)

            elif node.tagName == 'opaf:row':
                compiled_nodes += self.__process_opaf_row(node, values)

            elif node.tagName == 'opaf:image':
                compiled_nodes += self.__process_opaf_image(node)

            elif node.tagName == 'opaf:text':
                compiled_nodes.append(self.__process_opaf_text(node, values))

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
            component_element.appendChild(node.cloneNode(deep=True))

        return component_element

    def compile(self, name):
        if not self.opaf_doc:
            raise Exception("OPAF document is not set. Nothing to compile")

        if not self.opaf_doc.pkg_version:
            raise Exception("OPAF document has not been packaged. Compilation aborted.")

        # Set root element
        root_element = self.compiled_doc.createElement("project")
        root_element.setAttribute("name", name)
        root_element.setAttribute("unique_id", str(uuid.uuid4()))

        self.compiled_doc.appendChild(root_element)

        # Images
        if self.opaf_doc.opaf_images:
            for i in self.opaf_doc.opaf_images:
                image_element = self.compiled_doc.createElement("image")
                image_element.setAttribute("name", i.name)
                image_element.setAttribute(
                    "data",
                    base64.b64encode(i.data).decode('ascii')
                )

                root_element.appendChild(image_element)

        # Pattern
        pattern_element = self.compiled_doc.createElement("pattern")
        pattern_element.setAttribute("unique_id", self.opaf_doc.unique_id)
        pattern_element.setAttribute("name", self.opaf_doc.name)
        pattern_element.setAttribute("version", self.opaf_doc.version.__str__)

        # Metadata
        if self.opaf_doc.opaf_metadata:
            metadata_element = self.compiled_doc.createElement("metadata")

            for e in self.opaf_doc.opaf_metadata.elements:
                element = parseString(e).documentElement
                metadata_element.appendChild(element)

            pattern_element.appendChild(metadata_element)

        root_element.appendChild(pattern_element)

        # Evaluate global values
        self.__process_configs(root_element)
        self.__process_values(root_element)

        # Process colors
        self.__process_colors(root_element)

        # Process charts
        self.__process_charts(root_element)

        # Process components
        for component in self.opaf_doc.opaf_components:
            if component.condition:
                if not Utils.evaluate_condition(component.condition, self.global_values):
                    continue

            component_element = self.__process_component(component)
            root_element.appendChild(component_element)

        return self.compiled_doc.toxml()
