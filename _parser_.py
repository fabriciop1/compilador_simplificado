# -*- coding: cp1252 -*-
# Fabricio Paes Ferreira

import numpy as np
import csv
from collections import defaultdict
import _lexer_ as lexer
import sys
        
def openTable():                    
    syntax_table = defaultdict(dict)
    
    with open("symbol_table.csv", "rb") as f:
        rows = list(csv.reader(f, delimiter=';'))
        
    rows = np.array(rows)
    
    for i in range (1,len(rows)):
        for j in range (1,len(rows[0])):
            syntax_table[rows[i,0]][rows[0,j]] = rows[i,j]              # Tabela sintática de acordo com arquivo syntax_table.csv
            
    return syntax_table

def getPosition(element):
    for i in range(len(lexer.symbolTable)):
        if(lexer.symbolTable[i][0] == element):
            return i

def addType(tipo, idPos):
    tablePos = getPosition(idPos)
    lexer.symbolTable[tablePos][4] = tipo
    for i in lexer.symbolTable:
        if i[1] == lexer.symbolTable[tablePos][1] and i[6] >= lexer.symbolTable[tablePos][6]:
            i[7] = True
            i[4] = lexer.symbolTable[tablePos][4]

def addValue(value, tablePos):
    for i in lexer.symbolTable:
        if i[1] == lexer.symbolTable[tablePos][1]:
            i[5] = value
            i[8] = True

def printError(errorType, line):
    print "## ERROR ON LINE", line, ":", errorType, "##"
    sys.exit()

def deleteFromTable(tablePos):
    lexer.symbolTable = [x for x in lexer.symbolTable if x not in lexer.symbolTable[0:tablePos] or x[3] == "method"]
    for j in lexer.symbolTable:
        if j[3] != "method":
            j[7] = False
            j[8] = False
            j[4] = ""
            j[5] = ""
            
def isDeclared(tablePos):
    if lexer.symbolTable[tablePos][7] == True:
        return True

def checkScope(tablePos, line):
    for i in lexer.symbolTable:
        if i[1] == lexer.symbolTable[tablePos][1] and i[6] <= lexer.symbolTable[tablePos][6] and i[7] == True:
            printError("VARIABLE ALREADY EXISTS", line)

def checkParameters(table_pos, method, tipo):
    if lexer.symbolTable[table_pos][6] == 0 and not method:
        for j in reversed(lexer.symbolTable):
            if lexer.symbolTable[table_pos][1] == j[1]:
                j[8] = True
            if j[3] == "method":
                j[9].append(tipo)
                return

def checkCall(pos):
    for j in lexer.symbolTable:
        if j[1] == lexer.symbolTable[pos][1] and j[3] == "method" and lexer.symbolTable[pos][7] == False:
            parameters = j[9]
            lexer.symbolTable[pos][7] = True
            lexer.symbolTable[pos][8] = True
            lexer.symbolTable[pos][4] = j[4]
            lexer.symbolTable[pos][5] = j[5]
            lexer.symbolTable[pos][3] = "call"
            return parameters
    return []

