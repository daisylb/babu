from lark import Lark

GRAMMAR = r"""
start: _block+
_block: text | SLASH | placeholder
text: (TEXT | LITERAL_CURLY_L | LITERAL_CURLY_R)+
slash: SLASH
placeholder: _OPEN (type TYPE_SEP)? dotted_path _CLOSE
type: STRING_TYPE | INT_TYPE | DECIMAL_TYPE | PATH_TYPE
dotted_path: IDENTIFIER ("." IDENTIFIER)*
_OPEN: "{"
_CLOSE: "}"
LITERAL_CURLY_L: "{{"
LITERAL_CURLY_R: "}}"
TEXT: /[^\{\}\/]+/
SLASH: "/"
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
TYPE_SEP: ":"
STRING_TYPE: "string"
INT_TYPE: "int"
DECIMAL_TYPE: "decimal"
PATH_TYPE: "path"
"""

parser = Lark(GRAMMAR)