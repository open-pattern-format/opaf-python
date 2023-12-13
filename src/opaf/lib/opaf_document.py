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

import xml.etree.ElementTree as ET

from math import *


class OPAFDocument:
    def __init__(self):
        # OPAF objects
        self.unique_id = None
        self.name = ""
        self.version = None
        self.opaf_namespace = None
        self.pkg_version = None
        self.opaf_values = []
        self.opaf_blocks = []
        self.opaf_actions = []
        self.opaf_components = []

    #### Public Functions ###
    
    def set_name(self, value):
        self.name = value

    def set_version(self, value):
        self.version = value

    def set_unique_id(self, value):
        self.unique_id = value

    def set_pkg_version(self, value):
        self.pkg_version = value

    def set_opaf_namespace(self, value):
        self.opaf_namespace = value

    def add_opaf_value(self, value):
        self.opaf_values.append(value)

    def add_opaf_block(self, block):
        # Check for duplicates
        for b in self.opaf_blocks:
            if b.name == block.name:
                raise Exception("Block with name '" + block.name + "' already exists")

        self.opaf_blocks.append(block)

    def add_opaf_action(self, action):
        # Check for duplicates
        for a in self.opaf_actions:
            if a.name == action.name:
                raise Exception("Action with name '" + action.name + "' already exists")

        self.opaf_actions.append(action)

    def add_opaf_component(self, component):
        self.opaf_components.append(component)

    def get_opaf_action(self, name):
        for a in self.opaf_actions:
            if a.name == name:
                return a

        raise Exception("Action with name '" + name + "' not found")

    def get_opaf_block(self, name):
        for b in self.opaf_blocks:
            if b.name == name:
                return b

        raise Exception("Block with name '" + name + "' not found")
