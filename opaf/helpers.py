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


def __increase_even_round(count, num, colour, stitch_type, action_type):
    return __even_round(count, num, colour, stitch_type, action_type)

def __decrease_even_round(count, num, colour, stitch_type, action_type):
    return __even_round(count, num, colour, stitch_type, action_type, 2)

def __even_round(count, num, colour, stitch_type, action_type, offset=0):
    # Calculate knit count
    stitch_count = math.ceil(count / num) - offset
    remainder = count % num
    first_repeat = 0 if remainder == 0 else math.ceil(remainder / 2)
    main_repeat = num - (count % num)
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


def increase_even_round(node):
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

    xml = __increase_even_round(count, increase, colour, "knit", "make_one")

    return xml

def increase_even_purl_round(node):
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

    xml = __increase_even_round(count, increase, colour, "purl", "make_one_purl")

    return xml

def decrease_even_round(node):
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

    xml = __decrease_even_round(count, decrease, colour, "knit", "knit_together")
    
    return xml

def decrease_even_purl_round(node):
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

    xml = __decrease_even_round(count, decrease, colour, "purl", "purl_together")

    return xml