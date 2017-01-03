# -*- coding: cp1252 -*-
# Fabricio Paes Ferreira

import _lexer_ as lexer
import _parser_ as parser
import numpy as np
import csv

if __name__ == "__main__":
    with open("code.txt", "rb") as f:
        code = f.read()

    tokens = lexer.lexer(code)         # An�lise L�xica do arquivo code.txt que gera uma lista de tokens
    print np.array(tokens)
    parser.parser(tokens)              # An�lise Sint�tica da sa�da da an�lise l�xica (lista de tokens)
    for i in lexer.symbolTable: print i
        

