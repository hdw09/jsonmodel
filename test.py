import json
from jsonModel import jsonModel


@jsonModel()
class Pet(object):

    def __init__(self):
        self.name = ""


@jsonModel()
class Cat(Pet):

    def __init__(self):
        super(Pet, self).__init__()
        self.breed = ""
        self.love_humans = 0


@jsonModel()
class Dog(Pet):

    def __init__(self):
        super(Pet, self).__init__()
        self.age = 0


@jsonModel()
class Car(object):

    def __init__(self):
        self.registration_number = ""
        self.engine_capacity = 0.0
        self.color = ""


@jsonModel({"car": Car}, {"pets": Pet})
class Person(object):

    def __init__(self):
        self.name = ""
        self.surname = ""
        self.car = None
        self.pets = []


jsonString = """{
    "car": {
        "color": "red",
        "registration_number": "ASDF777",
        "engine_capacity": 5.0
    },
    "surname": "Bravo",
    "name": "Johny",
    "nickname": "hello",
    "pets": [
        {
            "name": "Garfield"
        },
        {
            "age": 9,
            "name": "Dogmeat"
        }
    ]
}"""

person = Person()

person.fromJson(json.loads(jsonString))  # json to model
print(person.__dict__)

print(json.dumps(person.toKeyValue()))  # model to json



