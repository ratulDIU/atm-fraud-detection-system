%{
#include "parser.tab.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
%}

%%

"ACCOUNT"        { return ACCOUNT; }
"LOCATION"       { return LOCATION; }
"WITHDRAW"       { return WITHDRAW; }
"TIME_INTERVAL"  { return TIME_INTERVAL; }
"ANALYZE"        { return ANALYZE; }

[0-9]+ {
    yylval.num = atoi(yytext);
    return NUMBER;
}

[A-Za-z]+ {
    yylval.str = strdup(yytext);
    return CITY;
}

[ \t\n]   ;

.         ;

%%

int yywrap(){
    return 1;
}