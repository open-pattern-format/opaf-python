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


def parse_uri(uri, dirname):
    result = ""
    split_str=uri.split("://")

    if len(split_str) != 2:
        return result

    # Get absolute path
    if split_str[0] == "file":
        if (not os.path.isabs(split_str[1])):
            split_str[1] = os.path.join(dirname,split_str[1])
        if os.path.isfile(split_str[1]):
            result = os.path.abspath(split_str[1])

    return result

def str_to_num(str):
    try:
        return int(str)
    except ValueError:
        pass

    try:
        return float(str)
    except ValueError:
        return str
