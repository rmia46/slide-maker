#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

// Mini Project: Grammar-Driven Recursive Descent Evaluator in C
// Grammar:
//   Expr   -> Term   { ('+' | '-') Term }
//   Term   -> Factor { ('*' | '/') Factor }
//   Factor -> NUMBER | '(' Expr ')'

const char *src;

void skip_whitespace() {
    while (*src && isspace(*src)) src++;
}

int parse_expr();

int parse_factor() {
    skip_whitespace();
    if (*src == '(') {
        src++; // consume '('
        int val = parse_expr();
        skip_whitespace();
        if (*src == ')') src++; // consume ')'
        return val;
    }
    int val = 0;
    while (*src && isdigit(*src)) {
        val = val * 10 + (*src - '0');
        src++;
    }
    return val;
}

int parse_term() {
    int val = parse_factor();
    while (1) {
        skip_whitespace();
        if (*src == '*') {
            src++;
            val *= parse_factor();
        } else if (*src == '/') {
            src++;
            val /= parse_factor();
        } else {
            break;
        }
    }
    return val;
}

int parse_expr() {
    int val = parse_term();
    while (1) {
        skip_whitespace();
        if (*src == '+') {
            src++;
            val += parse_term();
        } else if (*src == '-') {
            src++;
            val -= parse_term();
        } else {
            break;
        }
    }
    return val;
}

int main() {
    const char *expr = "3 + 4 * 5";
    src = expr;
    printf("Evaluating: '%s' = %d\n", expr, parse_expr());

    const char *expr2 = "(3 + 4) * 5";
    src = expr2;
    printf("Evaluating: '%s' = %d\n", expr2, parse_expr());
    return 0;
}
