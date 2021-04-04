import socket
import json

IP = 'localhost'
PORT = 50004


def connect(ip, port):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((ip, port))

    return connection


def send(connection, message: dict):
    msg = json.dumps(message)
    connection.send(msg.encode())
    (response, _, _, _) = connection.recvmsg(32768)

    return response


def run():
    try:
        print('Sistema de Consulta de Livros - Lucas Molin e Rafael Bourscheid\n')

        # ip = input('IP: ')
        # port = int(input('Porta: '))
        ip = IP
        port = PORT

        connection = connect(ip, port)

        while True:
            print('\nOpções\n')
            print('1 - Criar livro')
            print('2 - Consultar livro por título')
            print('3 - Consultar livro por autor')
            print('4 - Consultar livro por ano/edição')
            print('5 - Remover livro')
            print('6 - Alterar dados de livro')
            print('0 - Sair\n')

            response = None
            option = -1
            while option < 0 or option > 6:
                option = int(input('Qual opção você escolhe? '))
                if option == 1:
                    title = input('Título do livro: ')
                    author = input('Autor: ')
                    edition = input('Edição: ')
                    year = input('Ano: ')

                    book = {
                        "option": option,
                        "title": title,
                        "author": author,
                        "edition": edition,
                        "year": year
                    }

                    response = send(connection, book)

                elif option == 2:
                    title = input('Qual o título do livro? ')

                    search = {
                        "option": option,
                        "title": title,
                    }

                    response = send(connection, search)

                elif option == 3:
                    author = input('Qual o autor do livro? ')

                    search = {
                        "option": option,
                        "author": author
                    }

                    response = send(connection, search)

                elif option == 4:
                    edition = input('Qual a edição do livro? ')
                    year = input('Qual o ano do livro? ')

                    search = {
                        "option": option,
                        "edition": edition,
                        "year": year
                    }

                    response = send(connection, search)

                elif option == 5:
                    title = input('Qual o título do livro? ')

                    search = {
                        "option": option,
                        "title": title
                    }

                    response = send(connection, search)

                elif option == 6:
                    old_title = input('Título atual do livro: ')
                    title = input('Novo título do livro: ')
                    author = input('Autor: ')
                    edition = input('Edição: ')
                    year = input('Ano: ')

                    book = {
                        "option": option,
                        "old_title": old_title,
                        "title": title,
                        "author": author,
                        "edition": edition,
                        "year": year
                    }

                    response = send(connection, str(book))

                elif option == 0:
                    response = send(connection, {'option': 0})
                    break

            print('\n')
            print(response)

        connection.close()
    except Exception as e:
        print(e)


run()
