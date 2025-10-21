# 基于LLtworobot框架并用Websockets正向代理的QQ机器人--酪氨酸

# 调用库
import uuid
import asyncio
import websockets
import json
from openai import OpenAI
import random
from datetime import datetime


# 一般配置项
uri = " "  # 替换为你的 LLOneBot WebSocket 正向地址
qq = " "  # 机器人的qq账号
group_id = " " # 群号
my_api_key = " "  # ai回复的API_KEY
my_base_url = " "  # 代理地址
max_message = 5 # 机器人消息记忆储存数额，越高token消耗越快
robot_background = "" "" # 发送的图片URL

#创建一些要用到的变量
ai_messages = [
    {'role': 'system', 'content': robot_background}
]

dk_list = [

]#['user':xxx,'length':10]
last_clear_date = datetime.now().date()
async def receive_messages(ws):  # 循环接收消息
    while True:
        message = await ws.recv()
        message_data = json.loads(message)# 将字符串解析为字典
        if message_data.get('message_type') == 'group':
            print(f"""
        ----------------------"消息类型":{message_data.get('message_type', 'Unknown')}----------------------
        \n“收到消息”: {message}
        ---------------------------------------------------------------------------------------------------       
        """)
        elif message_data.get('post_type') == 'meta_event':
            print(f"""
        ----------------------"消息类型":meta_event---------------------------------------------------------
        \n“收到消息”: {message}
        ---------------------------------------------------------------------------------------------------       
        """)
        else:
            print(f"""
        ----------------------"消息类型":其他---------------------------------------------------------
        \n {message}
        ---------------------------------------------------------------------------------------------------       
        """)
        return message_data


async def main():  # 循环发送消息
    async with websockets.connect(uri) as websocket:
        echo_like = None
        while True:
            receive_data = await receive_messages(websocket)
            if receive_data.get('post_type') == 'meta_event' and receive_data.get('sub_type') == 'connect':
                print('邦邦卡邦，酪氨酸启动完成，ο(=•ω＜=)ρ⌒☆')
            check_and_clear_dk_list()#检查并清除字典
            #处理群一般消息
            if (receive_data.get('post_type') == 'message' and
                    receive_data.get('message_type') == 'group' and
                    receive_data.get('group_id') and
                    str(receive_data['group_id']) == group_id):
                if 'message' in receive_data:
                    messages = receive_data['message']
                    if messages:
                        for i in range(0, len(messages)):  # 遍历消息段
                            if messages[i]['type'] == 'at' and messages[i]['data']['qq'] == qq:

                                if (receive_data['message'][i + 1].get('data') and receive_data['message'][i + 1].get('data').get('text') and
                                    receive_data['message'][i + 1].get('data').get('text').startswith(' #luck')):#luck指令
                                    if any(user['user'] == receive_data['sender']['nickname']  for user in dk_list):
                                        length = get_user_length(receive_data['sender']['nickname'])
                                        echo = str(uuid.uuid4())
                                        data = {
                                            "action": "send_group_msg",
                                            "params": {
                                                "group_id": group_id,
                                                "message": f"你已经抽过啦，今日的牛牛长度为{length}cm"
                                            },
                                            'echo': echo
                                        }
                                        await websocket.send(json.dumps(data))
                                    else:
                                        dk_response_message = dk(receive_data['sender']['nickname'])
                                        echo = str(uuid.uuid4())
                                        data = {
                                            "action": "send_group_msg",
                                            "params": {
                                                "group_id": group_id,
                                                "message": dk_response_message
                                            },
                                            'echo': echo
                                        }
                                        await websocket.send(json.dumps(data))

                                elif (receive_data['message'][i + 1].get('data') and receive_data['message'][i + 1].get('data').get('text') and
                                    receive_data['message'][i + 1].get('data').get('text').startswith(' #list_luck')):#list_luck指令
                                    if dk_list:
                                        #对dk_list内依据length大小进行排序
                                        dk_list.sort(key=lambda x: x['length'], reverse=True)
                                        # 格式化为字符串
                                        dk_list_str = "\n".join(
                                            [f" {item['user']}, {item['length']}cm" for item in dk_list])
                                        echo = str(uuid.uuid4())
                                        data = {
                                            "action": "send_group_msg",
                                            "params": {
                                                "group_id": group_id,
                                                "message": "今日牛牛排行榜如下:\n"+dk_list_str
                                            },
                                            'echo': echo
                                        }
                                        await websocket.send(json.dumps(data))

                                    else:
                                        echo = str(uuid.uuid4())
                                        data = {
                                            "action": "send_group_msg",
                                            "params": {
                                                "group_id": group_id,
                                                "message": "今天还没有人抽取幸运数字哦"
                                            },
                                            'echo': echo
                                        }
                                        await websocket.send(json.dumps(data))

                                elif (receive_data['message'][i + 1].get('data') and receive_data['message'][i + 1].get('data').get('text') and
                                    receive_data['message'][i + 1].get('data').get('text').startswith(' #help')):#help指令
                                    echo = str(uuid.uuid4())
                                    data = {
                                        "action": "send_group_msg",
                                        "params": {
                                            "group_id": group_id,
                                            "message": help_order()
                                        },
                                        'echo': echo
                                    }
                                    await websocket.send(json.dumps(data))


                                elif (receive_data['message'][i + 1].get('data') and receive_data['message'][i + 1].get('data').get('text') and
                                    receive_data['message'][i + 1].get('data').get('text').startswith(' #like')):#like指令
                                    try:
                                        echo = str(uuid.uuid4())
                                        data = {
                                            "action": "send_group_msg",
                                            "params": {
                                                "group_id": group_id,
                                                "message": "正在点赞中..."
                                            },
                                            'echo': echo
                                        }
                                        await websocket.send(json.dumps(data))

                                        echo_like = str(uuid.uuid4())
                                        data = {
                                            "action": "send_like",
                                            "params": {
                                                "user_id": receive_data['user_id'],
                                                "times": 10
                                            },
                                            'echo': echo_like
                                        }
                                        await websocket.send(json.dumps(data))
                                        print('点赞成功')


                                    except:
                                        echo = str(uuid.uuid4())
                                        data = {
                                            "action": "send_group_msg",
                                            "params": {
                                                "group_id": group_id,
                                                "message": "点赞失败喵qwq"
                                            },
                                            'echo': echo
                                        }
                                        await websocket.send(json.dumps(data))


                                else:#调用AI回答
                                    message_text = await ai_respond(receive_data.get('sender').get('nickname'), receive_data.get('message')[i + 1]['data']['text'])
                                    echo = str(uuid.uuid4())
                                    data = {
                                        "action": "send_group_msg",
                                        "params": {
                                            "group_id": group_id,
                                            "message": message_text
                                        },
                                        'echo': echo
                                    }
                                    await websocket.send(json.dumps(data))

            #处理点赞失败返回的消息
            if echo_like is not None:
                if receive_data.get('status') == 'failed' and receive_data.get('echo') == echo_like:
                    echo = str(uuid.uuid4())
                    data = {
                        "action": "send_group_msg",
                        "params": {
                            "group_id": group_id,
                            "message": "今天已经给你点过赞了，不能再点了喵"
                        },
                        'echo': echo
                    }
                    await websocket.send(json.dumps(data))
                if receive_data.get('status') == 'ok' and receive_data.get('echo') == echo_like:
                    echo = str(uuid.uuid4())
                    data = {
                        "action": "send_group_msg",
                        "params": {
                            "group_id": group_id,
                            "message": "点赞成功喵"
                        },
                        'echo': echo
                    }
                    await websocket.send(json.dumps(data))
            if (receive_data.get('post_type') == 'notice' and receive_data.get('notice_type') == 'notify' #当收到戳一戳时发图片
                    and receive_data.get('sub_type') == 'poke' and str(receive_data.get('target_id')) == qq
                    and str(receive_data['group_id']) == group_id):
                print("已触发图片发送")
                echo = str(uuid.uuid4())
                data = {
                    "action": "send_group_msg",
                    "params": {
                        "group_id": group_id,
                        "message":[{
                            "type":"image",
                            "data":{
                                "file": image_url
                            }
                        }]
                    },
                    'echo': echo
                }
                await websocket.send(json.dumps(data))
