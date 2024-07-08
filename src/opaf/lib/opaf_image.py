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
import xml.dom.minidom

from io import BytesIO
from PIL import Image

from opaf.lib import Utils


class OPAFImage:

    __DEFINE_NAME__ = "opaf:define_image"
    __DEFAULT_SIZE__ = 1000

    def __init__(self,
                 name,
                 data):
        self.name = name
        self.data = data

    def to_node(self):
        doc = xml.dom.minidom.Document()
        node = doc.createElement(self.__DEFINE_NAME__)
        node.setAttribute("name", self.name)
        node.setAttribute("data", base64.b64encode(self.data).decode('ascii'))

        return node

    @staticmethod
    def parse(node, dir):
        if not isinstance(node, xml.dom.minidom.Node):
            raise Exception("Unable to parse object of type " + node.__class__)

        if not node.nodeType == xml.dom.Node.ELEMENT_NODE:
            raise Exception("Unexpected node type")

        if not node.nodeName == OPAFImage.__DEFINE_NAME__:
            raise Exception(
                "Expected node with name '"
                + OPAFImage.__DEFINE_NAME__
                + "' and got '"
                + node.nodeName
                + "'"
            )

        # Name
        name = node.getAttribute("name")

        # Size
        size = OPAFImage.__DEFAULT_SIZE__

        if node.hasAttribute("size"):
            size = int(node.getAttribute("size"))

        # URI
        if node.hasAttribute("uri"):
            uri = node.getAttribute("uri")
            img_path = Utils.parse_uri(uri, dir)

            if not img_path:
                raise Exception("Image not found with uri： %s" % uri)

            img = Image.open(img_path)
            img.thumbnail((size, size))

            img_file = BytesIO()

            if img.has_transparency_data:
                img.save(img_file, 'PNG')
            else:
                img.save(img_file, 'JPEG', quality=75)

            data = img_file.getvalue()
        else:
            data = base64.b64decode(node.getAttribute("data"))

        return OPAFImage(name, data)
