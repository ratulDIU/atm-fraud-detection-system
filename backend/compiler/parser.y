%{
#include <stdio.h>
#include <stdlib.h>

/* declare lexer function */
int yylex(void);
void yyerror(const char *s);

/* variables from fraud_logic.c */
extern int withdraw_count;
extern int total_amount;
extern int location_change;
extern int time_interval;
extern int account_number;

extern void update_location(char *loc);

void detect_fraud();

%}

%union{
    int num;
    char *str;
}

%token ACCOUNT LOCATION WITHDRAW TIME_INTERVAL ANALYZE
%token <num> NUMBER
%token <str> CITY

%%

program:
    statements ANALYZE { detect_fraud(); }
;

statements:
      statements statement
    | statement
;

statement:
      ACCOUNT NUMBER {
            account_number = $2;
        }

    | LOCATION CITY {
            update_location($2);
        }

    | WITHDRAW NUMBER {
            withdraw_count++;
            total_amount += $2;
        }

    | TIME_INTERVAL NUMBER {
            time_interval = $2;
        }
;

%%

void yyerror(const char *s){
    printf("Syntax Error: %s\n", s);
}