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
    # returh a absolute path.
    # current_dirname is needed for 'file://'
    result = ""
    splited_str=uri.split("://")
    if len(splited_str)!=2:
        return result
    #get absolute path according to uri
    if splited_str[0] == "file":
        #to absolute path
        if(not os.path.isabs(splited_str[1])):
            splited_str[1]=os.path.join(dirname,splited_str[1])
        if os.path.isfile(splited_str[1]):
            result = os.path.abspath(splited_str[1])

    return result

def str2num(str):
    try:
        return int(str)
    except ValueError:
        pass

    try:
        return float(str)
    except ValueError:
        return str
