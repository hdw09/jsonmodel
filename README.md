# Python Json to Model

## 1.写这个工具的背景

最近用Python写crash监控预警系统，系统在最开始加载时请求一个监控需要的配置接口，接口返回一个Json结构的数据，如下：

```python
{
    "projectName": "X项目",
    "projectID": "xproject",
    "administrator": "huangdawei@163.com",
    "threshold":30,
    "type":"iOS",// 项目类型  iOS Android
    "needCreateTask":false, // 新crash是否需要创建task
    "flowTaskName":"FLOWPEO",// 项目在flow上的名字，开task需要
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

在Android和iOS开发中我们从接口拿到数据后，紧接着就把它转换为实体类，通过实体类的属性去访问各个配置信息。这样最大的好处就是IDE会帮我们提示，输入一个`.`自动提示有哪些属性，并且避免由于拼写造成的crash ，如`project['mmembers']`。但是Python里竟然没有相应的转换功能，只好如下面这样：

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

而且我们用`for channel in self.projectConfig['channels']`取出来的channel不是一个对象，这很难受啊，于是有一大推的本应该封装在"Channel类“中的操作被放在高层，比如：

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

所以把json对象对应的字典变成实体类，不仅应该是Android和iOS中常见的操作，应该是所有语言都要有的特性。Python应该也不会例外，but，Python刚学，不熟啊，只好网上搜一搜

## 2.网上搜索结论

网上一搜,最多的方案是：

```python
class MyClass:  
    #初始化  
    def __init__(self):  
        self.a=2  
        self.b='bb' 
        
myClass2 = MyClass()
myClass2.__dict__ = json.loads(myClassJson)
```

这种方法很明显不行，比如`MyClass`中包含`OtherClass`类的属性就不行了, 可以使用下面方法解决这个问题

```python
load = json.loads(dump,object_hook = dict2object)
```

但是要每个类都写一个`object_hook`函数，烦都烦死啦。那用网上的框架怎么样呢？

不知道是不是我关键词不对，在github上搜索`json model`，真的没一个好用的，算了，还是自己写一个吧

## 3.Python Json to Model

这种框架在Android和iOS上十分泛滥，各种优缺点的框架都有。总的来说满足`代码侵入性低`、`易用性强`、`稳定性高`这三点的框架都是好框架。

* 代码代码侵入性低是指，不要让用户非得继承框架中的某个BaseModel，不要让用户添加或重写某种转换方法
* 易用性是指让用户非常方便的描述一个对象成员所属的类是哪个，对象数组成员中数组元素所属的类是哪个。（这两点，是所有框架都必须要的，因为无论框架做的再好都要让用户告诉程序这两个信息）
* 稳定性是指，一个来自文件或网络的json格式是不确定的，框架要保证无论json里面是啥，程序都能正常运行，不崩溃，合理的告诉用户哪里有问题

我写了一个叫JsonModel的小小框架，用法大概就如下这样。大家看看是不是满足上面三个特性

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

github链接（https://github.com/hdw09/jsonmodel）