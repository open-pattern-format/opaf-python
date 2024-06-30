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


class OPAFDocument:
    def __init__(self):
        # OPAF objects
        self.unique_id = None
        self.name = ""
        self.version = None
        self.opaf_namespace = None
        self.pkg_version = None
        self.opaf_configs = []
        self.opaf_values = []
        self.opaf_colors = []
        self.opaf_images = []
        self.opaf_charts = []
        self.opaf_blocks = []
        self.opaf_actions = []
        self.opaf_components = []
        self.opaf_metadata = None

    def set_name(self, value):
        self.name = value.strip()

    def set_version(self, value):
        self.version = value

    def set_unique_id(self, value):
        self.unique_id = value

    def set_pkg_version(self, value):
        self.pkg_version = value

    def set_opaf_namespace(self, value):
        self.opaf_namespace = value

    def add_opaf_config(self, value):
        self.opaf_configs.append(value)

    def add_opaf_value(self, value):
        self.opaf_values.append(value)

    def add_opaf_image(self, image):
        # Check for duplicates
        for i in self.opaf_images:
            if i.name == image.name:
                raise Exception("Image with name '" + image.name + "' already exists")

        self.opaf_images.append(image)

    def add_opaf_chart(self, chart):
        # Check for duplicates
        for c in self.opaf_charts:
            if c.name == chart.name:
                raise Exception("Chart with name '" + chart.name + "' already exists")

        self.opaf_charts.append(chart)

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

    def add_opaf_color(self, color):
        # Check for duplicates
        for c in self.opaf_colors:
            if c.name == color.name:
                raise Exception("Color with name '" + color.name + "' is already defined")

        self.opaf_colors.append(color)

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

    def get_opaf_chart(self, name):
        for c in self.opaf_charts:
            if c.name == name:
                return c

        raise Exception("Chart with name '" + name + "' not found")

    def get_opaf_color(self, name):
        for c in self.opaf_colors:
            if c.name == name:
                return c

        raise Exception("Color with name '" + name + "' not found")

    def get_opaf_colors(self):
        colors = {}

        for c in self.opaf_colors:
            colors[c.name] = c.value

        return colors

    def get_opaf_image(self, name):
        for i in self.opaf_images:
            if i.name == name:
                return i

        raise Exception("Image with name '" + name + "' not found")

    def add_opaf_metadata(self, metadata):
        if self.opaf_metadata:
            self.opaf_metadata.elements += metadata.elements
        else:
            self.opaf_metadata = metadata
