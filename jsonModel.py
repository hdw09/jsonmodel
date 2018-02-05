"""

"""


def jsonModel(objectMap={}, listClassMap={}):
    """
    it is very easy to use !
    @jsonModel(objectMap={"car": Car}, listClassMap={"pets": Dog})
    or
    @jsonModel({"car": Car}, {"pets": Dog})
    or
    @jsonModel()
    """
    def decorate(cls):
        def fromJson(self, data):
            """ json key_value model"""
            for key in self.__dict__:
                if key in data:
                    if isinstance(data[key], dict) and key in objectMap:
                        obj = self.__dict__[key] = objectMap[key]()
                        obj.fromJson(data[key])
                    elif isinstance(data[key], (list, tuple)) and key in listClassMap:
                        tempList = []
                        for item in data[key]:
                            obj = listClassMap[key]()
                            obj.fromJson(item)
                            tempList.append(obj)
                        self.__dict__[key] = tempList
                    else:
                        self.__dict__[key] = data[key]
                else:
                    print("JsonModel log : " + key + " not in json data")

        def toKeyValue(self):
            """ model to json key_value """
            tempDic = {}
            for key in self.__dict__:
                if key in objectMap:
                    obj = self.__dict__[key]
                    tempDic[key] = obj.toKeyValue()
                elif key in listClassMap:
                    tempList = []
                    for item in self.__dict__[key]:
                        obj = item.toKeyValue()
                        tempList.append(obj)
                    tempDic[key] = tempList
                else:
                    tempDic[key] = self.__dict__[key]
            return tempDic

        cls.fromJson = fromJson
        cls.toKeyValue = toKeyValue
        return cls
    return decorate
