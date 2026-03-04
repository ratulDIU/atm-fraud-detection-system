#include <stdio.h>

extern int yyparse();
extern FILE *yyin;

int main() {

    FILE *file = fopen("../input/transaction.dsl", "r");

    if(!file){
        printf("Input file not found\n");
        return 1;
    }

    yyin = file;

    yyparse();

    fclose(file);

    return 0;
}