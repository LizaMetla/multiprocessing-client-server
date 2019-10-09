import json
import multiprocessing
import socket
from dataclasses import asdict

from models import StudentSession

CONNECTION_COUNTER = 0


def get(pk=None):
    student = StudentSession.get(pk)
    if not student:
        return dict()
    else:
        return asdict(student)


def add(**kwargs):
    return asdict(StudentSession(**kwargs).save())  # создание и сохранение данных класса


def delete(pk=None):
    StudentSession.delete(student_uuid=pk)
    return {'message': 'success'}


def get_all_students():
    all_students = StudentSession.get_all_students()
    response = [asdict(student) for student in all_students]
    return response


def edit(**kwargs):
    print('edit')
    asdict(StudentSession(**kwargs).save())
    return {'message': 'success'}


def filter_lt(common_mark=None):
    response = StudentSession.filter_lt(common_mark=common_mark)
    response = [asdict(student) for student in response]
    return response


def filtera(**kwargs):
    response = StudentSession.filter(**kwargs)
    response = [asdict(student) for student in response]
    return response


operators = {'get': get, 'add': add, 'delete': delete, 'get_all_students': get_all_students, 'edit': edit,
             'filter_lt': filter_lt, 'filter': filtera}


def handle_echo(connection, address):
    global CONNECTION_COUNTER
    while True:
        data = connection.recv(1024)
        if not data:
            break
        message = data.decode()
        print(f"Пользователь {address!r} Сообщение: {message!r} ")
        request = json.loads(message)
        response = operators.get(request.get('method'))(**request.get('args'))
        data = json.dumps(response).encode()

        print(f"Отправка от сервера: {data!r}")
        connection.sendall(data)

    print(f"Закрытие соединения с пользователем: {address}")
    CONNECTION_COUNTER -= 1
    print(f'Количество подключений: {CONNECTION_COUNTER}')
    connection.close()


if __name__ == '__main__':

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind(('127.0.0.1', 8888))
    socket.listen(1)
    print('Запуск сервера на 127.0.0.1:8888')
    print(f'Количество подключений: {CONNECTION_COUNTER}')
    try:
        while True:
            conn, address = socket.accept()

            print(f'Подключение от пользователя: {address}')
            CONNECTION_COUNTER += 1
            print(f'Количество подключений: {CONNECTION_COUNTER}')
            process = multiprocessing.Process(target=handle_echo, args=(conn, address))
            process.daemon = True
            process.start()
    except:
        pass
    finally:
        for process in multiprocessing.active_children():
            process.terminate()
            process.join()
