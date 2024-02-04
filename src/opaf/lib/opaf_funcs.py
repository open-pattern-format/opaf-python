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

import builtins
import math


@staticmethod
def round(num):
    return builtins.round(num)


@staticmethod
def floor(num):
    return math.floor(num)


@staticmethod
def ceil(num):
    return math.ceil(num)


@staticmethod
def less(num, test):
    return num < test


@staticmethod
def greater(num, test):
    return num > test


@staticmethod
def equals(val, values):
    if isinstance(values, list):
        for v in values:
            if val == v:
                return True

    return val == values


@staticmethod
def not_equals(val, values):
    return not equals(val, values)


@staticmethod
def _and_(val1, val2):
    return (val1 and val2)


@staticmethod
def _or_(val1, val2):
    return (val1 or val2)


@staticmethod
def _not_(val):
    return not val
