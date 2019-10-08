import pickle
from dataclasses import dataclass
from uuid import uuid4


@dataclass
class StudentSession:
    name: str
    common_mark: float
    sex: str
    form_of_education: str
    pk: str = uuid4().hex

    def save(self):
        all_students = self.get_all_students()
        new_students = []
        for student in all_students:
            if student.pk != self.pk:
                new_students.append(student)
        new_students.append(self)
        self._save_in_db(new_students)
        return self

    @classmethod
    def filter(cls, queryset=None, **kwargs):
        if queryset is None:
            queryset = cls.get_all_students()
        result = queryset
        for key, value in kwargs.items():
            result = list(filter(lambda student: getattr(student, key) == value, result))
        return result

    @classmethod
    def filter_lt(cls, queryset=None, **kwargs):
        if queryset is None:
            queryset = cls.get_all_students()
        result = queryset
        for key, value in kwargs.items():
            result = list(filter(lambda student: float(getattr(student, key)) < value, result))
        return result

    @classmethod
    def get(cls, student_pk):
        all_students = cls.get_all_students()
        search_list = list(filter(lambda student: student.pk == student_pk, all_students))
        if len(search_list) < 1:
            return dict()
        return search_list.pop(0)


    @classmethod
    def delete(cls, student_uuid):
        student = cls.get(student_uuid)
        all_students = cls.get_all_students()
        if student in all_students:
            all_students.remove(student)
        cls._save_in_db(all_students)

    @classmethod
    def is_student_by_uuid_exists(cls, student_uuid):
        all_students = cls.get_all_students()
        search_list = list(filter(lambda student: student.uuid == student_uuid, all_students))
        if len(search_list) < 1:
            return False
        else:
            return True

    @staticmethod
    def get_all_students():
        with open('database.pickle', 'rb+') as f:
            try:
                data = pickle.load(f)
            except EOFError:
                data = list()
            return data

    @staticmethod
    def _save_in_db(data):
        with open('database.pickle', 'wb') as f:
            pickle.dump(data, f)


if __name__ == '__main__':
    student = {'pk': uuid4().hex, 'name': 'Минск', 'common_mark': 2000, 'sex': '1 неделя',
            'form_of_education': 'Космо-шатл Илона Макса'}
    #studentistOrganisation(**student).save()
    # result = studentistOrganisation.filter_lt(common_mark=4000)
    print(StudentSession.filter_lt(common_mark=4000))
    print(StudentSession.filter(pk='1a725e216d6c4cafa07c39ab06ced08e'))
