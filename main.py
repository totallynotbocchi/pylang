from pprint import pprint

from src.lexer import Lexer
from src.parser import Parser


def main():
    # lex code
    lexer = Lexer(source="(a + b)*c")

    # parse code
    parser = Parser(lexer.get_tokens())
    pprint(parser.get_ast())


if __name__ == "__main__":
    main()
