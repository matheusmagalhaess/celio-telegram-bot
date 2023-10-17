# Validador de CPF

import re

# Verificando se a entrada contém apenas dígitos e possui 9 caracteres.

def cpf_check(entrada):
    try:

        # Função que retorna a soma do produto dos 9 primeiros dígitos por uma regressão de 10 a 2

        def check_digito1 (entrada):
            cpf = [int(n) for n in entrada]
            cpf_lista = [int(n) for n in entrada]
            # Exclui os dois últimos valores da lista
            cpf_lista.pop()
            cpf_lista.pop()

            # Lista de referência para a validação do primeiro dígito... 
            ref_list1 =(10, 9, 8, 7, 6, 5, 4, 3, 2)

            # A função zip combina os dois iteráveis onde eu realizo uma multiplicação individual pelo acesso ao for
            resultado1 = [num1 * num2 for num1, num2 in zip(cpf_lista, ref_list1)]
            #Somando todos os elementos da tupla resultado1
            soma_resultado1 = sum(resultado1)

            resto = soma_resultado1 % 11
            

            if resto < 2 and cpf[9] == 0:
                checkdigit1_status = True
                digit1 = 0
            else:
                if cpf[9] == (11-resto):
                    checkdigit1_status = True
                    digit1 = (11-resto)
                else:
                    checkdigit1_status = False
                    digit1 = None
            # Retorna um booleano e o valor do digito 1
            return checkdigit1_status, digit1


        def check_digito2(entrada):
            cpf = [int(n) for n in entrada]
            cpf_lista = [int(n) for n in entrada]
            # Exclui o último valor da lista
            cpf_lista.pop()

            # Lista de referência para a validação do primeiro dígito... 
            ref_list2 =(11, 10, 9, 8, 7, 6, 5, 4, 3, 2)

            # A função zip combina os dois iteráveis onde eu realizo uma multiplicação individual pelo acesso ao for
            resultado2 = [num1 * num2 for num1, num2 in zip(cpf_lista, ref_list2)]
            #Somando todos os elementos da tupla resultado1
            soma_resultado2 = sum(resultado2)

            resto = soma_resultado2 % 11
            

            if resto < 2 and cpf[10] == 0:
                checkdigit2_status = True
                digit2 = 0
            else:
                if cpf[10] == (11-resto):
                    checkdigit2_status = True
                    digit2 = (11-resto)
                else:
                    checkdigit2_status = False
                    digit2 = None
            # Retorna um booleano e o valor do digito 1
            return checkdigit2_status, digit2
        status_digito1, valor_digito1 = check_digito1(entrada)
        status_digito2, valor_digito2 = check_digito2(entrada)

        if status_digito1 and status_digito2:
            return True
        else:
            return False
    except(IndexError, ValueError):
        return False