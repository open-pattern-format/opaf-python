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

import os
import re
import xml.dom.minidom

from importlib.metadata import metadata

from opaf.lib import OPAFFuncs


SUPPORTED_NODES = [
    'define_action',
    'define_block',
    'define_chart',
    'define_color',
    'define_image',
    'define_value',
    'action',
    'block',
    'component',
    'image',
    'instruction',
    'repeat',
    'row',
    'text'
]


def parse_uri(uri, dirname):
    result = ""
    split_str = uri.split('://')

    if len(split_str) != 2:
        return result

    # Get absolute path
    if split_str[0] == "file":
        if (not os.path.isabs(split_str[1])):
            split_str[1] = os.path.join(dirname, split_str[1])
        if os.path.isfile(split_str[1]):
            result = os.path.abspath(split_str[1])

    return result


def str_to_num(str):
    try:
        return int(str)
    except ValueError:
        pass

    try:
        val = float(str)

        return val
    except ValueError:
        return str


def check_node(node, allowed_nodes=[]):
    if not node.hasChildNodes():
        return node

    for child in list(node.childNodes):
        if not child.nodeType == xml.dom.Node.ELEMENT_NODE:
            node.removeChild(child)
            continue

        if not child.prefix == "opaf":
            raise Exception("Node with name '" + child.tagName + "' not recognized")

        if child.localName not in SUPPORTED_NODES:
            raise Exception("Node with name '" + child.tagName + "' not recognized")

        if len(allowed_nodes) > 0:
            if child.localName not in allowed_nodes:
                raise Exception(
                    "Node with name '" + child.tagName + "' is not allowed in this scope"
                )

        if child.hasChildNodes():
            check_node(child, allowed_nodes)

    return node


def get_url(name):
    urls = []
    urls = metadata('opaf').get_all("Project-URL")

    if len(urls) == 0:
        raise Exception("No URLs found in distribution package metadata")

    for url in urls:
        if url.startswith(name):
            return url.split(", ")[1]

    raise Exception("No URL found in distribution metadata with name '" + name + "'")


def write_to_file(data, filepath):
    with open(filepath, 'w', encoding='UTF-8') as f:
        f.write(data)


def params_to_str(params):
    param_strs = []

    for param in params:
        if params[param] == None:
            param_strs.append(param)
        else:
            param_strs.append(param + '=' + str(params[param]))

    return " ".join(param_strs)


def evaluate_expr(expr, values):
    pattern = re.compile(r'[$][{](.*?)[}]', re.S)

    context = {
        "__builtins__": {},
        "ROUND": OPAFFuncs.round,
        "MROUND": OPAFFuncs.mround,
        "FLOOR": OPAFFuncs.floor,
        "CEIL": OPAFFuncs.ceil,
        "LT": OPAFFuncs.less,
        "GT": OPAFFuncs.greater,
        "EQ": OPAFFuncs.equals,
        "NEQ": OPAFFuncs.not_equals,
        "AND": OPAFFuncs._and_,
        "OR": OPAFFuncs._or_,
        "NOT": OPAFFuncs._not_,
        "ABS": OPAFFuncs.abs,
        "CHOOSE": OPAFFuncs.choose,
        "ISEMPTY": OPAFFuncs.is_empty,
        "ODD": OPAFFuncs.odd,
        "EVEN": OPAFFuncs.even,
        "MULTIPLE": OPAFFuncs.multiple,
        "MAX": OPAFFuncs.max,
        "MIN": OPAFFuncs.min,
        "BOOL": OPAFFuncs.to_bool,
    }

    def eval_fn(obj):
        try:
            result = eval(obj.group(1), context, values)
        except Exception as e:
            raise Exception(
                "Failed to evaluate: <%s>" % (obj.group(1)) + ", " + str(e)
            )

        return str(result)

    return re.sub(pattern, eval_fn, expr)


def evaluate_condition(condition, values):
    result = evaluate_expr(condition, values)

    if result.lower() == 'false':
        return False

    if result.lower() == 'true':
        return True

    raise Exception(
        "Condition " + condition + " did not evaluate to 'true' or 'false' as expected"
    )

def evaluate_node_condition(node, values):
    if node.hasAttribute('condition'):
        condition = node.getAttribute('condition')

        if condition != "":
            return evaluate_condition(condition, values)

    return True


def sort_node_array(node_arr):
    # Store nodes and number of adjacent repeats
    node_arrays = []
    repeats = []
    count = 1

    # Iterate through each node array
    for arr in node_arr:
        # Check if the current node is the same as the previous
        if len(node_arrays) > 0:
            if node_arr_to_string(arr) == node_arr_to_string(node_arrays[-1]):
                count += 1
                continue
            else:
                node_arrays.append(arr)

                # Reset repeat count
                repeats.append(count)
                count = 1
        else:
            node_arrays.append(arr)

    # Add final node repeat count
    repeats.append(count)

    return node_arrays, repeats


def contains_duplicates(arr):
    if not len(arr) > 1:
        return False

    # Create string array
    str_arr = []

    for a in arr:
        str_arr.append(node_arr_to_string(a))

    for i in range(1, len(str_arr)):
        if str_arr[i] == str_arr[i - 1]:
            return True

    return False


def node_arr_to_string(node_arr):
    str = ''

    for node in node_arr:
        str += node.toxml()

    return str


def parse_arg_list(arg_list):
    values = {}

    if arg_list:
        vals = arg_list.split(',')

        for v in vals:
            if '=' in v:
                v_arr = v.split('=')
                values[v_arr[0].strip()] = v_arr[1].strip()

    return values


def add_id_attribute(nodes, names, num):
    for n in nodes:
        if n.tagName in names:
            num += 1
            n.setAttribute('id', str(num))

        if n.hasChildNodes:
            num = add_id_attribute(n.childNodes, names, num)

    return num


def add_chart_attribute(nodes, name, row):
    for n in nodes:
        if n.localName == 'action':
            n.setAttribute('chart', name + ':' + str(row))

        if n.hasChildNodes:
            add_chart_attribute(n.childNodes, name, row)


def get_stitch_count(nodes):
    count = 0

    for n in nodes:
        if n.tagName == 'action':
            if n.hasAttribute('total'):
                count += int(n.getAttribute('total'))

        if n.tagName == 'repeat':
            if n.hasAttribute('count'):
                r_count = int(n.getAttribute('count'))
                count += (r_count * get_stitch_count(n.childNodes))

    return count