def parser(tokens):
    att = False
    method = False
    tablePos = 0
    table_pos = 0
    retorno = False
    relational = False
    arithmetic = False
    printer = False
    arguments = False
    par = []
    
    stack = []
    semantic = []
    tokens.append('$')
    stack.append('$')
    stack.append("<Start>")
    
    table = openTable()                                                    # Abrir a tabela sintatica
    
    for i in range(len(tokens)):
        while list(stack[-1])[0] == '<':                                                        # Se começar com <, então existe uma variavel no topo da pilha
            if table[stack[-1]][tokens[i][0]] != '' and table[stack[-1]][tokens[i][0]] != '$':
                split_arr = table[stack[-1]][tokens[i][0]].split(' ')                           # Separar por espaço todos os tokens que são encontrados na posição (i,j) da tabela
                stack.pop()                                                                     # Retira a variável da pilha
                for string in reversed(split_arr):                                              # Coloca na pilha os tokens da posição (i,j) da tabela em ordem reversa
                    stack.append(string)
            elif table[stack[-1]][tokens[i][0]] == '$':                                         # Caso a posição (i,j) da tabela seja o símbolo $ (vazio), então basta desempilhar o elemento no topo 
                stack.pop()
            else:
                print "## SYNTAX ERROR ON LINE ", tokens[i][1], "##"
                print "Expected: ", stack[-1], " Found: ", tokens[i][0]
                sys.exit()
            #print np.array(stack)    
        if stack[-1] == '$':                                               # Apenas o símbolo $ na pilha acaba a verificação
            stack.pop()
        elif stack[-1] == tokens[i][0]:                                    # Símbolo no topo da pilha é igual ao token lido? Se sim, desempilha e continua a ler o próximo token            
            if stack[-1] == "int" or stack[-1] == "boolean" or stack[-1] == "void":       #
                semantic.append(stack[-1])                                                # Tipagem
            elif stack[-1] == "main":
                table_pos = getPosition(tokens[i][2])
                lexer.symbolTable[table_pos][3] = "method"
                lexer.symbolTable[table_pos][7] = True
                deleteFromTable(table_pos)
            elif stack[-1] == "IDENTIFIER":                                               # Tipagem
                par = checkCall(getPosition(tokens[i][2]))
                if semantic:                                                              # Tipagem
                    tipo = semantic.pop()
                    table_pos = getPosition(tokens[i][2])
                    checkScope(table_pos, tokens[i][1])
                    addType(tipo, tokens[i][2])
                    checkParameters(table_pos, method, tipo)
                if att:                                                                   # a = b
                    table_pos = getPosition(tokens[i][2])
                    if not isDeclared(table_pos):
                        printError("VARIABLE IS NOT DECLARED", tokens[i][1])
                    if lexer.symbolTable[tablePos][4] != lexer.symbolTable[table_pos][4]: # a = b -> Variaveis de tipos diferentes (erro)
                        printError("VARIABLES ARE NOT OF THE SAME TYPE", tokens[i][1])    #
                    addValue(lexer.symbolTable[table_pos][5], tablePos)
                    att = False
                if relational:
                    table_pos = getPosition(tokens[i][2])
                    if not isDeclared(table_pos):
                        printError("VARIABLE IS NOT DECLARED", tokens[i][1])
                    if lexer.symbolTable[tablePos][8] == False or lexer.symbolTable[table_pos][8] == False:
                        printError("VARIABLE NOT INITIALIZED.", tokens[i][1])
                    if lexer.symbolTable[tablePos][4] != lexer.symbolTable[table_pos][4]:
                        printError("VARIABLES ARE NOT OF THE SAME TYPE FOR COMPARISON.", tokens[i][1])
                    relational = False
                if arithmetic:
                    table_pos = getPosition(tokens[i][2])
                    if not isDeclared(table_pos):
                        printError("VARIABLE IS NOT DECLARED", tokens[i][1])
                    if lexer.symbolTable[tablePos][8] == False or lexer.symbolTable[table_pos][8] == False:
                        printError("VARIABLE NOT INITIALIZED.", tokens[i][1])
                    if lexer.symbolTable[tablePos][4] != "int" or lexer.symbolTable[table_pos][4] != "int":
                        printError("ERROR ON ARITHMETIC EXPRESSION", tokens[i][1])
                    arithmetic = False
                if printer:
                    table_pos = getPosition(tokens[i][2])
                    lexer.symbolTable[table_pos][7] = True
                    printer = False
                if method:
                    table_pos = getPosition(tokens[i][2])
                    lexer.symbolTable[table_pos][3] = "method"
                    lexer.symbolTable[table_pos][8] = True
                    lexer.symbolTable[table_pos].append([])
                    print np.array(lexer.symbolTable)
                    deleteFromTable(table_pos)
                    method = False
                if arguments:
                    table_pos = getPosition(tokens[i][2])
                    if lexer.symbolTable[table_pos][3] != "call":
                        if not isDeclared(table_pos):
                            printError("VARIABLE IS NOT DECLARED.", tokens[i][2])
                        elif lexer.symbolTable[table_pos][8] == False:
                            printError("VARIABLE NOT INITIALIZED.", tokens[i][1])
                        elif not parameters:
                            printError("TOO MANY ARGUMENTS ON FUNCTION CALL.", tokens[i][1])
                        elif lexer.symbolTable[table_pos][4] != parameters.pop(0):
                            printError("WRONG ARGUMENT TYPES.", tokens[i][1])
                if retorno:
                    table_pos = getPosition(tokens[i][2])
                    if not isDeclared(table_pos):
                        printError("VARIABLE IS NOT DECLARED", tokens[i][1])
                    elif lexer.symbolTable[table_pos][8] == False:
                        printError("VARIABLE NOT INITIALIZED.", tokens[i][1])
                    for j in reversed(lexer.symbolTable):
                        if j[3] == "method":
                            if j[4] != lexer.symbolTable[table_pos][4]:
                                printError("WRONG RETURN TYPE.", tokens[i][1])
                            j[5] = lexer.symbolTable[table_pos][5]
                            break
                    retorno = False
                if par or not par and lexer.symbolTable[getPosition(tokens[i][2])][3] == "call":
                    parameters = par[:]
                    arguments = True
                tablePos = getPosition(tokens[i][2])
                if not isDeclared(tablePos):
                    printError("VARIABLE IS NOT DECLARED", tokens[i][1])                 
            elif stack[-1] == "INTEGER":
                if att:                                                                        # a = INTEGER
                    if lexer.symbolTable[tablePos][4] != "int":                                # Variavel nao eh do tipo inteira (erro)
                        printError("VARIABLE IS NOT INTEGER TYPE.", tokens[i][1])              #
                    intPos = getPosition(tokens[i][2])
                    addValue(lexer.symbolTable[intPos][1], tablePos)
                    lexer.symbolTable.remove(lexer.symbolTable[intPos])
                    att = False
                elif arithmetic:
                    if lexer.symbolTable[tablePos][8] == False:
                        printError("VARIABLE NOT INITIALIZED.", tokens[i][1])
                    if lexer.symbolTable[tablePos][4] != "int":
                        printError("ERROR ON ARITHMETIC EXPRESSION", tokens[i][1])
                    arithmetic = False
                elif arguments:
                    intPos = getPosition(tokens[i][2])
                    if not parameters:
                        printError("TOO MANY ARGUMENTS ON FUNCTION CALL.", tokens[i][1])
                    elif parameters.pop(0) != "int":
                        printError("WRONG PARAMETER TYPES.", tokens[i][1])              
                elif relational:
                    if lexer.symbolTable[tablePos][8] == False:
                        printError("VARIABLE NOT INITIALIZED.", tokens[i][1])
                    if lexer.symbolTable[tablePos][4] != "int":
                        printError("VARIABLE IS NOT INTEGER TYPE FOR COMPARISON.", tokens[i][1])
                    relational = False
                elif retorno:
                    intPos = getPosition(tokens[i][2])
                    for j in reversed(lexer.symbolTable):
                        if j[3] == "method":
                            if j[4] != "int":
                                printError("WRONG RETURN TYPE.", tokens[i][1])
                            j[5] = lexer.symbolTable[intPos][1]
                            break
                    lexer.symbolTable.remove(lexer.symbolTable[intPos])
                    retorno = False
                int_pos = getPosition(tokens[i][2])
            elif (stack[-1] == "TRUE" or stack[-1] == "FALSE"):
                if att:                                                                        # a = BOOL
                    if lexer.symbolTable[tablePos][4] != "boolean":                            # Variavel nao eh do tipo bool (erro)
                        printError("VARIABLE IS NOT BOOLEAN TYPE.", tokens[i][1])
                    addValue(stack[-1], tablePos)
                    att = False
                elif arithmetic:
                    printError("ERROR ON ARITHMETIC EXPRESSION", tokens[i][1])
                elif arguments:
                    if not parameters:
                        printError("TOO MANY ARGUMENTS ON FUNCTION CALL.", tokens[i][1])
                    elif parameters.pop(0) != "boolean":
                        printError("WRONG PARAMETER TYPES.", tokens[i][1])
                elif relational:
                    if lexer.symbolTable[tablePos][8] == False:
                        printError("VARIABLE NOT INITIALIZED.", tokens[i][1])
                    if lexer.symbolTable[tablePos][4] != "boolean":
                        printError("VARIABLE IS NOT BOOLEAN TYPE FOR COMPARISON.", tokens[i][1])
                    relational = False
                elif retorno:
                    for j in reversed(lexer.symbolTable):
                        if j[3] == "method":
                            if j[4] != "boolean":
                                printError("WRONG RETURN TYPE.", tokens[i][1])
                            j[5] = stack[-1]
                            break
                    retorno = False
            elif stack[-1] == "CLOSE_PAR" and arguments:
                if parameters:
                    printError("WRONG ARGUMENTS ON FUNCTION CALL.", tokens[i][1])
                arguments = False
            elif stack[-1] == "ATT":
                att = True
            elif stack[-1] == "RELATIONAL":
                relational = True
            elif stack[-1] == "ARITHMETIC":
                arithmetic = True
            elif stack[-1] == "def":
                method = True
            elif stack[-1] == "return":
                retorno = True
            elif stack[-1] == "print":
                printer = True
            print stack[-1]    
            stack.pop()
        else:
            print "## SYNTAX ERROR ON LINE", tokens[i][1], "##"
            print "Expected: ", stack[-1], " Found: ", tokens[i][0]
            sys.exit()
        #print np.array(stack)
    #print stack
    
    if not stack:       # Pilha Vazia?
       print "------------------------------Code Compiled!----------------------------------"
   
   
