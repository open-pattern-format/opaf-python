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
        'repeat',
        'offset'
    ]

    def __init__(self, doc, values={}, colors={}):
        self.opaf_doc = doc
        self.compiled_doc = xml.dom.minidom.Document()
        self.custom_values = values
        self.custom_colors = colors
        self.global_values = {}

    def __process_values(self, parent):
        for v in self.opaf_doc.opaf_values:
            # Check condition
            if v.condition:
                if not Utils.evaluate_condition(v.condition, self.global_values):
                    continue

            if v.config:
                config_element = self.compiled_doc.createElement('config')
                config_element.setAttribute('name', v.name)

                if v.name in self.custom_values:
                    # Check allowed values
                    if v.allowed_values:
                        if not self.custom_values[v.name] in v.allowed_values:
                            raise Exception(
                                '"' +
                                self.custom_values[v.name] +
                                '" is not a valid value for "' +
                                v.name +
                                '"'
                            )

                    config_element.setAttribute("value", self.custom_values[v.name])
                    parent.appendChild(config_element)

                    self.global_values[v.name] = Utils.str_to_num(
                        self.custom_values[v.name]
                    )

                    continue
                else:
                    config_element.setAttribute("value", v.value)
                    parent.appendChild(config_element)

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

    def __process_opaf_row(self, node, values):
        new_element = self.compiled_doc.createElement('row')

        # Check type attribute
        if not node.hasAttribute('type'):
            raise Exception("Row attribute 'type' is missing")

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
            new_element.appendChild(n)

        # Calculate row count
        offset = 0

        if node.hasAttribute('offset'):
            offset = int(Utils.evaluate_expr(node.getAttribute('offset'), values))

        count = Utils.get_stitch_count(nodes) + offset

        new_element.setAttribute('count', str(count))
        self.global_values['prev_row_count'] = count

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

        Utils.validate_params(self.opaf_doc, params)
        nodes = Utils.evaluate_action_node(action, params)

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

    def __process_opaf_chart(self, node, values):
        # Get chart object
        name = node.getAttribute('name')
        chart = self.opaf_doc.get_opaf_chart(name)

        # Attributes
        row_num = 0
        repeat = 1

        if node.hasAttribute('row'):
            row_num = int(
                Utils.str_to_num(
                    Utils.evaluate_expr(
                        node.getAttribute('row'),
                        values
                    )
                )
            )

        if node.hasAttribute('repeat'):
            repeat = round(
                int(
                    Utils.str_to_num(
                        Utils.evaluate_expr(
                            node.getAttribute('repeat'),
                            values
                        )
                    )
                )
            )

        nodes = []

        # Choose specific row or all rows
        if row_num > 0:
            if len(chart.rows) >= row_num:
                row = parseString(chart.rows[row_num - 1]).documentElement

                for c in row.getElementsByTagName('opaf:action'):
                    if c.getAttribute('name') == 'none':
                        continue

                    nodes += self.__process_opaf_node(c, values)

                # Add chart reference to action
                Utils.add_chart_attribute(nodes, name, row_num - 1)

        else:
            for i in range(len(chart.rows)):
                row = parseString(chart.rows[i]).documentElement

                # Remove irrelevant actions
                for a in row.getElementsByTagName('opaf:action'):
                    if a.getAttribute('name') == 'none':
                        row.removeChild(a)

                r_nodes = self.__process_opaf_node(row, values)

                Utils.add_chart_attribute(r_nodes, name, i)
                nodes += r_nodes

        # Handle repeats
        if repeat > 1 and len(nodes) > 0:
            repeat_element = self.compiled_doc.createElement("repeat")
            repeat_element.setAttribute("count", str(repeat))

            for n in nodes:
                repeat_element.appendChild(n)

            return [repeat_element]
        else:
            return nodes

    def __process_opaf_block(self, node, values):
        # Get block object
        name = node.getAttribute('name')
        block = self.opaf_doc.get_opaf_block(name)

        # Repeat
        repeat = 1

        if node.hasAttribute('repeat'):
            repeat = round(
                int(
                    Utils.str_to_num(
                        Utils.evaluate_expr(
                            node.getAttribute('repeat'),
                            values
                        )
                    )
                )
            )

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

        params['repeat_total'] = repeat

        # Process elements the required number of times handling repeats
        node_arrays = []

        for i in range(0, repeat):
            # Add default params
            if 'prev_row_count' in self.global_values:
                params['prev_row_count'] = self.global_values['prev_row_count']

            params['repeat'] = i + 1

            nodes = []

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

    def __process_opaf_text(self, node, values):
        text_element = self.compiled_doc.createElement('text')

        if node.hasAttribute('heading'):
            text_element.setAttribute(
                'heading',
                Utils.evaluate_expr(
                    node.getAttribute('heading'),
                    values
                )
            )

        if node.hasAttribute('body'):
            text_element.setAttribute(
                'body',
                Utils.evaluate_expr(
                    node.getAttribute('body'),
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

            elif node.tagName == 'opaf:chart':
                compiled_nodes += self.__process_opaf_chart(node, values)

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
            component_element.appendChild(node)

        # Post-processing
        if component_element.hasChildNodes:
            # Add row IDs
            Utils.add_id_attribute(component_element.childNodes, ['row'], 0)

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
                image_element.setAttribute("data", i.data)

                root_element.appendChild(image_element)

        # Pattern
        pattern_element = self.compiled_doc.createElement("pattern")
        pattern_element.setAttribute("unique_id", self.opaf_doc.unique_id)
        pattern_element.setAttribute("name", self.opaf_doc.name)
        pattern_element.setAttribute("version", self.opaf_doc.version)

        # Metadata
        if self.opaf_doc.opaf_metadata:
            metadata_element = self.compiled_doc.createElement("metadata")

            for e in self.opaf_doc.opaf_metadata.elements:
                element = parseString(e).documentElement
                metadata_element.appendChild(element)

            pattern_element.appendChild(metadata_element)

        root_element.appendChild(pattern_element)

        # Evaluate global values
        self.__process_values(root_element)

        # Process colors
        self.__process_colors(root_element)

        # Process charts
        for chart in self.opaf_doc.opaf_charts:
            chart_nodes = []

            chart_element = self.compiled_doc.createElement('chart')

            for r in chart.rows:
                row = parseString(r).documentElement
                chart_nodes += self.__process_opaf_node(row, self.global_values)

            for n in chart_nodes:
                chart_element.appendChild(n)

            root_element.appendChild(chart_element)

        # Process components
        for component in self.opaf_doc.opaf_components:
            if component.condition:
                if not Utils.evaluate_condition(component.condition, self.global_values):
                    continue

            component_element = self.__process_component(component)
            root_element.appendChild(component_element)

        return self.compiled_doc.toxml()
