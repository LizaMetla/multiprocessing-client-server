import pickle
from dataclasses import dataclass
from uuid import uuid4


@dataclass
class TouristOrganisation:
    name: str
    cost: float
    timeline: str
    type_of_transport: str
    pk: str = uuid4().hex

    def save(self):
        all_tours = self.get_all_tours()
        new_tours = []
        for tour in all_tours:
            if tour.pk != self.pk:
                new_tours.append(tour)
        new_tours.append(self)
        self._save_in_db(new_tours)
        return self

    @classmethod
    def filter(cls, queryset=None, **kwargs):
        if queryset is None:
            queryset = cls.get_all_tours()
        result = queryset
        for key, value in kwargs.items():
            result = list(filter(lambda tour: getattr(tour, key) == value, result))
        return result

    @classmethod
    def filter_lt(cls, queryset=None, **kwargs):
        if queryset is None:
            queryset = cls.get_all_tours()
        result = queryset
        for key, value in kwargs.items():
            result = list(filter(lambda tour: float(getattr(tour, key)) < value, result))
        return result

    @classmethod
    def get(cls, tour_pk):
        all_tours = cls.get_all_tours()
        search_list = list(filter(lambda tour: tour.pk == tour_pk, all_tours))
        if len(search_list) < 1:
            return dict()
        return search_list.pop(0)


    @classmethod
    def delete(cls, tour_uuid):
        tour = cls.get(tour_uuid)
        all_tours = cls.get_all_tours()
        if tour in all_tours:
            all_tours.remove(tour)
        cls._save_in_db(all_tours)

    @classmethod
    def is_tour_by_uuid_exists(cls, tour_uuid):
        all_tours = cls.get_all_tours()
        search_list = list(filter(lambda tour: tour.uuid == tour_uuid, all_tours))
        if len(search_list) < 1:
            return False
        else:
            return True

    @staticmethod
    def get_all_tours():
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
    tour = {'pk': uuid4().hex, 'name': 'Минск', 'cost': 2000, 'timeline': '1 неделя',
            'type_of_transport': 'Космо-шатл Илона Макса'}
    #TouristOrganisation(**tour).save()
    # result = TouristOrganisation.filter_lt(cost=4000)
    print(TouristOrganisation.filter_lt(cost=4000))
    print(TouristOrganisation.filter(pk='1a725e216d6c4cafa07c39ab06ced08e'))
