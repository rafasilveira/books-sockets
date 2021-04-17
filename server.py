import socket
import sys
import simplejson as json
import threading
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_NAME = os.getenv('DB_NAME')
DB_PW = os.getenv('DB_PW')
DB_PORT = os.getenv('DB_PORT')

IP = 'localhost'
PORT = 50512


def message(code: str, status: str, content: any):
    return json.dumps({'status': status, 'content': content, 'code': code}).encode()


def client_thread(client, connection):
    return threading.Thread(target=handler, args=(client, connection))


def handler(client, connection):
    print('Starting client thread for:')
    print(client)

    while True:
        try:
            d = client.recv(1048576)
        except Exception as e:
            d = None

        if (d):
            data = json.loads(d.decode())
            if 'option' in data.keys():
                opt = int(data['option'])
                msg = message('', '', '')

                # criar livro
                if opt == 1:
                    if (create_book(connection, data)):
                        msg = message('create_book',
                                      'sucesso', 'livro adicionado com sucesso')
                    else:
                        msg = message('create_book',
                                      'erro', 'houve um problema ao adicionar o livro.')

                # busca por titulo
                elif opt == 2:
                    result = get_by_title(connection, data)
                    if (len(result) > 0):
                        msg = message('get_book',
                                      'sucesso', result)
                    else:
                        msg = message('get_book',
                                      'erro', 'não foi encontrado nenhum livro com esse título')

                # busca por autor
                elif opt == 3:
                    result = get_by_author(connection, data)
                    if (len(result) > 0):
                        msg = message('get_book',
                                      'sucesso', result)
                    else:
                        msg = message('get_book',
                                      'erro', 'não foi encontrado nenhum livro com esse autor')

                # busca por ano/edicao
                elif opt == 4:
                    result = get_by_year_edition(connection, data)
                    if (len(result) > 0):
                        msg = message('get_book',
                                      'sucesso', result)
                    else:
                        msg = message('get_book',
                                      'erro', 'não foi encontrado nenhum livro com esse ano/edição')

                # remover
                elif opt == 5:
                    if (remove(connection, data)):
                        msg = message('remove_book',
                                      'sucesso', 'livro excluído com sucesso')
                    else:
                        msg = message('remove_book',
                                      'erro', 'não foi possível excluir o livro')

                # atualizar
                elif opt == 6:
                    update(connection, data)
                    msg = message('update_book',
                                  'successo', 'livro atualizado com sucesso')

                # sair
                elif opt == 0:
                    print('client left:')
                    print(client)
                    msg = message('logout', 'sucesso', 'você desconectou')
                    client.send(msg)
                    break

            else:
                msg = message('generic_error',
                              'erro', 'key \'option\' not found')

            client.send(msg)
        else:
            break

    client.close()


def connect_db():
    print('Connecting to db')
    #print(f'DB_HOST: {DB_HOST}')
    #print(f'DB_USER: {DB_USER}')
    #print(f'DB_NAME: {DB_NAME}')
    #print(f'DB_PW: {DB_PW}')
    #print(f'DB_PORT: {DB_PORT}')

    try:
        connection = mysql.connector.connect(host=DB_HOST,
                                             database=DB_NAME,
                                             user=DB_USER,
                                             password=DB_PW,
                                             port=DB_PORT)
        print('connection:')
        print(connection)
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            return connection

    raise Exception('Error while connecting to MySQL')


def start_server(ip: str, port: int):
    connection = connect_db()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(10)
    print(f'🚀 Socket server ready!')
    print(f'Waiting for connections at {ip}:{port}')

    while True:
        (client_socket, address) = server_socket.accept()
        print(f'Receiving connection from {address}')
        ct = client_thread(client_socket, connection)
        ct.run()


def create_book(connection, data):
    cursor = connection.cursor()

    query = "SELECT MAX(l.codigo)+1 AS proximo_codigo FROM livros l"
    cursor.execute(query)
    record = cursor.fetchone()

    idBook = None
    for r in record:
        idBook = r

    query = "INSERT INTO livros (codigo, titulo) VALUES (" + str(idBook) + ", '" + data['title'].strip() + "') "

    cursor = connection.cursor()
    cursor.execute(query)

    if cursor.rowcount == 0:
        raise Exception('An insertion error has occurred [livros]')

    query = "SELECT a.codigo as codigo FROM autor a WHERE TRIM(a.nome) = '" + \
            data['author'].strip() + "'"
    cursor.execute(query)
    record = cursor.fetchone()

    if record is None:
        raise Exception('No authors were found.')

    idAuthor = None
    for r in record:
        idAuthor = r

    if idAuthor is None:
        raise Exception('No authors were found')

    query = "INSERT INTO livroautor (codigolivro, codigoautor) VALUES (" + str(idBook) + ", " + str(idAuthor) + ") "

    cursor = connection.cursor()
    cursor.execute(query)

    if cursor.rowcount == 0:
        raise Exception('An insertion error has occurred [livroautor]')

    query = "INSERT INTO edicao (codigolivro, numero, ano) VALUES (" + str(idBook) + ", " + data['edition'].strip() + ", " + data['year'].strip() + ") "

    cursor = connection.cursor()
    cursor.execute(query)

    if cursor.rowcount == 0:
        raise Exception('An insertion error has occurred [edicao]')

    connection.commit()

    return cursor.rowcount


