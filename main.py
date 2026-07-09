from pprint import pprint

from src.lexer import Lexer
from src.parser import Parser


def main():
    # lex code
    lexer = Lexer(source="if x + 2 then if x + 2 then x+2; x+3 end end")

    # parse code
    parser = Parser(lexer.get_tokens())
    pprint(parser.get_ast())

    for err in parser.errors:
        print(err)


if __name__ == "__main__":
    main()
