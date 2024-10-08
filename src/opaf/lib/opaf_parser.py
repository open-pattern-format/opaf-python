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
import xml.dom.minidom

from xml.parsers.expat import ExpatError
from packaging.version import Version


from opaf.lib import (
    OPAFAction,
    OPAFBlock,
    OPAFChart,
    OPAFColor,
    OPAFConfig,
    OPAFComponent,
    OPAFDocument,
    OPAFImage,
    OPAFMetadata,
    OPAFValue,
    Utils
)


class OPAFParser:
    def __init__(self,
                 src_path):
        self.src_path = os.path.abspath(src_path)

        # Get OPAF namespace
        self.namespace = Utils.get_url("namespace")

        self.opaf_doc = OPAFDocument()
        self.opaf_doc.set_opaf_namespace(self.namespace)

    def __check_doc(self, doc):
        if doc is None:
            raise Exception("Source document is not defined")

        # Check root node
        if not doc.documentElement.tagName == "pattern":
            raise Exception("'pattern' root node not found in OPAF file")

        # Check namespace
        if not doc.documentElement.hasAttribute("xmlns:opaf"):
            raise Exception("OPAF namespace is not declared in pattern attributes")

    def __parse_root(self, doc):
        # Set name
        if doc.documentElement.hasAttribute("name"):
            self.opaf_doc.set_name(doc.documentElement.getAttribute("name"))

        # Check for pattern version
        if doc.documentElement.hasAttribute("version"):
            self.opaf_doc.version = Version(doc.documentElement.getAttribute("version"))

        # Check for spec version
        if doc.documentElement.hasAttribute("spec_version"):
            self.opaf_doc.spec_version = Version(doc.documentElement.getAttribute("spec_version"))

        # Check if this is a packaged file
        if doc.documentElement.hasAttribute("pkg_version"):
            self.opaf_doc.pkg_version = doc.documentElement.getAttribute("pkg_version")

        # Check for unique ID
        if doc.documentElement.hasAttribute("unique_id"):
            self.opaf_doc.set_unique_id(doc.documentElement.getAttribute("unique_id"))

    def __parse_opaf_configs(self, doc):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:define_config")

        for element in elements:
            config = OPAFConfig.parse(element)
            self.opaf_doc.add_opaf_config(config)

    def __parse_opaf_values(self, doc):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:define_value")

        for element in elements:
            value = OPAFValue.parse(element)
            self.opaf_doc.add_opaf_value(value)

    def __parse_opaf_colors(self, doc):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:define_color")

        for element in elements:
            value = OPAFColor.parse(element)
            self.opaf_doc.add_opaf_color(value)

    def __parse_opaf_images(self, doc, dir):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:define_image")

        for element in elements:
            image = OPAFImage.parse(element, dir)
            self.opaf_doc.add_opaf_image(image)

    def __parse_opaf_metadata(self, doc):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:metadata")

        for element in elements:
            metadata = OPAFMetadata.parse(element)
            self.opaf_doc.add_opaf_metadata(metadata)

    def __parse_opaf_actions(self, doc):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:define_action")

        for element in elements:
            action = OPAFAction.parse(element)
            self.opaf_doc.add_opaf_action(action)

    def __parse_opaf_charts(self, doc):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:define_chart")

        for element in elements:
            chart = OPAFChart.parse(element)
            self.opaf_doc.add_opaf_chart(chart)

    def __parse_opaf_blocks(self, doc):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:define_block")

        for element in elements:
            block = OPAFBlock.parse(element)
            self.opaf_doc.add_opaf_block(block)

    def __parse_opaf_components(self, doc):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:component")

        for element in elements:
            component = OPAFComponent.parse(element)
            self.opaf_doc.add_opaf_component(component)

    def __parse_opaf_includes(self, doc, dir):
        root = doc.documentElement
        elements = root.getElementsByTagName("opaf:include")

        for element in elements:
            uri = element.getAttribute("uri")
            file_path = Utils.parse_uri(uri, dir)

            if not file_path:
                raise Exception("Included OPAF file not found with uri： %s" % uri)

            # Recursively parse included OPAF files
            inc_doc = xml.dom.minidom.parse(file_path)
            self.__parse_opaf_includes(inc_doc, os.path.dirname(file_path))
            self.__parse_opaf_colors(inc_doc)
            self.__parse_opaf_configs(inc_doc)
            self.__parse_opaf_values(inc_doc)
            self.__parse_opaf_images(inc_doc, os.path.dirname(file_path))
            self.__parse_opaf_metadata(inc_doc)
            self.__parse_opaf_actions(inc_doc)
            self.__parse_opaf_charts(inc_doc)
            self.__parse_opaf_blocks(inc_doc)

    def parse(self):
        # Parse input file
        try:
            doc = xml.dom.minidom.parse(self.src_path)
        except Exception as e:
            raise ExpatError("OPAF namespace is not declared" + ", " + str(e))

        # Check source document is valid
        self.__check_doc(doc)

        # Parse root pattern element
        self.__parse_root(doc)

        # Parse main file
        self.__parse_opaf_includes(doc, os.path.dirname(self.src_path))
        self.__parse_opaf_colors(doc)
        self.__parse_opaf_configs(doc)
        self.__parse_opaf_values(doc)
        self.__parse_opaf_images(doc, os.path.dirname(self.src_path))
        self.__parse_opaf_metadata(doc)
        self.__parse_opaf_actions(doc)
        self.__parse_opaf_charts(doc)
        self.__parse_opaf_blocks(doc)
        self.__parse_opaf_components(doc)

        return self.opaf_doc
