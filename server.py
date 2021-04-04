import socket
import sys
import json
import threading

IP = 'localhost'
PORT = 50004
DB_HOST = 'your.mysql.host'  # todo: replace with host
DB_USER = 'your.db.user'     # todo: replace with user
DB_PW = 'your.password'      # todo: replace with password
DB_PORT = 'yout.db.port'     # todo: replace with db port

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
    print('(not) connecting to db')


def start_server(ip: str, port: int):
    connect_db()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(10)
    print(f'🚀 Socket server ready!')
    print('Waiting for connections at {ip}:{port}')

    while(True):
        (client_socket, address) = server_socket.accept()
        print(f'Receiving connection from {address}')
        ct = client_thread(client_socket)
        ct.run()


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