# 模拟ai回复,将用户的对话存入messages字典中
async def ai_respond(user, content):
    """模拟ai回复，将用户的对话存入messages字典中"""
    if not content or not user:
        return "酪氨酸没听清楚呢，能再说一遍吗喵？"

    try:
        loop = asyncio.get_event_loop()

        def sync_ai_call():
            client = OpenAI(
                api_key=my_api_key,
                base_url=my_base_url
            )

            ai_messages.append({'role': 'user', 'content': user + '说' + content})

            response = client.chat.completions.create(
                model="deepseek-v3",
                messages=ai_messages,
                stream=False
            )

            # 将AI所说的话添加到消息列表
            assistant_message = response.choices[0].message.content
            ai_messages.append({'role': 'assistant', 'content': assistant_message})

            # 当信息列表超过限制时，删除除设定外的最早两条信息
            if len(ai_messages) > max_message:
                del ai_messages[1:3]

            return response.choices[0].message.content

        return await loop.run_in_executor(None, sync_ai_call)

    except Exception as e:
        print(f'AI调用失败: {e}')
        return "酪氨酸现在有点忙，待会再陪你聊天喵~ (。・ω・。)"


# 幸运dk函数
def dk(sender):
    length = random.randint(-50, 50)
    dk_list.append({"user":sender,"length":length})
    if length <= 0:
        return sender+f"的牛牛长度为{length}cm，"+sender+"是女孩子捏"
    elif length <= 20:
        return sender+f"的牛牛长度为{length}cm"
    elif length > 20:
        return sender+f"的牛牛长度为{length}cm，WOW!"


def check_and_clear_dk_list():
    """检查并清除字典（在循环中调用）"""
    global dk_list, last_clear_date

    current_date = datetime.now().date()
    # 如果日期变化且是0点后，清除字典
    if current_date != last_clear_date and datetime.now().hour == 0:
        dk_list.clear()
        last_clear_date = current_date
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 已清空dk_list")

def get_user_length(username):
    """获取指定用户的长度"""
    for user_data in dk_list:
        if user_data['user'] == username:
            return user_data['length']
    return -100

def help_order():
    order = """以下是酪氨酸的常用命令列表喵(。・ω・。)
             #help:查询指令喵
             #luck:抽取今日幸运数字喵(可能会怪怪的哦)
             #list_luck:查询今日幸运榜单
             #like:给个人资料点赞喵"""
    return order

asyncio.run(main())