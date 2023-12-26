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
import base64
import logging
import os

from opaf.lib import OPAFCompiler, OPAFPackager, OPAFParser, Utils


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Open Pattern Format (OPAF) Build Tool')
    parser.add_argument(
        '--input',
        required=True,
        help='Source file path (.opaf)'
    )
    parser.add_argument(
        '--output',
        required=False,
        help='Output directory'
    )
    parser.add_argument(
        '--package',
        default=False,
        action='store_true',
        help='Create distributable OPAF file'
    )
    parser.add_argument(
        '--compile',
        default=False,
        action='store_true',
        help='Compile OPAF package'
    )
    parser.add_argument(
        '--extract_images',
        default=False,
        action='store_true',
        help='Extract images from OPAF package'
    )
    parser.add_argument(
        '--values',
        required=False,
        help='Values to use for compilation'
    )
    parser.add_argument(
        '--colors',
        required=False,
        help='Colors to use for compilation'
    )
    parser.add_argument(
        '--log_level',
        required=False,
        default='INFO',
        help='Log level (Default: INFO)'
    )

    args = vars(parser.parse_args())

    input_path = args.get('input')
    output_path = args.get('output')
    package = args.get('package')
    compile = args.get('compile')
    extract_images = args.get('extract_images')
    values = args.get('values')
    colors = args.get('colors')
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
    if not os.path.splitext(input_path)[1].startswith('.opaf'):
        logging.error("Input file is not an OPAF file or has the wrong extension")
        return -2

    try:
        # Parse OPAF file
        opaf_parser = OPAFParser(input_path)
        opaf_doc = opaf_parser.parse()

        if package:
            if opaf_doc.pkg_version is None:
                opaf_packager = OPAFPackager(opaf_doc)
                opaf_pkg = opaf_packager.package()

                # Write OPAF package file
                pkg_name = (
                    os.path.splitext(input_path)[0]
                    + "_" + opaf_doc.version
                    + ".opafpkg"
                )
                Utils.write_to_file(opaf_pkg, pkg_name)
            else:
                logging.error("Input file is already packaged")
                return -2

        if extract_images:
            if opaf_doc.pkg_version:
                # Check output directory
                if output_path:
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                else:
                    logging.error(
                        "Output path is not specified."
                    )
                    return -2

                # Extract images
                for i in opaf_doc.opaf_images:
                    with open(output_path + '/' + i.name + '.webp', "wb") as img_file:
                        img_file.write(base64.b64decode(i.data))
            else:
                logging.error(
                    "Input file is not an OPAF package file."
                )
                return -2

        if compile:
            if opaf_doc.pkg_version:
                # Parse custom colors
                custom_colors = Utils.parse_arg_list(colors)

                # Parse custom values
                custom_values = Utils.parse_arg_list(values)

                opaf_compiler = OPAFCompiler(
                    opaf_doc,
                    values=custom_values,
                    colors=custom_colors
                )
                compiled_pattern = opaf_compiler.compile()

                # Write XML pattern file
                if output_path:
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)

                    Utils.write_to_file(
                        compiled_pattern,
                        output_path
                        + '/'
                        + opaf_doc.name.strip().replace(' ', '_').lower()
                        + '.xml'
                    )
                else:
                    print(compiled_pattern)
            else:
                logging.error(
                    "Input file is not an OPAF package file. Compilation is not possible."
                )
                return -2

    except Exception as e:
        logging.error(e)

    return 0


if __name__ == '__main__':
    main()
