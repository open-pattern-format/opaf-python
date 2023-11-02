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

import math
import sys
import xml.dom.minidom


def __increase_even_row(count, num, colour, stitch_type, action_type):
    return __even_row(count, num, colour, stitch_type, action_type)

def __decrease_even_row(count, num, colour, stitch_type, action_type):
    return __even_row(count, num, colour, stitch_type, action_type, 2)

def __even_row(count, num, colour, stitch_type, action_type, offset=0):
    # Calculate knit count
    main_stitch_count = math.ceil(count / num) - offset
    secondary_stitch_count = math.floor(count / num) - offset
    remainder = count % num
    secondary_repeat = 0 if remainder == 0 else math.floor(remainder / 2)
    main_repeat = num - remainder - 1
    extra_stitches = count - (num * offset) - ((secondary_repeat * secondary_stitch_count) * 2) - (main_repeat * main_stitch_count)
    extra_stitches_start = math.ceil(extra_stitches / 2)
    extra_stitches_end = math.floor(extra_stitches / 2)

    # Generate OPAF block
    doc = xml.dom.minidom.Document()
    root_element = doc.createElement("increase_even")
    doc.appendChild(root_element)

    # Add extra stitches at the start
    stitch_element = doc.createElement("opaf_action")
    stitch_element.setAttribute("name", stitch_type)
    stitch_element.setAttribute("count", str(extra_stitches_start))
    stitch_element.setAttribute("colour", colour)
    root_element.appendChild(stitch_element)

    # Add first repeat
    if secondary_repeat > 0:
        # Define elements
        make_element = doc.createElement("opaf_action")
        make_element.setAttribute("name", action_type)
        make_element.setAttribute("colour", colour)
        stitch_element = doc.createElement("opaf_action")
        stitch_element.setAttribute("name", stitch_type)
        stitch_element.setAttribute("count", str(secondary_stitch_count))
        stitch_element.setAttribute("colour", colour)

        if(secondary_repeat > 1):
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(secondary_repeat))
            root_element.appendChild(repeat_element)
            repeat_element.appendChild(make_element)
            repeat_element.appendChild(stitch_element)
        else:
            root_element.appendChild(make_element)
            root_element.appendChild(stitch_element)

    # Add main repeat
    if main_repeat > 0:
        # Define elements
        make_element = doc.createElement("opaf_action")
        make_element.setAttribute("name", action_type)
        make_element.setAttribute("colour", colour)
        stitch_element = doc.createElement("opaf_action")
        stitch_element.setAttribute("name", stitch_type)
        stitch_element.setAttribute("count", str(main_stitch_count))
        stitch_element.setAttribute("colour", colour)

        if(main_repeat > 1):
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(main_repeat))
            root_element.appendChild(repeat_element)
            repeat_element.appendChild(make_element)
            repeat_element.appendChild(stitch_element)
        else:
            root_element.appendChild(make_element)
            root_element.appendChild(stitch_element)

    # Add final repeat
    if secondary_repeat > 0:
        # Define elements
        make_element = doc.createElement("opaf_action")
        make_element.setAttribute("name", action_type)
        make_element.setAttribute("colour", colour)
        stitch_element = doc.createElement("opaf_action")
        stitch_element.setAttribute("name", stitch_type)
        stitch_element.setAttribute("count", str(secondary_stitch_count))
        stitch_element.setAttribute("colour", colour)

        if(secondary_repeat > 1):
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(secondary_repeat))
            root_element.appendChild(repeat_element)
            repeat_element.appendChild(make_element)
            repeat_element.appendChild(stitch_element)
        else:
            root_element.appendChild(make_element)
            root_element.appendChild(stitch_element)

    # Add extra stitches at the end
    make_element = doc.createElement("opaf_action")
    make_element.setAttribute("name", action_type)
    make_element.setAttribute("colour", colour)
    stitch_element = doc.createElement("opaf_action")
    stitch_element.setAttribute("name", stitch_type)
    stitch_element.setAttribute("count", str(extra_stitches_end))
    stitch_element.setAttribute("colour", colour)
    root_element.appendChild(make_element)
    root_element.appendChild(stitch_element)

    return root_element

