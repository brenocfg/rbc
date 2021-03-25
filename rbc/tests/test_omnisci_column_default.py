import pytest
from rbc.tests import omnisci_fixture

scalar_types = ["float64", "int64", "float32", "int32", "int16", "int8"]
table_columns_map = dict(
    int64="i8", int32="i4", int16="i2", int8="i1", float64="f8", float32="f4"
)
sql_type_map = dict(
    int64="BIGINT",
    int32="INT",
    int16="SMALLINT",
    int8="TINYINT",
    float64="DOUBLE",
    float32="FLOAT",
)


@pytest.fixture(scope="module")
def omnisci():

    for o in omnisci_fixture(globals(), minimal_version=(5, 5, 5)):
        define(o)
        yield o


def define(omnisci):
    return


typs = (
    ("1", "1"),  # udtf_default_sizer1__cpu_1
    ("1", "1r"),  # udtf_default_sizer1__cpu_1
    ("2", "1a"),  # udtf_default_sizer2__cpu_1
    ("2", "1ar"),  # udtf_default_sizer2__cpu_1
    # ("3", "2"),  # udtf_default_sizer3__cpu_1     # should this one work?
    ("3", "11r"),  # udtf_default_sizer3__cpu_1
    # ("3", "2r"),  # udtf_default_sizer3__cpu_1    # should this one work???
    ("4", "11"),  # udtf_default_sizer4__cpu_1
    ("4", "1r1"),  # udtf_default_sizer4__cpu_1
    ("5", "1a"),  # udtf_default_sizer5__cpu_1
    ("5", "1ra"),  # udtf_default_sizer5__cpu_1
    ("6", "1a1"),  # udtf_default_sizer6__cpu_1
    ("6", "1a1r"),  # udtf_default_sizer6__cpu_1
    ("7", "11a"),  # udtf_default_sizer7__cpu_1
    ("7", "1r1a"),  # udtf_default_sizer7__cpu_1
    ("8", "31a"),  # udtf_default_sizer8__cpu_1
    ("8", "3r1a"),  # udtf_default_sizer8__cpu_1
)


@pytest.mark.parametrize("suffix,kind", typs)
def test_default_sizer(omnisci, suffix, kind):
    omnisci.require_version((5, 5, 5), "Requires omniscidb-internal PR 5403")

    codes = {
        "1": "i4",
        "2": "i4, i4",
        "3": "i4, i4, i4",
        "a": "cast(231 as INT)",
        "b": "132",
        "r": "1",
    }

    table = omnisci.table_name
    fn = f"udtf_default_sizer{suffix}"
    query = f"select * from table({fn}("
    for i, n in enumerate(kind):
        cols = codes[n]
        if str.isdigit(n):
            query += f"cursor(select {cols} from {table})"
        else:
            query += f"{cols}"
        query += ", " if i + 1 < len(kind) else ""
    query += "));"

    _, result = omnisci.sql_execute(query)
    result = list(result)

    r = sum(map(lambda x: int(x) if str.isdigit(x) else ord(x), kind))
    if "r" in kind:
        r -= ord("r")
    assert result == [(1000 + r,)], (result, query)
