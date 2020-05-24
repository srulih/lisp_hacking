package listinterpreter

import "fmt"
import "testing"

func TestLexer(t *testing.T) {
	program := "(if (= 2 2) 23 42)"

	lexer := Lexer{}
	lexer.InstallProgram(program)
	lexer.Lex()
	fmt.Println("------------------")

	fmt.Println(lexer.Error)
	if err := lexer.Error; err != nil {
		fmt.Println(err)
	}

	for _, t := range lexer.Tokens {
		fmt.Println(t)
	}
}
