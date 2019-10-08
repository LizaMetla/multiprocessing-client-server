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
            '1': {'desc': 'Просмотр учеников.', 'func': self.get_all_students},
            '2': {'desc': 'Просмотр ученика', 'func': self.student_view},
            '3': {'desc': 'Добавление студента', 'func': self.add_student},
            '4': {'desc': 'Удаление студента', 'func': self.delete_student},
            '5': {'desc': 'Редактирование студента', 'func': self.edit_student},
            '6': {'desc': 'Фильтрация студентов по оценке', 'func': self.filter_students_by_mark},
            '7': {'desc': 'Поиск', 'func': self.filter_students},
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

    async def get_all_students(self):
        await self.send_data('get_all_students')
        await self.read_data()

    async def student_view(self):
        pk = input('Введите первичный ключ пользователя: ')
        await self.send_data('get', pk=pk)
        await self.read_data()

    async def add_student(self):
        name = input('Введите ФАМИЛИЮ студента: ')
        common_mark = input('Введите среднюю оценку: ')
        sex = input('Введите пол студента: ')
        form_of_education = input('Введите тип обучения: ')
        await self.send_data('add', name=name, common_mark=common_mark, sex=sex, form_of_education=form_of_education)
        await self.read_data()

    async def delete_student(self):
        pk = input('Введите первичный ключ тура, для удалениия: ')
        await self.send_data('delete', pk=pk)
        await self.read_data()

    async def edit_student(self):
        await self.send_data('get_all_students')
        all_students = await self.read_data()
        pk = input('Введите первичный ключ тура, для редактирования: ')
        while not self._is_student_exists(pk, all_students):
            print('Неверный ввод, такой записи не существует!')
            pk = input('Введите первичный ключ тура, для редактирования: ')
        student = self._get_student_from_students(pk, all_students)
        edit_student = self._edit_student_from_dict(student)
        await self.send_data('edit', **edit_student)
        await self.read_data()

    def _edit_student_from_dict(self, student):
        continue_flag = 'д'
        while continue_flag == 'д':
            answers = {}
            i = 1
            for key, value in student.items():
                if key == 'pk':
                    continue
                print(f'{i}: {key} - {value}')
                answers.update({i: key})
                i += 1
            number = int(input('Введите номер поля, которое вы хотите редактировать: '))
            key = answers.get(number)
            new_value = input(f'Введите новое значение для поля {key}: ')
            student.update({key: new_value})
            continue_flag = input('Продолжить редактирование? Д/н').lower()
        return student

    def _is_student_exists(self, pk, all_students):
        for student in all_students:
            if student.get('pk') == pk:
                return True
        return False

    def _get_student_from_students(self, pk, all_students):
        for student in all_students:
            if student.get('pk') == pk:
                return student

    async def filter_students_by_mark(self):
        common_mark = float(input('Введите максимальную оценку: '))
        await self.send_data('filter_lt', common_mark=common_mark)
        await self.read_data()

    async def filter_students(self):
        model_fields = ['name', 'common_mark', 'sex', 'form_of_education']
        filter_params = {}
        continue_flag = 'д'
        while continue_flag == 'д':
            answers = {}
            i = 1
            for key in model_fields:
                print(f'{i}: {key}')
                answers.update({i: key})
                i += 1
            number = int(input('Введите номер поля для поиска: '))
            key = answers.get(number)
            new_value = input(f'Введите значение для поиска {key}: ')
            filter_params.update({key: new_value})
            continue_flag = input('Продолжить ? Д/н').lower()

        await self.send_data('filter', **filter_params)
        await self.read_data()

    async def exit_from_program(self):
        await sleep(1)
        return 0


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client(loop))
    loop.close()
