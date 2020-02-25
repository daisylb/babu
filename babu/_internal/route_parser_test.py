from .route_parser import parser

def test_simple():
    res = parser.parse("/a{b}/c{string:d.Foo}")
    print(res.pretty())
    assert False