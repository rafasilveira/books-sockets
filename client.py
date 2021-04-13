import socket
import simplejson as json

IP = 'localhost'
PORT = 50512


def connect(ip, port):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((ip, port))

    return connection


def send(connection, message: dict):
    msg = json.dumps(message).encode()
    connection.send(msg)
    res = connection.recv(32768)
    return json.loads(res.decode())


def handleResponse(response):
    if (response['status'] == 'sucesso'):

        # Busca por livro
        if (response['code'] == 'get_book'):
            if (len(response['content']) > 0):
                print('id \t| ano \t| edicao \t| titulo \t| autor ')
                for row in response['content']:
                    id, title, author, edition, year = row
                    print(f'{id} \t| {year} \t| {edition} \t| {title} \t| {author}')
            else:
                print('Nenhum livro encontrado.')

        # Criar livro
        if (response['code'] in ['create_book', 'update_book', 'remove_book', 'update_book'] ):
            print(response['content'])


    if (response['status'] != 'sucesso'):
        print(f"Erro: {response['content']}")
                    


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

            handleResponse(response)

        connection.close()
    except Exception as e:
        print(e)
        wait = input()


run()
