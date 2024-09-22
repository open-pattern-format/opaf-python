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
def mround(num, multiple=1):
    return multiple * builtins.round(num / multiple)


@staticmethod
def floor(num, multiple=1):
    return multiple * math.floor(num / multiple)


@staticmethod
def ceil(num, multiple=1):
    return multiple * math.ceil(num / multiple)


@staticmethod
def less(num, test):
    return num < test


@staticmethod
def greater(num, test):
    return num > test


@staticmethod
def abs(num):
    return builtins.abs(num)


@staticmethod
def equals(val, values):
    if isinstance(val, str):
        val = val.lower()

    if isinstance(values, str):
        values = values.lower()

    if isinstance(values, list):
        for v in values:
            if isinstance(v, str):
                v = v.lower()

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


@staticmethod
def choose(index, values):
    if index < 1:
        raise Exception("Index must be 1 or greater for 'CHOOSE' function")

    if len(values) < index:
        raise Exception(
            "Index "
            + str(index)
            + " is out of range. Expected an index between 1 and "
            + str(len(values))
        )

    return values[index - 1]


@staticmethod
def is_empty(val):
    if val is None:
        return True

    return str(val) == ''


@staticmethod
def odd(val):
    return not even(val)


@staticmethod
def even(val):
    return (val % 2) == 0


@staticmethod
def multiple(val, multiple):
    return (val % multiple) == 0


@staticmethod
def min(val1, val2):
    return builtins.min(val1, val2)


@staticmethod
def max(val1, val2):
    return builtins.max(val1, val2)

@staticmethod
def to_bool(val):
    if isinstance(val, bool):
        return val
    
    if isinstance(val, str):
        return val.strip().lower() in ("yes", "true", "1")
    
    return val == 1
