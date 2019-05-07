# ----------------------------------------------------------------------
#  Copyright (c) 2018-2030, huang dawei, China. All rights reserved.
#
#  everyone can use this code for any purpose.
# ----------------------------------------------------------------------

import json


def jsonModel(objectMap={}, listClassMap={}, customKeyMap={}):
    """
    It is very easy to use !
    @jsonModel(objectMap={"car": Car}, listClassMap={"pets": Dog})
    or
    @jsonModel({"car": Car}, {"pets": Dog})
    or
    @jsonModel()
    """

    def decorate(cls):
        __origin_init__ = None

        def __hack_init__(self, *args, **kwargs):
            # exclude self
            input_count = len(args) + len(kwargs)
            default_var_count = len(__origin_init__.__defaults__)
            min_arg_count = __origin_init__.__code__.co_argcount - default_var_count - 1
            max_arg_count = __origin_init__.__code__.co_argcount
            varnames = __origin_init__.__code__.co_varnames
            co_flags = __origin_init__.__code__.co_flags
            is_args = co_flags & 0b100 != 0
            is_kwargs = co_flags & 0b1000 != 0

            # variable parameters unsupported, consider using `fromJson` in `__init__` directly
            if is_args and is_kwargs:
                __origin_init__(self, *args, **kwargs)
                return
            if is_args and not is_kwargs:
                __origin_init__(self, *args)
                return
            if is_kwargs and not is_args:
                __origin_init__(self, **kwargs)
                return

            # no extra json param
            if input_count == min_arg_count:
                __origin_init__(self, *args, **kwargs)
                return

            # check extra json param or exception
            if input_count == max_arg_count:
                # lookup json param in kwargs
                json_data = None
                for (key, val) in kwargs.iteritems():
                    if key not in varnames:
                        json_data = val
                        kwargs.pop(key)
                        break
                # lookup json param in args
                if not json_data and len(args) > 0:
                    json_data = args[-1]
                # check json param type
                if isinstance(json_data, basestring):
                    json_data = json.loads(json_data)
                if not isinstance(json_data, dict):
                    raise Exception("[error] invalid parameter or json format, expect dict or json string")
                __origin_init__(self, *args, **kwargs)
                fromJson(self, json_data)
                return

            # lookup extra json param or exception
            if min_arg_count < input_count < max_arg_count:
                # lookup json param in kwargs
                json_data = None
                for (key, val) in kwargs.iteritems():
                    if key not in varnames:
                        json_data = val
                        kwargs.pop(key)
                        break
                if not json_data:
                    __origin_init__(self, *args, **kwargs)
                    return
                if isinstance(json_data, basestring):
                    json_data = json.loads(json_data)
                if not isinstance(json_data, dict):
                    raise Exception("[error] invalid parameter or json format, expect dict or json string")
                __origin_init__(self, *args, **kwargs)
                fromJson(self, json_data)
                return

            # incorrect param count
            raise Exception("[error] invalid parameter count, expect " + str(min_arg_count) + ", got " + str(len(args)))

        def fromJson(self, data):
            """ json key_value model"""
            for key in self.__dict__:
                custom_key = key
                if key in customKeyMap:
                    custom_key = customKeyMap[key]
                if custom_key in data:
                    if isinstance(data[custom_key], dict) and key in objectMap:
                        obj = self.__dict__[key] = objectMap[key]()
                        obj.fromJson(data[custom_key])
                    elif isinstance(data[custom_key], (list, tuple)) and key in listClassMap:
                        tempList = []
                        for item in data[custom_key]:
                            obj = listClassMap[key]()
                            obj.fromJson(item)
                            tempList.append(obj)
                        self.__dict__[key] = tempList
                    else:
                        self.__dict__[key] = data[custom_key]
                else:
                    print("JsonModel log : [" + key + " --> " + custom_key + "] not in json data")

        def toKeyValue(self):
            """ model to json key_value """
            tempDic = {}
            for key in self.__dict__:
                custom_key = key
                if key in customKeyMap:
                    custom_key = customKeyMap[key]

                if key in objectMap:
                    obj = self.__dict__[key]
                    tempDic[custom_key] = obj.toKeyValue()
                elif key in listClassMap:
                    tempList = []
                    for item in self.__dict__[key]:
                        obj = item.toKeyValue()
                        tempList.append(obj)
                    tempDic[custom_key] = tempList
                else:
                    tempDic[custom_key] = self.__dict__[key]
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

        __origin_init__ = cls.__init__
        cls.__init__ = __hack_init__
        cls.fromJson = fromJson
        cls.toKeyValue = toKeyValue
        cls.objectArrayFromJsonArray = objectArrayFromJsonArray
        cls.objectArrayToJsonArray = objectArrayToJsonArray

        return cls

    return decorate
