package listinterpreter

import "fmt"
import "strconv"
import "unicode/utf8"

type TokenType int

type Token struct {
	Type   TokenType
	Source interface{}
	Line   int
}

type Lexer struct {
	Start      int
	Current    int
	Tokens     []Token
	LineNumber int
	Program    string
	Error      error
}

func CreateLexer() *Lexer {
	return &Lexer{
		Tokens: make([]Token, 0),
	}
}

const (
	LEFT_PAREN TokenType = iota
	RIGHT_PAREN
	DEFINITION
	ADD
	SUBTRACT
	MULTIPLY
	DIVIDE
	EQUAL
	IF
	ELSE
	LAMBDA
	NUMBER
	SYMBOL
	IDENTIFIER
	EOF
)

var keywordMap = map[string]TokenType{
	"define": DEFINITION,
	"if":     IF,
	"else":   ELSE,
	"lambda": LAMBDA,
}

func (l *Lexer) InstallProgram(program string) {
	l.Program = program
}

func (l *Lexer) Lex() {
	var err error

	for !l.isAtEnd() {
		l.Start = l.Current
		err = l.LexToken()
		if err != nil {
			l.Error = err
			break
		}
	}

	if l.Error != nil {
		l.addToken(EOF)
	}
}

func (l *Lexer) LexToken() error {
	r, _ := utf8.DecodeRuneInString(l.Program[l.Current:])
	if r == '(' {
		l.advance()
		l.addToken(LEFT_PAREN)
	} else if r == ')' {
		l.advance()
		l.addToken(RIGHT_PAREN)
	} else if r == '+' {
		l.advance()
		l.addToken(ADD)
	} else if r == '-' {
		l.advance()
		l.addToken(SUBTRACT)
	} else if r == '*' {
		l.advance()
		l.addToken(MULTIPLY)
	} else if r == '/' {
		l.advance()
		l.addToken(DIVIDE)
	} else if r == '=' {
		l.advance()
		l.addToken(EQUAL)
	} else if r == ' ' {
		l.advance()
	} else if r == '\n' {
		l.LineNumber++
		l.advance()
	} else if isDigit(r) {
		l.lexNumber()
	} else if isAlpha(r) {
		l.lexIdentifier()
	} else {
		return fmt.Errorf("cannot identify token %c", r)
	}
	return nil
}

func isDigit(r rune) bool {
	return r >= '0' && r <= '9'
}

func isAlpha(r rune) bool {
	return (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || r == '?'
}

func (l *Lexer) peek() rune {
	r, _ := utf8.DecodeRuneInString(l.Program[l.Current:])
	return r
}

func (l *Lexer) advance() rune {
	r, size := utf8.DecodeRuneInString(l.Program[l.Current:])
	l.Current += size
	return r
}

func (l *Lexer) isAtEnd() bool {
	return l.Current >= len(l.Program)
}

// TODO add support for floating point
func (l *Lexer) lexNumber() {
	for !l.isAtEnd() && isDigit(l.peek()) {
		l.advance()
	}
	l.addToken(NUMBER)
}

func (l *Lexer) lexIdentifier() {
	for !l.isAtEnd() && isAlpha(l.peek()) {
		l.advance()
	}

	source := l.Program[l.Start:l.Current]
	if tt, ok := keywordMap[source]; ok {
		l.addToken(tt)
	} else {
		l.addToken(IDENTIFIER)
	}
}

func (l *Lexer) addToken(tt TokenType) {
	var source interface{}
	source = l.Program[l.Start:l.Current]
	fmt.Printf("%s\n", source.(string))
	if tt == NUMBER {
		source, _ = strconv.Atoi(source.(string))
	}

	l.Tokens = append(l.Tokens, Token{Type: tt, Source: source, Line: l.LineNumber})
}

func main() {
	fmt.Println("vim-go")
}
