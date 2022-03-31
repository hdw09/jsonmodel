# ----------------------------------------------------------------------
#  Copyright (c) 2018-2030, huang dawei, China. All rights reserved.
#
#  everyone can use this code for any purpose.
# ----------------------------------------------------------------------


def jsonModel(objectMap={}, listClassMap={}, dictMap={}):
    """
    It is very easy to use !
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
                tmpObject = data.get(key)
                if tmpObject is None:
                    print("JsonModel log : " + key + " not in json data")
                    continue

                if isinstance(tmpObject, dict):
                    if key in dictMap:
                        objClass = dictMap[key]
                        tmpDict = {}
                        for k, v in tmpObject.items():
                            obj = objClass()
                            obj.fromJson(v)
                            tmpDict[k] = obj
                        self.__dict__[key] = tmpDict
                        continue
                    elif key in objectMap:
                        obj = self.__dict__[key] = objectMap[key]()
                        obj.fromJson(tmpObject)
                        continue
                elif isinstance(tmpObject, (list, tuple)) and key in listClassMap:
                    tempList = []
                    for item in tmpObject:
                        obj = listClassMap[key]()
                        obj.fromJson(item)
                        tempList.append(obj)
                    self.__dict__[key] = tempList
                    continue
                self.__dict__[key] = data[key]


        def toKeyValue(self):
            """ model to json key_value """
            tempDic = {}
            for key in self.__dict__:
                tmpObj = self.__dict__[key]
                if tmpObj is None:
                    continue

                if key in dictMap:
                    objDict = {}
                    for k, v in tmpObj.items():
                        objDict[k] = v.toKeyValue()
                    tempDic[key] = objDict

                elif key in objectMap:
                    obj = tmpObj
                    tempDic[key] = obj.toKeyValue()
                elif key in listClassMap:
                    tempList = []
                    for item in tmpObj:
                        obj = item.toKeyValue()
                        tempList.append(obj)
                    tempDic[key] = tempList
                else:
                    tempDic[key] = tmpObj
            return tempDic

        @classmethod
        def objectArrayFromJsonArray(className, data):
            """create model list by json list"""
            tempList = []
            if isinstance(data, list):
                for item in data:
                    obj = className()
                    obj.fromJson(item)
                    tempList.append(obj)
            return tempList

        @classmethod
        def objectArrayToJsonArray(className, objectList):
            """dump objectList to json keyValue list"""
            tempList = []
            for obj in objectList:
                if isinstance(obj, className):
                    tempList.append(obj.toKeyValue())
            return tempList

        cls.fromJson = fromJson
        cls.toKeyValue = toKeyValue
        cls.objectArrayFromJsonArray = objectArrayFromJsonArray
        cls.objectArrayToJsonArray = objectArrayToJsonArray

        return cls

    return decorate
