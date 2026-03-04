#include <stdio.h>
#include <string.h>

int account_number = 0;
int withdraw_count = 0;
int total_amount = 0;
int location_change = 0;
int time_interval = 0;

char first_location[50] = "";
char current_location[50] = "";

void update_location(char *loc){

    if(strlen(first_location) == 0){
        strcpy(first_location, loc);
    }
    else{
        strcpy(current_location, loc);

        if(strcmp(first_location, current_location) != 0){
            location_change = 1;
        }
    }
}

void detect_fraud(){

    int risk_score = 0;

    if(withdraw_count >= 3)
        risk_score += 3;

    if(total_amount > 40000)
        risk_score += 3;

    if(location_change)
        risk_score += 3;

    if(time_interval <= 5)
        risk_score += 2;

    char *level;
    char *action;

    if(risk_score <= 3){
        level = "LOW";
        action = "WARNING";
    }
    else if(risk_score <= 6){
        level = "MEDIUM";
        action = "TEMPORARY BLOCK";
    }
    else{
        level = "HIGH";
        action = "PERMANENT BLOCK";
    }

    printf("\n----- Fraud Analysis Result -----\n");

    printf("Account: %d\n", account_number);
    printf("Withdraw Count: %d\n", withdraw_count);
    printf("Total Amount: %d\n", total_amount);

    printf("Risk Score: %d\n", risk_score);
    printf("Risk Level: %s\n", level);
    printf("Action: %s\n", action);
}