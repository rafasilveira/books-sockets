import socket
import sys
import json
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
PORT = 50004

def client_thread(client):
    return threading.Thread(target=handler, args=(client,))


def handler(client):
    print('Starting client thread for:')
    print(client)
    
    while True:
        (d, _, _, _) = client.recvmsg(32768)
        
        if (d):
            data = json.loads(d.decode())
            if 'option' in data.keys():
                opt = int(data['option'])
                msg = message('', '')

                # criar livro
                if opt == 1:
                    if (create_book(data)):
                        msg = message(
                            'sucesso', 'livro adicionado com sucesso')
                    else:
                        msg = message(
                            'erro', 'houve um problema ao adicionar o livro.')

                # busca por titulo
                elif opt == 2:
                    result = get_by_title(data)
                    if(result is not None):
                        msg = message(
                            'sucesso', json.dumps(result))
                    else:
                        msg = message(
                            'erro', 'não foi encontrado nenhum livro com esse título')

                # busca por autor
                elif opt == 3:
                    result = get_by_author(data)
                    if(result is not None):
                        msg = message(
                            'sucesso', json.dumps(result))
                    else:
                        msg = message(
                            'erro', 'não foi encontrado nenhum livro com esse autor')

                # busca por ano/edicao
                elif opt == 4:
                    result = get_by_year_edition(data)
                    if(result is not None):
                        msg = message(
                            'sucesso', json.dumps(result))
                    else:
                        msg = message(
                            'erro', 'não foi encontrado nenhum livro com esse ano/edição')

                # remover
                elif opt == 5:
                    if(remove(data)):
                        msg = message(
                            'sucesso', 'livro excluído com sucesso')
                    else:
                        msg = message(
                            'erro', 'não foi possível excluir o livro')

                # atualizar
                elif opt == 6:
                    update(data)
                    msg = message(
                        'successo', 'livro atualizado com sucesso')

                # sair
                elif opt == 0:
                    print('client left:')
                    print(client)
                    msg = message('sucesso', 'você desconectou')
                    client.send(msg)
                    break

            else:
                msg = message(
                    'erro', 'key \'option\' not found')
            client.send(msg)
        else:
            break

    client.close()


def message(status: str, content: str):
    return json.dumps({'status': status, 'content': content}).encode()


def connect_db():
    print('Connecting to db')
    print(f'DB_HOST: {DB_HOST}')
    print(f'DB_USER: {DB_USER}')
    print(f'DB_NAME: {DB_NAME}')
    print(f'DB_PW: {DB_PW}')
    print(f'DB_PORT: {DB_PORT}')

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
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def start_server(ip: str, port: int):
    connect_db()

    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.bind((ip, port))
    # server_socket.listen(10)
    # print(f'🚀 Socket server ready!')
    # print('Waiting for connections at {ip}:{port}')

    # while(True):
    #     (client_socket, address) = server_socket.accept()
    #     print(f'Receiving connection from {address}')
    #     ct = client_thread(client_socket)
    #     ct.run()


def create_book(data):
    print('Create book')
    print(data)
    return True


def get_by_title(data):
    print('Get by title')
    print(data)
    return True


def get_by_author(data):
    print('Get by author')
    print(data)
    return True


def get_by_year_edition(data):
    print('Get by year/edition')
    print(data)
    return True


def remove(data):
    print('remove book')
    print(data)
    return True


def update(data):
    print('update book')
    print(data)
    return True


if __name__ == '__main__':
    ip = IP
    port = PORT
    start_server(ip, port)