def __increase_even_round(count, num, colour, stitch_type, action_type):
    return __even_round(count, num, colour, stitch_type, action_type)

def __decrease_even_round(count, num, colour, stitch_type, action_type):
    return __even_round(count, num, colour, stitch_type, action_type, 2)

def __even_round(count, num, colour, stitch_type, action_type, offset=0):
    # Calculate knit count
    stitch_count = math.ceil(count / num) - offset
    remainder = count % num
    first_repeat = 0 if remainder == 0 else math.ceil(remainder / 2)
    main_repeat = num - remainder
    last_repeat = 0 if remainder == 0 else math.floor(remainder / 2)

    # Generate OPAF block
    doc = xml.dom.minidom.Document()
    root_element = doc.createElement("increase_even")
    doc.appendChild(root_element)

    # Add first repeat
    if first_repeat > 0:
        # Define elements
        stitch_element = doc.createElement("opaf_action")
        stitch_element.setAttribute("name", stitch_type)
        stitch_element.setAttribute("count", str(stitch_count))
        stitch_element.setAttribute("colour", colour)
        make_element = doc.createElement("opaf_action")
        make_element.setAttribute("name", action_type)
        make_element.setAttribute("colour", colour)

        if(first_repeat > 1):
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(first_repeat))
            root_element.appendChild(repeat_element)
            repeat_element.appendChild(stitch_element)
            repeat_element.appendChild(make_element)
        else:
            root_element.appendChild(stitch_element)
            root_element.appendChild(make_element)

    # Add main repeat
    if main_repeat > 0:
        # Define elements
        stitch_element = doc.createElement("opaf_action")
        stitch_element.setAttribute("name", stitch_type)
        stitch_element.setAttribute("count", str(stitch_count - 1))
        stitch_element.setAttribute("colour", colour)
        make_element = doc.createElement("opaf_action")
        make_element.setAttribute("name", action_type)
        make_element.setAttribute("colour", colour)

        if(main_repeat > 1):
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(main_repeat))
            root_element.appendChild(repeat_element)
            repeat_element.appendChild(stitch_element)
            repeat_element.appendChild(make_element)
        else:
            root_element.appendChild(stitch_element)
            root_element.appendChild(make_element)

    # Add last repeat
    if last_repeat > 0:
        # Define elements
        stitch_element = doc.createElement("opaf_action")
        stitch_element.setAttribute("name", stitch_type)
        stitch_element.setAttribute("count", str(stitch_count))
        stitch_element.setAttribute("colour", colour)
        make_element = doc.createElement("opaf_action")
        make_element.setAttribute("name", action_type)
        make_element.setAttribute("colour", colour)

        if(last_repeat > 1):
            repeat_element = doc.createElement("repeat")
            repeat_element.setAttribute("count", str(last_repeat))
            root_element.appendChild(repeat_element)
            repeat_element.appendChild(stitch_element)
            repeat_element.appendChild(make_element)
        else:
            root_element.appendChild(stitch_element)
            root_element.appendChild(make_element)
    
    return root_element

#
# Public helpers
#

def increase_even_row(node):
    supported_stitches = ["knit", "purl"]
    supported_actions = ["make_one", "make_one_purl", "yarn_over"]

    if node.hasAttribute("count"):
        count = int(node.getAttribute("count"))
    else:
        raise AttributeError("opaf_helper attribute 'count' is not defined" + ", line %d" % (sys._getframe().f_lineno))

    if node.hasAttribute("increase"):
        increase = int(node.getAttribute("increase"))
    else:
        raise AttributeError("opaf_helper attribute 'increase' is not defined" + ", line %d" % (sys._getframe().f_lineno))

    if node.hasAttribute("colour"):
        colour = node.getAttribute("colour")
    else:
        colour = "main"

    if node.hasAttribute("stitch"):
        stitch = node.getAttribute("stitch")
        if not stitch in supported_stitches:
            raise AttributeError("stitch with name '" + stitch + "' is not supported" + ", line %d" % (sys._getframe().f_lineno))
    else:
        stitch = supported_stitches[0]

    if node.hasAttribute("action"):
        action = node.getAttribute("action")
        if not action in supported_actions:
            raise AttributeError("action with name '" + action + "' is not supported" + ", line %d" % (sys._getframe().f_lineno))
    else:
        action = supported_actions[0]

    xml = __increase_even_row(count, increase, colour, stitch, action)

    return xml

