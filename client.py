import asyncio
import json
from asyncio import sleep


async def tcp_echo_client(loop):
    ui = UserInterface(loop)
    await ui.socket_start()
    ans = await ui.input_point_of_menu()
    print('Close the connection')
    ui.writer.close()


class UserInterface:
    point = None

    def __init__(self, loop):
        self.menu_common = {
            '1': {'desc': 'Просмотр всех туров.', 'func': self.get_all_tours},
            '2': {'desc': 'Просмотр тура', 'func': self.tour_view},
            '3': {'desc': 'Добавление тура', 'func': self.add_tour},
            '4': {'desc': 'Удаление тура', 'func': self.delete_tour},
            '5': {'desc': 'Редактирование тура', 'func': self.edit_tour},
            '6': {'desc': 'Фильтрация туров по стоимости', 'func': self.filter_tour},
            '0': {'desc': 'Выход', 'func': self.exit_from_program}
        }
        self.loop = loop

    async def socket_start(self):
        self.reader, self.writer = await asyncio.open_connection(
            '127.0.0.1', 8888, loop=self.loop)

    async def send_data(self, method, **kwargs):
        message = {'method': method, 'args': dict()}

        message['args'].update(kwargs)
        message = json.dumps(message)
        print(f'Send: {message!r}')
        self.writer.write(message.encode()) # sendall = write

    async def read_data(self):
        data = await self.reader.read(10000) # recv = read
        response = json.loads(data.decode())
        self.print_response(response)
        return response

    def dict_print(self, data):
        for key, value in data.items():
            print(f'{key}: {value}')
        print('\n')

    def print_response(self, data):
        if len(data) == 0:
            print('Данные не найдены')
        elif isinstance(data, dict):
            self.dict_print(data)# isinstance if data = dict?
        else:
            for line in data:
                if isinstance(line, dict):
                    self.dict_print(line)
                else:
                    print(line)

    def print_common_menu(self):
        for point, settings in self.menu_common.items():
            print(point + '.', settings.get('desc'))

    async def input_point_of_menu(self):
        while True:
            self.print_common_menu()
            point = input('>> ')
            if point.isdigit() and point in self.menu_common:
                settings = self.menu_common.get(point)
                ans = await settings['func']()
                if ans == 0:
                    break
            else:
                print('Неверный ввод! \n')

    async def get_all_tours(self):
        await self.send_data('get_all_tours')
        await self.read_data()

    async def tour_view(self):
        pk = input('Введите первичный ключ пользователя: ')
        await self.send_data('get', pk=pk)
        await self.read_data()

    async def add_tour(self):
        name = input('Введите название тура: ')
        cost = input('Введите стоимость тура: ')
        timeline = input('Продолжительность тура: ')
        type_of_transport = input('Введите тип транспорта: ')
        await self.send_data('add', name=name, cost=cost, timeline=timeline, type_of_transport=type_of_transport)
        await self.read_data()

    async def delete_tour(self):
        pk = input('Введите первичный ключ тура, для удалениия: ')
        await self.send_data('delete', pk=pk)
        await self.read_data()

    async def edit_tour(self):
        await self.send_data('get_all_tours')
        all_tours = await self.read_data()
        pk = input('Введите первичный ключ тура, для редактирования: ')
        while not self._is_tour_exists(pk, all_tours):
            print('Неверный ввод, такой записи не существует!')
            pk = input('Введите первичный ключ тура, для редактирования: ')
        tour = self._get_tour_from_tours(pk, all_tours)
        edit_tour = self._edit_tour_from_dict(tour)
        await self.send_data('edit', **edit_tour)
        await self.read_data()

    def _edit_tour_from_dict(self, tour):
        continue_flag = 'д'
        while continue_flag == 'д':
            answers = {}
            i = 1
            for key, value in tour.items():
                if key == 'pk':
                    continue
                print(f'{i}: {key} - {value}')
                answers.update({i: key})
                i += 1
            number = int(input('Введите номер поля, которое вы хотите редактировать: '))
            key = answers.get(number)
            new_value = input(f'Введите новое значение для поля {key}: ')
            tour.update({key: new_value})
            continue_flag = input('Продолжить редактирование? Д/н').lower()
        return tour

    def _is_tour_exists(self, pk, all_tours):
        for tour in all_tours:
            if tour.get('pk') == pk:
                return True
        return False

    def _get_tour_from_tours(self, pk, all_tours):
        for tour in all_tours:
            if tour.get('pk') == pk:
                return tour

    async def filter_tour(self):
        cost = float(input('Введите стоимость тура: '))
        await self.send_data('filter', cost=cost)
        await self.read_data()

    async def exit_from_program(self):
        await sleep(1)
        return 0


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client(loop))
    loop.close()
