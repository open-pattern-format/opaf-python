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

import copy
import math
import xml

from opaf.lib import Utils


def __even_row(opaf_doc, params, offset=0):
    nodes = []
    doc = xml.dom.minidom.Document()

    # Get actions from document
    make_action = opaf_doc.get_opaf_action(params['action'])
    stitch_action = opaf_doc.get_opaf_action(params['stitch'])

    # Create temp parameters to use for action evaluation
    make_params = make_action.params.copy()
    stitch_params = stitch_action.params.copy()

    if 'color' in params:
        make_params['color'] = params['color']
        stitch_params['color'] = params['color']

    # Evaluate make action
    make_nodes = Utils.evaluate_action_node(make_action, make_params)

    # Calculate knit count
    main_stitch_count = math.ceil(params['count'] / params['num']) - offset
    secondary_stitch_count = math.floor(params['count'] / params['num']) - offset
    remainder = params['count'] % params['num']
    secondary_repeat = 0 if remainder == 0 else math.floor(remainder / 2)
    main_repeat = params['num'] - remainder - (1 if main_stitch_count > 0 else 0)
    extra_stitches = (
        params['count']
        - (params['num'] * offset)
        - ((secondary_repeat * secondary_stitch_count) * 2)
        - (main_repeat * main_stitch_count)
    )
    extra_stitches_start = math.ceil(extra_stitches / 2)
    extra_stitches_end = math.floor(extra_stitches / 2)

    # Add extra stitches at the start
    if extra_stitches_start > 0:
        stitch_params['count'] = extra_stitches_start
        nodes += Utils.evaluate_action_node(stitch_action, stitch_params)

    # Add first repeat
    if secondary_repeat > 0:
        # Evaluate stitch action
        stitch_params['count'] = secondary_stitch_count
        stitch_nodes = Utils.evaluate_action_node(stitch_action, stitch_params)

        if secondary_repeat > 1:
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(secondary_repeat))

            for n in make_nodes:
                repeat_element.appendChild(n)

            for n in stitch_nodes:
                repeat_element.appendChild(n)

            nodes += [repeat_element.cloneNode(deep=True)]
        else:
            nodes += copy.deepcopy(make_nodes)
            nodes += copy.deepcopy(stitch_nodes)

    # Add main repeat
    if main_repeat > 0:
        # Evaluate stitch action
        stitch_params['count'] = main_stitch_count
        stitch_nodes = Utils.evaluate_action_node(stitch_action, stitch_params)

        if main_repeat > 1:
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(main_repeat))

            for n in make_nodes:
                repeat_element.appendChild(n)

            if main_stitch_count > 0:
                for n in stitch_nodes:
                    repeat_element.appendChild(n)

            nodes += [repeat_element.cloneNode(deep=True)]
        else:
            nodes += copy.deepcopy(make_nodes)

            if main_stitch_count > 0:
                nodes += copy.deepcopy(stitch_nodes)

    # Add final repeat
    if secondary_repeat > 0:
        # Evaluate stitch action
        stitch_params['count'] = secondary_stitch_count
        stitch_nodes = Utils.evaluate_action_node(stitch_action, stitch_params)

        if secondary_repeat > 1:
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(secondary_repeat))

            for n in make_nodes:
                repeat_element.appendChild(n)

            for n in stitch_nodes:
                repeat_element.appendChild(n)

            nodes += [repeat_element.cloneNode(deep=True)]
        else:
            nodes += copy.deepcopy(make_nodes)
            nodes += copy.deepcopy(stitch_nodes)

    # Add extra stitches at the end
    if extra_stitches_end > 0:
        # Evaluate stitch action
        stitch_params['count'] = extra_stitches_end
        stitch_nodes = Utils.evaluate_action_node(stitch_action, stitch_params)

        nodes += copy.deepcopy(make_nodes)
        nodes += copy.deepcopy(stitch_nodes)

    return nodes


