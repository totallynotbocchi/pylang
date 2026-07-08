from pprint import pprint

import src.lexer as lx


def main():
    lexer = lx.Lexer(source="x+=2")
    pprint(lexer.get_tokens())

    for err in lexer.errors:
        print(err)


if __name__ == "__main__":
    main()
