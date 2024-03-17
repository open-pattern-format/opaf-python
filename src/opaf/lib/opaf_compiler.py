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
        'repeat',
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

    def __process_charts(self, parent):
        for chart in self.opaf_doc.opaf_charts:
            chart_nodes = []

            chart_element = self.compiled_doc.createElement('chart')
            chart_element.setAttribute('name', chart.name)

            chart.row_actions = []
            chart.processed_row_actions = []
            chart.row_colors = []
            chart.row_counts = []

            for r in chart.rows:
                row = parseString(r).documentElement
                chart_nodes += self.__process_opaf_node(row, self.global_values)

                r_actions = []

                for a in row.getElementsByTagName('opaf:action'):
                    if a.getAttribute('name') == 'none':
                        continue

                    if Utils.evaluate_node_condition(a, self.global_values):
                        r_actions.append(a)

                if len(r_actions) == 0:
                    raise Exception("opaf:chart - no actions found for row")

                chart.row_actions.append(r_actions)

            for n in chart_nodes:
                chart_element.appendChild(n.cloneNode(True))

                # Store row info
                actions = []
                colors = []
                count = 0

                for a in n.childNodes:
                    total = int(a.getAttribute('total'))
                    color = a.getAttribute('color')
                    actions.append(a)
                    count += total

                    for i in range(0, total):
                        colors.append(color)

                chart.processed_row_actions.append(actions)
                chart.row_colors.append(colors)
                chart.row_counts.append(count)

            parent.appendChild(chart_element)

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

                # Check for row specific attributes
                if attr.name == 'offset':
                    continue

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
        offset = 0

        if node.hasAttribute('offset'):
            offset = int(Utils.evaluate_expr(node.getAttribute('offset'), values))

        count = Utils.get_stitch_count(nodes) + offset

        new_element.setAttribute('count', str(count))
        self.global_values['opaf_prev_row_count'] = count
        self.global_values['opaf_prev_row_offset'] = offset

        return [new_element]

    def __process_opaf_action(self, node, values):
        # Get action object
        name = node.getAttribute('name')
        action = self.opaf_doc.get_opaf_action(name)

        # Process parameters
        params = action.params.copy()
        params.update(self.global_values)

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
            color = params['color'].split(':')

            if len(color) == 1:
                if color[0] not in self.opaf_doc.get_opaf_colors():
                    raise Exception('color "' + color[0] + '" is not defined')
            else:
                # Color from chart
                if color[0] == 'chart':
                    if len(color) != 4:
                        raise Exception(
                            'chart color definition is invalid: ' + params['color']
                        )

                    chart = self.opaf_doc.get_opaf_chart(color[1])
                    row = int(color[2]) - 1
                    stitch = int(color[3])

                    # Get row in correct range
                    if row >= len(chart.row_colors):
                        row = row % len(chart.row_colors)

                    # Get stitch in correct range
                    if stitch >= len(chart.row_colors[row]):
                        stitch = stitch % len(chart.row_colors[row])

                    if stitch < 0:
                        stitch = (
                            len(chart.row_colors[row])
                            -
                            (abs(stitch) % len(chart.row_colors[row]))
                        )

                    params['color'] = chart.row_colors[row][stitch]

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

    def __process_opaf_chart(self, node, values):
        # Get chart object
        name = node.getAttribute('name')
        chart = self.opaf_doc.get_opaf_chart(name)

        # Attributes
        row_num = 0
        offset = 0
        count = 0

        if node.hasAttribute('row'):
            row_num = int(
                Utils.str_to_num(
                    Utils.evaluate_expr(
                        node.getAttribute('row'),
                        values
                    )
                )
            )

        if node.hasAttribute('offset'):
            offset = int(
                Utils.str_to_num(
                    Utils.evaluate_expr(
                        node.getAttribute('offset'),
                        values
                    )
                )
            )

        if node.hasAttribute('count'):
            count = round(
                int(
                    Utils.str_to_num(
                        Utils.evaluate_expr(
                            node.getAttribute('count'),
                            values
                        )
                    )
                )
            )

        # Check row number has been specified
        if row_num <= 0:
            raise Exception(
                "opaf:chart received an invalid or missing 'row' attribute"
            )

        # Get row and actions
        if row_num > len(chart.row_actions):
            row_num = row_num % len(chart.row_actions)

            if row_num == 0:
                row_num = len(chart.row_actions)

        row_num -= 1

        # Processed actions
        r_actions = chart.row_actions[row_num]
        p_actions = chart.processed_row_actions[row_num]
        row_count = chart.row_counts[row_num]

        # Get offset in correct range
        if offset > row_count:
            offset = offset % row_count

        if offset < 0:
            offset = row_count - (abs(offset) % row_count)

        # Process nodes to return
        nodes = []

        # Handle single action case
        if len(p_actions) == 1:
            pa = p_actions[0]
            a = r_actions[0]

            a_count = int(pa.getAttribute('count'))
            a_total = int(pa.getAttribute('total'))
            a_sts = round(a_total / a_count)

            if (count % a_sts) != 0:
                raise Exception("opaf:chart - cannot return desired stitch count")

            a.setAttribute('count', str(round(count / a_sts)))
            nodes += self.__process_opaf_action(a, values)
            count = 0
            offset = 0

        # Handle offset
        if offset > 0:
            for i in range(0, len(p_actions)):
                if count == 0:
                    break

                pa = p_actions[i]

                p_count = int(pa.getAttribute('count'))
                p_total = int(pa.getAttribute('total'))

                # Check if offset is reached
                if offset == 0 and count >= p_total:
                    nodes.append(pa)
                    count -= p_total
                    continue

                if p_total <= offset:
                    offset -= p_total
                    continue

                # Refactor action for offset or stitch count
                a = r_actions[i]

                if offset == 0:
                    if (round(p_total / p_count) % count) != 0:
                        raise Exception("opaf:chart - cannot return desired stitch count")

                    a_count = round((p_count / p_total) * count)
                    count -= round((p_total / p_count) * a_count)
                else:
                    if round(p_total / p_count) > offset:
                        raise Exception("opaf:chart - offset is invalid")

                    a_count = p_count - round((p_count / p_total) * offset)
                    c_count = round((p_count / p_total) * count)

                    if a_count > c_count:
                        if (count % round(p_total / p_count)) != 0:
                            raise Exception(
                                "opaf:chart - cannot return desired stitch count"
                            )

                        a_count = c_count

                    count -= round((p_total / p_count) * a_count)
                    offset = 0

                a.setAttribute('count', str(a_count))
                nodes += self.__process_opaf_action(a, values)

        # Work out number of row repeats for stitch count
        if count > 0:
            repeat_count = math.floor(count / row_count)

            if repeat_count > 0:
                repeat_element = self.compiled_doc.createElement("repeat")
                repeat_element.setAttribute("count", str(repeat_count))

                for ra in p_actions:
                    repeat_element.appendChild(ra)

                nodes.append(repeat_element)

                # Update stitch count
                count -= repeat_count * row_count

        # Work out remaining stitches
        if count > 0:
            for i in range(0, len(p_actions)):
                # Check if stitch count is reached
                if count == 0:
                    break

                pa = p_actions[i]

                p_count = int(pa.getAttribute('count'))
                p_total = int(pa.getAttribute('total'))

                if round(p_total / p_count) > count:
                    raise Exception("opaf:chart - cannot return desired stitch count")

                if p_total <= count:
                    nodes.append(pa)
                    count -= p_total
                    continue

                # Refactor action for desired stitch count
                if (count % round(p_total / p_count)) != 0:
                    raise Exception("opaf:chart - cannot return desired stitch count")

                a = r_actions[i]
                a_count = round((p_count / p_total) * count)
                a.setAttribute('count', str(a_count))
                nodes += self.__process_opaf_action(a, values)

                break

        # Add chart reference to actions
        Utils.add_chart_attribute(nodes, name, row_num)

        return nodes

    def __process_opaf_block(self, node, values):
        # Get block object
        name = node.getAttribute('name')
        block = self.opaf_doc.get_opaf_block(name)

        # Add global values to params
        values.update(self.global_values)

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

        params.update(self.global_values)

        # Process elements the required number of times handling repeats
        node_arrays = []

        for i in range(0, repeat):
            # Add default params
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
                        repeat_element.appendChild(n.cloneNode(deep=True))

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
            component_element.appendChild(node.cloneNode(deep=True))

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
                image_element.setAttribute(
                    "data",
                    base64.b64encode(i.data).decode('ascii')
                )

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
        self.__process_charts(root_element)

        # Process components
        for component in self.opaf_doc.opaf_components:
            if component.condition:
                if not Utils.evaluate_condition(component.condition, self.global_values):
                    continue

            component_element = self.__process_component(component)
            root_element.appendChild(component_element)

        return self.compiled_doc.toxml()
