# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, print_function, unicode_literals

import collections
import itertools
from decimal import Decimal

import pytablewriter as ptw
import pytest
import toml
from dateutil.parser import parse

from ._common import print_test_result
from .data import float_header_list, float_value_matrix, header_list, value_matrix


Data = collections.namedtuple("Data", "table_name header value expected")

normal_test_data_list = [
    Data(
        table_name="normal",
        header=header_list,
        value=value_matrix,
        expected="""[[normal]]
a = 1
c = "a"
b = 123.1
e = 1
dd = 1
[[normal]]
a = 2
c = "bb"
b = 2.2
e = 2.2
dd = 2.2
[[normal]]
a = 3
c = "ccc"
b = 3.3
e = "cccc"
dd = 3
""",
    ),
    Data(
        table_name="sparse",
        header=header_list,
        value=[
            ["1", "", "a", "1", None],
            [None, 2.2, None, "2.2", 2.2],
            [None, None, None, None, None],
            [3, 3.3, "ccc", None, "cccc"],
            [None, None, None, None, None],
        ],
        expected="""[[sparse]]
a = 1
c = "a"
b = ""
dd = 1
[[sparse]]
dd = 2.2
b = 2.2
e = 2.2
[[sparse]]
a = 3
c = "ccc"
b = 3.3
e = "cccc"
""",
    ),
    Data(
        table_name="symbols",
        header=["a!0", "a#1", "a.2$", "a_%3", "a-&4"],
        value=[["a?b", "c   d", "e+f", "g=h", "i*j"], [1, 2.0, 3.3, Decimal("4.4"), ""]],
        expected="""[[symbols]]
"a-&4" = "i*j"
"a#1" = "c   d"
"a_%3" = "g=h"
"a!0" = "a?b"
"a.2$" = "e+f"
[[symbols]]
"a-&4" = ""
"a#1" = 2
"a_%3" = 4.4
"a!0" = 1
"a.2$" = 3.3
""",
    ),
    Data(
        table_name="mixtype",
        header=["int", "float", "bool", "datetime"],
        value=[
            [0, 2.2, True, parse("2017-01-02T03:04:05")],
            [-1, Decimal("4.4"), False, parse("2022-01-01T00:00:00")],
        ],
        expected="""[[mixtype]]
float = 2.2
datetime = 2017-01-02T03:04:05
int = 0
bool = true
[[mixtype]]
float = 4.4
datetime = 2022-01-01T00:00:00
int = -1
bool = false
""",
    ),
    Data(
        table_name="float",
        header=float_header_list,
        value=float_value_matrix,
        expected="""[[float]]
a = 0.01
b = 0.00125
c = 0
[[float]]
a = 1
b = 99.9
c = 0.01
[[float]]
a = 1.2
b = 999999.123
c = 0.001

""",
    ),
]

exception_test_data_list = [
    Data(table_name="dummy", header=header, value=value, expected=ptw.EmptyTableDataError)
    for header, value in itertools.product([None, [], ""], [None, [], ""])
] + [
    Data(table_name="empty_header", header=None, value=value_matrix, expected=ptw.EmptyHeaderError),
    Data(table_name=None, header=header_list, value=value_matrix, expected=ptw.EmptyTableNameError),
]

table_writer_class = ptw.TomlTableWriter


class Test_TomlTableWriter_write_new_line(object):
    def test_normal(self, capsys):
        writer = table_writer_class()
        writer.write_null_line()

        out, _err = capsys.readouterr()
        assert out == "\n"


class Test_TomlTableWriter_write_table(object):
    @pytest.mark.parametrize(
        ["table_name", "header", "value", "expected"],
        [
            [data.table_name, data.header, data.value, data.expected]
            for data in normal_test_data_list
        ],
    )
    def test_normal(self, capsys, table_name, header, value, expected):
        writer = table_writer_class()
        writer.table_name = table_name
        writer.header_list = header
        writer.value_matrix = value
        writer.write_table()

        out, err = capsys.readouterr()
        print_test_result(expected=expected, actual=out, error=err)

        assert toml.loads(out) == toml.loads(expected)

    @pytest.mark.parametrize(
        ["table_name", "header", "value", "expected"],
        [
            [data.table_name, data.header, data.value, data.expected]
            for data in exception_test_data_list
        ],
    )
    def test_exception(self, capsys, table_name, header, value, expected):
        writer = table_writer_class()
        writer.table_name = table_name
        writer.header_list = header
        writer.value_matrix = value

        with pytest.raises(expected):
            writer.write_table()