def __even_round(opaf_doc, params, offset=0):
    nodes = []
    doc = xml.dom.minidom.Document()

    # Get actions from document
    make_action = opaf_doc.get_opaf_action(params['action'])
    stitch_action = opaf_doc.get_opaf_action(params['stitch'])

    # Create temp parameters to use for action evaluation
    make_params = make_action.params.copy()
    stitch_params = stitch_action.params.copy()

    if 'color' in params:
        make_params['color'] = params['color']
        stitch_params['color'] = params['color']

    make_nodes = Utils.evaluate_action_node(make_action, make_params)

    # Calculate knit count
    main_stitch_count = math.floor(params['count'] / params['num']) - offset
    secondary_stitch_count = math.ceil(params['count'] / params['num']) - offset
    remainder = params['count'] % params['num']
    first_repeat = 0 if remainder == 0 else math.ceil(remainder / 2)
    main_repeat = params['num'] - remainder
    last_repeat = 0 if remainder == 0 else math.floor(remainder / 2)

    # Add first repeat
    if first_repeat > 0:
        # Evaluate stitch action
        stitch_params['count'] = secondary_stitch_count
        stitch_nodes = Utils.evaluate_action_node(stitch_action, stitch_params)

        if first_repeat > 1:
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(first_repeat))

            for n in stitch_nodes:
                repeat_element.appendChild(n)

            for n in make_nodes:
                repeat_element.appendChild(n)

            nodes += [repeat_element.cloneNode(deep=True)]
        else:
            nodes += copy.deepcopy(stitch_nodes)
            nodes += copy.deepcopy(make_nodes)

    # Add main repeat
    if main_repeat > 0:
        # Evaluate stitch action
        stitch_params['count'] = main_stitch_count
        stitch_nodes = Utils.evaluate_action_node(stitch_action, stitch_params)

        if main_repeat > 1:
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(main_repeat))

            if main_stitch_count > 0:
                for n in stitch_nodes:
                    repeat_element.appendChild(n)

            for n in make_nodes:
                repeat_element.appendChild(n)

            nodes += [repeat_element.cloneNode(deep=True)]
        else:
            if main_stitch_count > 0:
                nodes += copy.deepcopy(stitch_nodes)

            nodes += copy.deepcopy(make_nodes)

    # Add last repeat
    if last_repeat > 0:
        # Evaluate stitch action
        stitch_params['count'] = secondary_stitch_count
        stitch_nodes = Utils.evaluate_action_node(stitch_action, stitch_params)

        if last_repeat > 1:
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(last_repeat))

            for n in stitch_nodes:
                repeat_element.appendChild(n)

            for n in make_nodes:
                repeat_element.appendChild(n)

            nodes += [repeat_element.cloneNode(deep=True)]
        else:
            nodes += copy.deepcopy(stitch_nodes)
            nodes += copy.deepcopy(make_nodes)

    return nodes


def increase_even_row(opaf_doc, params):
    supported_stitches = ["knit", "purl"]
    supported_actions = ["make_one", "make_one_purl", "yarn_over"]

    if 'count' not in params:
        raise AttributeError(
            "opaf helper attribute 'count' is not defined"
        )

    if 'increase' not in params:
        raise AttributeError(
            "opaf helper attribute 'increase' is not defined"
        )

    params['num'] = params['increase']

    if 'stitch' in params:
        if not params['stitch'] in supported_stitches:
            raise AttributeError(
                "stitch with name '"
                + params['stitch']
                + "' is not supported"
            )
    else:
        params['stitch'] = supported_stitches[0]

    if 'action' in params:
        if not params['action'] in supported_actions:
            raise AttributeError(
                "action with name '"
                + params['action']
                + "' is not supported"
            )
    else:
        params['action'] = supported_actions[0]

    nodes = __even_row(opaf_doc, params)

    return nodes


def decrease_even_row(opaf_doc, params):
    supported_stitches = ["knit", "purl"]
    supported_actions = ["knit_together", "purl_together", "slip_knit"]

    if 'count' not in params:
        raise AttributeError(
            "opaf helper attribute 'count' is not defined"
        )

    if 'decrease' not in params:
        raise AttributeError(
            "opaf helper attribute 'decrease' is not defined"
        )

    params['num'] = params['decrease']

    if 'stitch' in params:
        if not params['stitch'] in supported_stitches:
            raise AttributeError(
                "stitch with name '"
                + params['stitch']
                + "' is not supported"
            )
    else:
        params['stitch'] = supported_stitches[0]

    if 'action' in params:
        if not params['action'] in supported_actions:
            raise AttributeError(
                "action with name '"
                + params['action']
                + "' is not supported"
            )
    else:
        params['action'] = supported_actions[0]

    nodes = __even_row(opaf_doc, params, offset=2)

    return nodes


def increase_even_round(opaf_doc, params):
    supported_stitches = ["knit", "purl"]
    supported_actions = ["make_one", "make_one_purl", "yarn_over"]

    if 'count' not in params:
        raise AttributeError(
            "opaf helper attribute 'count' is not defined"
        )

    if 'increase' not in params:
        raise AttributeError(
            "opaf helper attribute 'increase' is not defined"
        )

    params['num'] = params['increase']

    if 'stitch' in params:
        if not params['stitch'] in supported_stitches:
            raise AttributeError(
                "stitch with name '"
                + params['stitch']
                + "' is not supported"
            )
    else:
        params['stitch'] = supported_stitches[0]

    if 'action' in params:
        if not params['action'] in supported_actions:
            raise AttributeError(
                "action with name '"
                + params['action']
                + "' is not supported"
            )
    else:
        params['action'] = supported_actions[0]

    nodes = __even_round(opaf_doc, params)

    return nodes


def decrease_even_round(opaf_doc, params):
    supported_stitches = ["knit", "purl"]
    supported_actions = ["knit_together", "purl_together", "slip_knit"]

    if 'count' not in params:
        raise AttributeError(
            "opaf helper attribute 'count' is not defined"
        )

    if 'decrease' not in params:
        raise AttributeError(
            "opaf helper attribute 'decrease' is not defined"
        )

    params['num'] = params['decrease']

    if 'stitch' in params:
        if not params['stitch'] in supported_stitches:
            raise AttributeError(
                "stitch with name '"
                + params['stitch']
                + "' is not supported"
            )
    else:
        params['stitch'] = supported_stitches[0]

    if 'action' in params:
        if not params['action'] in supported_actions:
            raise AttributeError(
                "action with name '"
                + params['action']
                + "' is not supported"
            )
    else:
        params['action'] = supported_actions[0]

    nodes = __even_round(opaf_doc, params, offset=2)

    return nodes
