import asyncio
import json
from dataclasses import asdict

CONNECTION_COUNTER = 0
from models import StudentSession


def get(pk=None):
    student = StudentSession.get(pk)
    if not student:
        return dict()
    else:
        return asdict(student)


def add(**kwargs):
    return asdict(StudentSession(**kwargs).save()) # создание и сохранение данных класса


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
             'filter_lt': filter_lt, 'filter': filtera }


async def handle_echo(reader, writer):
    global CONNECTION_COUNTER
    CONNECTION_COUNTER += 1
    addr = writer.get_extra_info("peername")
    print(f'Подключение от пользователя: {addr}')
    print(f'Количество подключений: {CONNECTION_COUNTER}')
    while True:
        data = await reader.read(10000)
        if not data:
            break
        message = data.decode()
        print(f"Пользователь {addr!r} Сообщение: {message!r} ")
        request = json.loads(message)
        response = operators.get(request.get('method'))(**request.get('args'))
        data = json.dumps(response).encode()

        print(f"Отправка от сервера: {data!r}")
        writer.write(data)
        await writer.drain()
    print(f"Закрытие соединения с пользователем: {addr}")
    CONNECTION_COUNTER -= 1
    print(f'Количество подключений: {CONNECTION_COUNTER}')
    writer.close()


loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Запуск сервера на {}'.format(server.sockets[0].getsockname()))
print(f'Количество подключений: {CONNECTION_COUNTER}')
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
