import asyncio
import json
from dataclasses import asdict

CONNECTION_COUNTER = 0
from models import TouristOrganisation


def get(pk=None):
    tour = TouristOrganisation.get(pk)
    if not tour:
        return dict()
    else:
        return asdict(tour)


def add(**kwargs):
    return asdict(TouristOrganisation(**kwargs).save()) # создание и сохранение данных класса


def delete(pk=None):
    TouristOrganisation.delete(tour_uuid=pk)
    return {'message': 'success'}


def get_all_tours():
    all_tours = TouristOrganisation.get_all_tours()
    response = [asdict(tour) for tour in all_tours]
    return response


def edit(**kwargs):
    print('edit')
    asdict(TouristOrganisation(**kwargs).save())
    return {'message': 'success'}


def filter_lt(cost=None):
    response = TouristOrganisation.filter_lt(cost=cost)
    response = [asdict(tour) for tour in response]
    return response


operators = {'get': get, 'add': add, 'delete': delete, 'get_all_tours': get_all_tours, 'edit': edit,
             'filter': filter_lt}


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
