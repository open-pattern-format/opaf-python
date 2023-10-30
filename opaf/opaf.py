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

import argparse
import xml.etree.ElementTree as ET
import glob
import logging
import os
import sys
import re
import xml.dom.minidom
from math import *

from opaf import utils, helpers

class OPAFDocument:
    def __init__(self,
                 src_path,
                 expand_repeats=False):
        self.common_opaf_paths = []

        # OPAF objects to parse
        self.opaf_values={}
        self.opaf_block_params={}
        self.opaf_blocks={}
        self.opaf_action_params={}
        self.opaf_actions={}

        # variables for xml info
        self.src_path = src_path
        self.src_dir = os.path.dirname(os.path.abspath(src_path))
        self.src_doc = None
        self.out_doc = None

        # Config variables
        self.expand_repeats = expand_repeats

    #### Private Functions ###

    def __parse_opaf_definition(self, doc):
        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'opaf_define_value':
                    # Check condition
                    condition = True
                    if node.hasAttribute("condition"):
                        condition = self.__replace_value(node.getAttribute("condition"), self.opaf_values)
                    if condition == 'False' or condition == '0':
                        continue

                    name = node.getAttribute("name")
                    self.opaf_values[name] = utils.str_to_num(self.__replace_value(node.getAttribute("value"), self.opaf_values))
                elif node.tagName == 'opaf_define_block':
                    name = node.getAttribute("name")
                    self.opaf_block_params[name] = {}

                    if node.hasAttribute("params"):
                        params = node.getAttribute("params").split(' ')

                        for param in params:
                            if '=' in param:
                                param = param.split('=')
                                self.opaf_block_params[name][param[0]] = param[1]
                            else:
                                self.opaf_block_params[name][param] = ''

                    self.opaf_blocks[name] = node.toxml()
                elif node.tagName == 'opaf_define_action':
                    name = node.getAttribute("name")
                    self.opaf_action_params[name] = {}

                    if node.hasAttribute("params"):
                        params = node.getAttribute("params").split(' ')

                        for param in params:
                            if '=' in param:
                                param = param.split('=')
                                self.opaf_action_params[name][param[0]] = param[1]
                            else:
                                self.opaf_action_params[name][param] = ''

                    self.opaf_actions[name] = node.toxml()

    def __include_opaf_definition(self, doc, dir):
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'opaf_include':
                    uri = node.getAttribute("uri")
                    filepath = utils.parse_uri(uri, dir)
                    if filepath != "":
                        tmp_doc = xml.dom.minidom.parse(filepath)
                        self.__include_opaf_definition(tmp_doc, os.path.dirname(filepath))

                        # Parse opaf from file
                        self.__parse_opaf_definition(tmp_doc)
                    else:
                        raise Exception("Couldn't find opaf_include uri： %s" % uri)
        
    def __remove_opaf_definition(self, doc):
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'opaf_define_value' \
                    or node.tagName == 'opaf_define_block' \
                    or node.tagName == 'opaf_define_action' \
                    or node.tagName == 'opaf_include' \
                    or node.tagName == 'opaf_action' \
                    or node.tagName == 'opaf_block' \
                    or node.tagName == 'opaf_helper':
                    root.removeChild(node)

    def __replace_value(self, xml_str, value_dict):
        pattern = re.compile(r'[$][{](.*?)[}]', re.S)

        def eval_fn(obj):
            try:
                result = eval(obj.group(1), None, value_dict)
            except Exception as e:
                 raise Exception("Failed to evaluate: <%s>" % (obj.group(1)) + ", " + str(e))

            return str(result)

        return re.sub(pattern, eval_fn, xml_str)
            
    def __replace_opaf_block(self,node):
        parent = node.parentNode

        if not node.hasAttribute("name"):
            raise Exception("opaf_block attribute 'name' is not defined" + ", line %d" % (sys._getframe().f_lineno))

        name = node.getAttribute("name")

        # Check name
        if name not in self.opaf_blocks.keys():
            raise Exception("opaf_block<%s> is not defined" % name + ", line %d" % (sys._getframe().f_lineno))

        # Check condition
        condition = True
        if node.hasAttribute("condition"):
            condition = node.getAttribute("condition")
        if condition == 'False' or condition == '0':
            # Remove opaf node
            parent.removeChild(node)
            return

        # Get block info
        xml_str = self.opaf_blocks[name]
        params = {}
        for k, v in self.opaf_block_params[name].items():
            if v == '' and not node.hasAttribute(k):
                raise Exception("<%s> attribute '%s' is not defined" % (name, k) + ", line %d"%(sys._getframe().f_lineno))

            if node.hasAttribute(k):
                params[k] = utils.str_to_num(node.getAttribute(k))
            else:
                params[k] = utils.str_to_num(v)

        # Handle repeats
        repeat = 1
        
        if node.hasAttribute("repeat"):
            repeat = int(float(node.getAttribute("repeat")))

        # Add repeat_total to params
        params['repeat_total'] = repeat

        xml_strs = []

        for i in range(repeat):
            # Add repeat parameter to params
            params['repeat'] = i+1

            # Replace parameters
            try:
                xml_strs.append(self.__replace_value(xml_str, params))
            except Exception as e:
                raise Exception("<%s>" % name + ", line %d"%(sys._getframe().f_lineno) + ", " + str(e))
        
        # Determine if repeats are equal
        if repeat > 1 and len(set(xml_strs)) == 1:
            # Add repeat element and add existing block nodes
            new_doc = xml.dom.minidom.Document()
            root_element = new_doc.createElement("repeat_block")
            new_doc.appendChild(root_element)
            repeat_element = new_doc.createElement("repeat")
            repeat_element.setAttribute("count", str(repeat))
            root_element.appendChild(repeat_element)

            block_node = xml.dom.minidom.parseString(xml_strs[0]).documentElement
            for cc in list(block_node.childNodes):
                n = new_doc.importNode(cc, deep=True)
                repeat_element.appendChild(n)
                        
            # Add to parent document
            for cc in list(new_doc.documentElement.childNodes):
                parent.insertBefore(cc, node)
        else:
            for s in xml_strs:
                new_node = xml.dom.minidom.parseString(s).documentElement
                for cc in list(new_node.childNodes):
                    parent.insertBefore(cc, node)

        # Remove opaf node
        parent.removeChild(node)


    def __replace_opaf_helper(self, node):
        parent = node.parentNode

        if not node.hasAttribute("name"):
            raise Exception("opaf_helper attribute 'name' is not defined" + ", line %d" % (sys._getframe().f_lineno))

        name = node.getAttribute("name")

        # Check action
        if not hasattr(helpers, name):
            raise Exception("opaf_helper<%s> is not defined" % name + ", line %d" % (sys._getframe().f_lineno))

        # Check condition
        condition = True
        if node.hasAttribute("condition"):
            condition = node.getAttribute("condition")
        if condition == 'False' or condition == '0':
            parent.removeChild(node)
            return

        # Get function
        helper = getattr(helpers, name)
        result = helper(node)

        for cc in list(result.childNodes):
            parent.insertBefore(cc, node)

        # Remove opaf node
        parent.removeChild(node)


    def __replace_opaf_action(self, node):
        parent = node.parentNode

        if not node.hasAttribute("name"):
            raise Exception("opaf_action attribute 'name' is not defined" + ", line %d" % (sys._getframe().f_lineno))

        name = node.getAttribute("name")

        # Check action
        if name not in self.opaf_actions.keys():
            raise Exception("opaf_action<%s> is not defined" % name + ", line %d" % (sys._getframe().f_lineno))

        # Check condition
        condition = True
        if node.hasAttribute("condition"):
            condition = node.getAttribute("condition")
        if condition == 'False' or condition == '0':
            parent.removeChild(node)
            return

        # Get action info
        xml_str = self.opaf_actions[name]
        params = {}
        for k, v in self.opaf_action_params[name].items():
            if v == '' and not node.hasAttribute(k):
                raise Exception("<%s> attribute '%s' is not defined" % (name, k) + ", line %d" % (sys._getframe().f_lineno))

            if node.hasAttribute(k):
                params[k] = utils.str_to_num(node.getAttribute(k))
            else:
                params[k] = utils.str_to_num(v)

        # Replace value
        try:
            xml_str = self.__replace_value(xml_str,params)
        except Exception as e:
            raise Exception("<%s>" % name + ", line %d" % (sys._getframe().f_lineno) + ", " + str(e))

        # transform to doc and insert to parent doc
        new_node = xml.dom.minidom.parseString(xml_str).documentElement
        for cc in list(new_node.childNodes):
            parent.insertBefore(cc, node)

        # Remove parent node
        parent.removeChild(node)

    def __expand_repeat(self, node):
        parent = node.parentNode

        if not node.hasAttribute("count"):
            raise Exception("repeat attribute 'count' is not defined" + ", line %d" % (sys._getframe().f_lineno))

        count = int(node.getAttribute("count"))

        for i in range(0, count):
            for child in list(node.childNodes):
                child_clone = child.cloneNode(True)
                parent.insertBefore(child_clone, node)

        # Remove parent node
        parent.removeChild(node)

    def __parse(self):
        # Parse OPAF library
        dir_path = os.path.realpath(os.path.dirname(__file__))
        self.common_opaf_paths = glob.glob(dir_path + "/" + "*.opaf")

        for opaf_path in self.common_opaf_paths:
            self.__parse_opaf_definition(xml.dom.minidom.parse(opaf_path))

        self.__include_opaf_definition(self.src_doc, self.src_dir)

        self.__parse_opaf_definition(self.src_doc)

        self.__remove_opaf_definition(self.src_doc)


    #### Public Functions ###
    
    def set_expand_repeats(self, value):
        self.expand_repeats = value

    def compile(self, custom_values:dict={}):
        # Parse input file
        self.src_doc = xml.dom.minidom.parse(self.src_path)
        self.__parse()

        # Add custom values which should override default values
        opaf_values = self.opaf_values.copy()
        for k in custom_values:
            opaf_values[k] = custom_values[k]

        xml_str = self.src_doc.documentElement.toxml()

        # Replace opaf values
        try:
            xml_str = self.__replace_value(xml_str, opaf_values)
        except Exception as e:
            raise Exception("Failed to process opaf_value, " + "line %d" % (sys._getframe().f_lineno) + ", " + str(e))

        self.out_doc = xml.dom.minidom.parseString(xml_str)

        # Replace blocks
        for _ in range(10):
            nodes = self.out_doc.getElementsByTagName("opaf_block")
            if nodes.length != 0:
                for node in list(nodes):
                    self.__replace_opaf_block(node)
            else:
                break

        # Check depth
        if self.out_doc.getElementsByTagName("opaf_block").length != 0:
            raise Exception("[line %d]"%(sys._getframe().f_lineno)+"recursion level too deep (must<=10).")

        # Replace helpers
        for _ in range(10):
            nodes = self.out_doc.getElementsByTagName("opaf_helper")
            if nodes.length != 0:
                for node in list(nodes):
                    self.__replace_opaf_helper(node)
            else:
                break

        # Check depth
        if self.out_doc.getElementsByTagName("opaf_helper").length != 0:
            raise Exception("Recursion level is too deep (must<=10), " + "line %d" % (sys._getframe().f_lineno))

        # Replace actions
        for _ in range(10):
            nodes = self.out_doc.getElementsByTagName("opaf_action")
            if nodes.length != 0:
                for node in list(nodes):
                    self.__replace_opaf_action(node)
            else:
                break

        # Check depth
        if self.out_doc.getElementsByTagName("opaf_action").length != 0:
            raise Exception("Recursion level is too deep (must<=10), " + "line %d" % (sys._getframe().f_lineno))

        # Expand repeats
        if self.expand_repeats:
            for _ in range(10):
                nodes = self.out_doc.getElementsByTagName("repeat")
                if nodes.length != 0:
                    for node in list(nodes):
                        self.__expand_repeat(node)
                else:
                    break

            # Check depth
            if self.out_doc.getElementsByTagName("repeat").length != 0:
                raise Exception("Recursion level is too deep (must<=10), " + "line %d" % (sys._getframe().f_lineno))

        return self

    def to_file(self, filepath):
        with open(filepath, 'w', encoding='UTF-8') as f:
            f.write(self.to_string())
    
    def to_string(self):
        xml = ET.XML(self.out_doc.toxml())
        ET.indent(xml)
        return ET.tostring(xml, encoding='unicode')


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Open Pattern Format (OPAF) Build Tool')
    parser.add_argument('--input', required=True, help='Source file path (.opaf)')
    parser.add_argument('--output', required=False, help='Output file path (.xml)')
    parser.add_argument('--expand_repeats', default=False, action='store_true', help='Expand repeats when compiling XML')
    parser.add_argument('--log_level', required=False, default='INFO', help='Log level (Default: INFO)')

    args = vars(parser.parse_args())

    input_path = args.get('input')
    output_path = args.get('output')
    expand_repeats = args.get('expand_repeats')
    log_level = getattr(logging, args.get('log_level').upper(), None)

    # Logging
    if not isinstance(log_level, int):
        log_level = logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    # Check file exists
    if not os.path.isfile(input_path):
        logging.error("File not found '" + input_path + "'")
        return -2

    # Check input file extension
    if os.path.splitext(input_path)[1] != '.opaf':
        logging.error("Input file is not an opaf file has the wrong extension")
        return -2

    # Load OPAF instance
    opaf = OPAFDocument(src_path=input_path,
                        expand_repeats=expand_repeats)

    # Compile to XML and write to console or file
    try:
        opaf.compile()

        if output_path:
            opaf.to_file(output_path)
        else:
            print(opaf.to_string())
    except Exception as e:
        logging.error(e)

    return 0
    
if __name__ == '__main__':
    main()