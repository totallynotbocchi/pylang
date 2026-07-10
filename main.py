from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser


def main():
    # lex code
    lexer = Lexer(source="-2;")

    # parse code
    parser = Parser(lexer.get_tokens())

    for err in parser.errors:
        print(err)

    # run code
    ast = parser.get_ast()
    print(ast)

    interpr = Interpreter(ast)
    interpr.execute()


if __name__ == "__main__":
    main()
