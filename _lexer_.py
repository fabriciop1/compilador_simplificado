# -*- coding: cp1252 -*-
# Fabricio Paes Ferreira

import re
import numpy as np

symbolTable = []

def lexer(code):
    
    keywords = {"if", "else", "while", "print", "int", "main", "boolean", "return", "break", "continue", "def", "void", "TRUE", "FALSE"} # Palavras Reservadas

    token_pattern = r"""  
        (?P<IDENTIFIER>    [a-zA-Z_][a-zA-Z0-9_]*   )
    |   (?P<INTEGER>       [0-9]+                   )
    |   (?P<END>           [;]                      )
    |   (?P<OPEN_BR>       [{]                      )
    |   (?P<CLOSE_BR>      [}]                      )
    |   (?P<OPEN_PAR>      [(]                      )
    |   (?P<CLOSE_PAR>     [)]                      )
    |   (?P<NEWLINE>       [\n]                     )
    |   (?P<WHITE>         [ \t\r]                  )
    |   (?P<ARITHMETIC>    [+\-*\/]                 )
    |   (?P<RELATIONAL>    (<=?|>=?|==|!=)          )
    |   (?P<ATT>           [=]                      )
    |   (?P<MARKS>         ["]                      )
    |   (?P<COMMA>         [,]                      )
    |   (?P<ERROR>         .                        )
    """

    token_re = re.compile(token_pattern, re.VERBOSE)

    scope = 0
    position = 0
    line = 1
    tokens = []             # Lista de tokens
    count_id = 0
    match = token_re.match(code, position)
    
    while match != None:  
        token_name = match.lastgroup
        lexeme = match.group(token_name)
        position = match.end()
        if (token_name == "OPEN_BR"):
            scope += 1
        if (token_name == "CLOSE_BR"):
            scope -= 1
        if (token_name == "ERROR"):
            print "ERROR ON LINE ", line, ". CHARACTER ", lexeme," NOT RECOGNIZED."
            sys.exit()
        if (token_name == "NEWLINE"):
            line += 1
        if (token_name == "IDENTIFIER"):
            if lexeme in keywords:
                token_name = lexeme
                if token_name == "main":
                    symbolTable.append([count_id, "main", "main", "", "", "", "", True, True])
            else:
                symbolTable.append([count_id, lexeme, token_name, "", "", "", scope, False, False]) # ID - Lexema - Token - Categoria - Tipo - Valor - Escopo - Declarado? - Inicializado?
        if (token_name != "WHITE" and token_name != "NEWLINE"):
            if token_name == "IDENTIFIER":
                tokens.append([token_name, line, count_id])
                count_id += 1
            elif token_name == "INTEGER":
                tokens.append([token_name, line, count_id])
                symbolTable.append([count_id, lexeme, token_name, "", "", "", scope, True, True]) # ID - Lexema - Token - Categoria - Tipo - Valor - Escopo - Declarado? - Inicializado?
                count_id += 1
            elif token_name == "RELATIONAL":
                tokens.append([token_name, line, lexeme])
            elif token_name == "main":
                tokens.append([token_name, line, count_id])
                count_id += 1
            else:
                tokens.append([token_name, line])
        
        match = token_re.match(code, position)
        
    return tokens