def get_by_title(connection, data):
    query = "SELECT ls.codigo as codigo, " \
            "TRIM(ls.titulo) as titulo, " \
            "GROUP_CONCAT(DISTINCT TRIM(ar.nome) SEPARATOR ' & ') as autor, " \
            "GROUP_CONCAT(DISTINCT eo.numero SEPARATOR ', ') as edicao, " \
            "GROUP_CONCAT(DISTINCT eo.ano SEPARATOR ', ') as edicao " \
            "FROM livros ls " \
            "INNER JOIN livroautor la ON ls.codigo = la.codigolivro " \
            "INNER JOIN autor ar ON la.codigoautor = ar.codigo " \
            "INNER JOIN edicao eo ON ls.codigo = eo.codigolivro " \
            "WHERE ls.titulo LIKE '%" + data['title'] + "%'" \
            "GROUP BY ls.codigo " \
            "ORDER BY ls.titulo ASC"

    cursor = connection.cursor()
    cursor.execute(query)

    records = cursor.fetchall()

    return records


def get_by_author(connection, data):
    query = "SELECT ls.codigo as codigo, " \
            "TRIM(ls.titulo) as titulo, " \
            "GROUP_CONCAT(DISTINCT TRIM(ar.nome) SEPARATOR ' & ') as autor, " \
            "GROUP_CONCAT(DISTINCT eo.numero SEPARATOR ', ') as edicao, " \
            "GROUP_CONCAT(DISTINCT eo.ano SEPARATOR ', ') as edicao " \
            "FROM livros ls " \
            "INNER JOIN livroautor la ON ls.codigo = la.codigolivro " \
            "INNER JOIN autor ar ON la.codigoautor = ar.codigo " \
            "INNER JOIN edicao eo ON ls.codigo = eo.codigolivro " \
            "WHERE ar.nome LIKE '%" + data['author'] + "%'" \
            "GROUP BY ls.codigo " \
            "ORDER BY ls.titulo ASC"

    cursor = connection.cursor()
    cursor.execute(query)

    records = cursor.fetchall()

    return records


def get_by_year_edition(connection, data):
    query = "SELECT ls.codigo as codigo, " \
            "TRIM(ls.titulo) as titulo, " \
            "GROUP_CONCAT(DISTINCT TRIM(ar.nome) SEPARATOR ' & ') as autor, " \
            "GROUP_CONCAT(DISTINCT eo.numero SEPARATOR ', ') as edicao, " \
            "GROUP_CONCAT(DISTINCT eo.ano SEPARATOR ', ') as edicao " \
            "FROM livros ls " \
            "INNER JOIN livroautor la ON ls.codigo = la.codigolivro " \
            "INNER JOIN autor ar ON la.codigoautor = ar.codigo " \
            "INNER JOIN edicao eo ON ls.codigo = eo.codigolivro " \
            "WHERE eo.numero = " + data['edition'] + " AND eo.ano = " + data['year'] + " " \
            "GROUP BY ls.codigo " \
            "ORDER BY ls.titulo ASC"

    cursor = connection.cursor()
    cursor.execute(query)

    records = cursor.fetchall()

    return records


def remove(connection, data):
    cursor = connection.cursor()

    query = "SELECT ls.codigo as codigo FROM livros ls WHERE TRIM(ls.titulo) = '" + \
        data['title'].strip() + "'"
    cursor.execute(query)
    record = cursor.fetchone()

    if record is None:
        raise Exception('No books were found.')

    id = None
    for r in record:
        id = r

    if id is None:
        raise Exception('No books were found.')

    query = "DELETE FROM livroautor WHERE codigolivro = " + str(id)
    cursor.execute(query)
    connection.commit()

    query = "DELETE FROM edicao WHERE codigolivro = " + str(id)
    cursor.execute(query)
    connection.commit()

    query = "DELETE FROM livros WHERE codigo = " + str(id)
    cursor.execute(query)
    connection.commit()

    amount = str(cursor.rowcount)

    return amount


def update(connection, data):
    cursor = connection.cursor()

    query = "SELECT ls.codigo as codigo FROM livros ls WHERE TRIM(ls.titulo) = '" + \
            data['old_title'].strip() + "'"
    cursor.execute(query)
    record = cursor.fetchone()

    if record is None:
        raise Exception('No books were found.')

    idBook = None
    for r in record:
        idBook = r

    if idBook is None:
        raise Exception('No books were found.')

    if len(data['title'].strip()) > 0:
        query = "UPDATE livros SET titulo = '" + data['title'].strip() + "' WHERE codigo = " + str(idBook)
        cursor.execute(query)

    if len(data['author'].strip()) > 0:
        query = "SELECT a.codigo as codigo FROM autor a WHERE TRIM(a.nome) = '" + \
                data['author'].strip() + "'"
        cursor.execute(query)
        record = cursor.fetchone()

        idAuthor = None
        for r in record:
            idAuthor = r

        if idAuthor is None:
            raise Exception('No authors were found')

        query = "UPDATE livroautor SET codigoautor = " + str(idAuthor) + " WHERE codigolivro = " + str(idBook)
        cursor.execute(query)

    if len(data['edition'].strip()) > 0:
        query = "UPDATE edicao SET numero = " + data['edition'].strip() + " WHERE codigolivro = " + str(idBook)
        cursor.execute(query)

    if len(data['year'].strip()) > 0:
        query = "UPDATE edicao SET ano = " + data['year'].strip() + " WHERE codigolivro = " + str(idBook)
        cursor.execute(query)

    connection.commit()

    return 1


if __name__ == '__main__':
    ip = IP
    port = PORT
    start_server(ip, port)
