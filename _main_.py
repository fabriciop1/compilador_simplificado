# -*- coding: cp1252 -*-
# Fabricio Paes Ferreira

import _lexer_ as lexer
import _parser_ as parser
import numpy as np
import csv

if __name__ == "__main__":
    with open("code.txt", "rb") as f:
        code = f.read()

    tokens = lexer.lexer(code)         # Análise Léxica do arquivo code.txt que gera uma lista de tokens
    print np.array(tokens)
    parser.parser(tokens)              # Análise Sintática da saída da análise léxica (lista de tokens)
    for i in lexer.symbolTable: print i
        

