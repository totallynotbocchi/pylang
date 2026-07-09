from pprint import pprint

from src.lexer import Lexer
from src.parser import Parser


def main():
    # lex code
    lexer = Lexer(source="if x + 2 then x+3; if x+4 then x+5 end end")

    # parse code
    parser = Parser(lexer.get_tokens())
    pprint(parser.get_ast())

    for err in parser.errors:
        print(err)


if __name__ == "__main__":
    main()
