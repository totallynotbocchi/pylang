from pprint import pprint

import src.lexer as lx


def main():
    lexer = lx.Lexer(source="1.67.7")
    pprint(lexer.get_tokens())

    for err in lexer.errors:
        print(err)


if __name__ == "__main__":
    main()
