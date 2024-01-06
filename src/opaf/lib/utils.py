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
import os
import re
import xml.dom.minidom

from importlib.metadata import metadata
from io import BytesIO
from math import ( # noqa
    ceil,
    floor,
    remainder
)
from PIL import Image
from xml.dom.minidom import parseString


SUPPORTED_NODES = [
    'define_action',
    'define_block',
    'define_color',
    'define_image',
    'define_value',
    'action',
    'block',
    'component',
    'helper',
    'image',
    'round',
    'row'
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


def check_node(node):
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

        if child.hasChildNodes():
            check_node(child)

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
        if params[param]:
            param_strs.append(param + '=' + str(params[param]))
        else:
            param_strs.append(param)

    return " ".join(param_strs)


def evaluate_expr(expr, values):
    pattern = re.compile(r'[$][{](.*?)[}]', re.S)

    def eval_fn(obj):
        try:
            result = eval(obj.group(1), None, values)
        except Exception as e:
            raise Exception(
                "Failed to evaluate: <%s>" % (obj.group(1)) + ", " + str(e)
            )

        return str(result)

    return re.sub(pattern, eval_fn, expr)


def evaluate_condition(condition, values):
    result = evaluate_expr(condition, values)

    if result == 'False' or result == '0':
        return False

    return True


def evaluate_node_condition(node, values):
    if node.hasAttribute('condition'):
        condition = node.getAttribute('condition')
        return evaluate_condition(condition, values)

    return True


def validate_params(doc, params):
    # Check colors
    if 'color' in params:
        colors = doc.get_opaf_colors()

        if params['color'] not in colors:
            raise Exception('color "' + params['color'] + '" is not defined')


def evaluate_action_node(action, values):
    # Process action elements
    nodes = []

    for e in action.elements:
        element = parseString(e).documentElement

        # Handle condition
        if element.hasAttribute('condition'):
            if not evaluate_condition(element.getAttribute('condition'), values):
                continue

            element.removeAttribute('condition')

        for i in range(0, element.attributes.length):
            attr = element.attributes.item(i)
            element.setAttribute(attr.name, evaluate_expr(attr.value, values))

        nodes.append(element)

    return nodes


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


def image_to_base64(img_path, size):
    img = Image.open(img_path)
    img.convert("RGB")
    img.thumbnail((size, size))

    img_file = BytesIO()
    img.save(img_file, format="WEBP")
    img_bytes = img_file.getvalue()
    b64_img = base64.b64encode(img_bytes)

    return b64_img.decode('ascii')


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
            add_id_attribute(n.childNodes, names, num)
