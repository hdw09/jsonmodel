# Python Json to Model

## 1.Python 需要json2model吗？

最近用Python写crash监控预警系统，系统在最开始时，加载请求一个监控需要的配置接口。接口返回一个Json结构的数据，如下：

```python
{
    "projectName": "X项目",
    "projectID": "xproject",
    "administrator": "huangdawei@163.com",
    "threshold":30,
    "type":"iOS",
    "needCreateTask":false, 
    "flowTaskName":"FLOWPEO",
    "channels": [
      {
        "channelName": "平台业务",
        "channelID": " PlatPlugin",
        "manager": "huangdawei@163.com",
        "threshold":5
      },
      {
        "channelName": "用户评论回复",
        "channelID": " disPlugin",
        "manager": "huangdawei@163.com",
        "threshold":5
      }
    ],
    "members": [
      {
        "misID": "huagndawei@meituan.com",
        "channelID": "FoodPlugin",
        "type": "rd"
      },
      {
        "misID": "huangdawei@163.com",
        "channelID": "NAN",
        "type": "qa"
      },
      {
        "misID": "huangdawei@163.com",
        "channelID": "NAN",
        "type": "leader"
      }
    ]
  }
```

在使用Java和swift开发时，从接口拿到数据后，紧接着就把它转换为实体类。通过实体类的属性去访问各个信息字段。这样做不仅对IDE友好，输入一个`.`自动提示有哪些属性。而且可以避免由于拼写造成的crash ，如`project['members']`写作`project['mmembers']`。但是Python里默认没有相应的转换功能，我们在写代码时一般如下面这样：

```python
if respond.status_code == 200:
    self.projectConfig = respond.json()
# self.projectConfig 是一个字典(key_value)
```

于是就有一大堆的 `if x in X`的判断代码，比如：

```python
if 'channels' in self.projectConfig and len(self.projectConfig['channels']) > 0:
    for channel in self.projectConfig['channels']:
```

不使用实体类的另外一个缺点就是不能抽象的描述数据，不能将相关的方法与数据结合。比如我们用`for channel in self.projectConfig['channels']`取出来的channel不是一个对象，这在写代码的时候会十分难受，有一大推的本应该封装在"Channel类“中的操作被放在高层，比如：

```python
def findFirstLevelUsers(self):
        if 'members' in self.mainProject and len(self.mainProject['members']) > 0:
            return map(lambda member: member['misID'],
                       filter(lambda member: member['type'] == 'rd' or member['type'] == 'qa',
                              self.mainProject['members']))
        else:
            return []
"""
这个函数本应该封装在project中，现在要放在预警处理类中，造成预警处理类逻辑很多。程序整体的封装和内聚都很差
"""
```

所以把json对象对应的字典变成实体类，应该是一个常规需求，在Python中应该也有现成的解决办法。但是由于接触Python时间不长，没有在网上找到十分令人满意的转换方法。

## 2.现有的json2model方法或框架

搜索到最多的方案是：

```python
class MyClass:  
    #初始化  
    def __init__(self):  
        self.a=2  
        self.b='bb' 
        
myClass2 = MyClass()
myClass2.__dict__ = json.loads(myClassJson)
```

这种方法有一个很严重的缺陷，就是实体类无法嵌套定义，比如`MyClass`中包含`OtherClass`类的属性就不行了。 可以使用下面方法解决这个问题：

```python
load = json.loads(dump,object_hook = dict2object)
```

但是要每个类都要写一个`object_hook`函数，对开发人员带来的负担很大。这个问题如此明显，网上应该有相应的框架做了这个事情才对，但不知道是不是我搜索关键词的问题，在github上搜索`json model`，真的没一个好用的，于是索性自己写一个。（PS:我没有专门深入找过相应的框架，觉得很简单就自己写了，如果有现有的好用的库还请告诉我，多谢）

## 3.Python Json to Model实现

这种框架在Android和iOS上十分泛滥，各种优缺点的框架都有。总的来说满足`代码侵入性低`、`易用性强`、`稳定性高`这三点的框架都是好框架。

* 代码代码侵入性低是指，不要让用户非得继承框架中的某个BaseModel，不要让用户添加或重写某种转换方法
* 易用性是指让用户非常方便的描述一个对象成员所属的类是哪个，对象数组成员中数组元素所属的类是哪个。（这两点，是所有框架都必须要的，因为无论框架做的再好都要让用户告诉程序这两个信息）
* 稳定性是指，一个来自文件或网络的json格式是不确定的，框架要保证无论json里面是啥，程序都能正常运行，不崩溃，合理的告诉用户哪里有问题

我写了一个叫JsonModel的小框架，用法大概就如下这样。大家看看是不是满足上面三个特性

```python
import json
from jsonModel import jsonModel

@jsonModel()
class Pet(object):

    def __init__(self):
        self.name = ""

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

```

用户通过修饰符对实体类进行修饰就行了，对用户代码的侵入性很低。如果用户想要更换解析框架只要把修饰去除就好了。通过可选的objectMap={}, listClassMap={}参数很简单就可以对映射做出描述。

最后大家看代码吧，总共不超过60行就搞定了，如果大家喜欢给个星星吧~

github链接（https://github.com/hdw09/jsonmodel）。

在使用的过程中有发现需要添加两个针对数组的方法，补充进来，更新的示例如下：

```python
jsonListString = """[{
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
},{
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
},{
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
}]"""


"""
通过调用描述符动态生成Person的类方法objectArrayFromJsonArray()
可以吧json list 直接转换为object list 
"""
personList = Person.objectArrayFromJsonArray(json.loads(jsonListString))
print(personList)
print(json.dumps(personList[0].toKeyValue()))

"""
通过调用描述符动态生成Person的类方法objectArrayToJsonArray()
可以反过来吧object list 转换为 json keyvalue list
"""
print(json.dumps(Person.objectArrayToJsonArray(personList)))
```