def decrease_even_row(node):
    supported_stitches = ["knit", "purl"]
    supported_actions = ["knit_together", "purl_together", "slip_knit"]

    if node.hasAttribute("count"):
        count = int(node.getAttribute("count"))
    else:
        raise AttributeError("opaf_helper attribute 'count' is not defined" + ", line %d" % (sys._getframe().f_lineno))

    if node.hasAttribute("decrease"):
        decrease = int(node.getAttribute("decrease"))
    else:
        raise AttributeError("opaf_helper attribute 'decrease' is not defined" + ", line %d" % (sys._getframe().f_lineno))

    if node.hasAttribute("colour"):
        colour = node.getAttribute("colour")
    else:
        colour = "main"

    if node.hasAttribute("stitch"):
        stitch = node.getAttribute("stitch")
        if not stitch in supported_stitches:
            raise AttributeError("stitch with name '" + stitch + "' is not supported" + ", line %d" % (sys._getframe().f_lineno))
    else:
        stitch = supported_stitches[0]

    if node.hasAttribute("action"):
        action = node.getAttribute("action")
        if not action in supported_actions:
            raise AttributeError("action with name '" + action + "' is not supported" + ", line %d" % (sys._getframe().f_lineno))
    else:
        action = supported_actions[0]

    xml = __decrease_even_row(count, decrease, colour, stitch, action)

    return xml

def increase_even_round(node):
    supported_stitches = ["knit", "purl"]
    supported_actions = ["make_one", "make_one_purl", "yarn_over"]

    if node.hasAttribute("count"):
        count = int(node.getAttribute("count"))
    else:
        raise AttributeError("opaf_helper attribute 'count' is not defined" + ", line %d" % (sys._getframe().f_lineno))

    if node.hasAttribute("increase"):
        increase = int(node.getAttribute("increase"))
    else:
        raise AttributeError("opaf_helper attribute 'increase' is not defined" + ", line %d" % (sys._getframe().f_lineno))

    if node.hasAttribute("colour"):
        colour = node.getAttribute("colour")
    else:
        colour = "main"

    if node.hasAttribute("stitch"):
        stitch = node.getAttribute("stitch")
        if not stitch in supported_stitches:
            raise AttributeError("stitch with name '" + stitch + "' is not supported" + ", line %d" % (sys._getframe().f_lineno))
    else:
        stitch = supported_stitches[0]

    if node.hasAttribute("action"):
        action = node.getAttribute("action")
        if not action in supported_actions:
            raise AttributeError("action with name '" + action + "' is not supported" + ", line %d" % (sys._getframe().f_lineno))
    else:
        action = supported_actions[0]

    xml = __increase_even_round(count, increase, colour, stitch, action)

    return xml

def decrease_even_round(node):
    supported_stitches = ["knit", "purl"]
    supported_actions = ["knit_together", "purl_together", "slip_knit"]

    if node.hasAttribute("count"):
        count = int(node.getAttribute("count"))
    else:
        raise AttributeError("opaf_helper attribute 'count' is not defined" + ", line %d" % (sys._getframe().f_lineno))

    if node.hasAttribute("decrease"):
        decrease = int(node.getAttribute("decrease"))
    else:
        raise AttributeError("opaf_helper attribute 'decrease' is not defined" + ", line %d" % (sys._getframe().f_lineno))

    if node.hasAttribute("colour"):
        colour = node.getAttribute("colour")
    else:
        colour = "main"

    if node.hasAttribute("stitch"):
        stitch = node.getAttribute("stitch")
        if not stitch in supported_stitches:
            raise AttributeError("stitch with name '" + stitch + "' is not supported" + ", line %d" % (sys._getframe().f_lineno))
    else:
        stitch = supported_stitches[0]

    if node.hasAttribute("action"):
        action = node.getAttribute("action")
        if not action in supported_actions:
            raise AttributeError("action with name '" + action + "' is not supported" + ", line %d" % (sys._getframe().f_lineno))
    else:
        action = supported_actions[0]

    xml = __decrease_even_round(count, decrease, colour, stitch, action)

    return xml
