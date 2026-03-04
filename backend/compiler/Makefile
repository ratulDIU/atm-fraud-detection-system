all:
	flex lexer.l
	bison -d parser.y
	gcc lex.yy.c parser.tab.c fraud_logic.c runner.c -o fraud

run:
	./fraud