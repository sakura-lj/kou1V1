from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand
from nonebot import get_bot
import os
import json
import sys
import re
from datetime import datetime

# 从文件中读取群号、关键词和QQ号
try:
    data_path = os.path.join(os.path.dirname(sys.executable), 'data.json')
    print(f"当前读取的json文件路径是: {data_path}")
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'group' in data and 'keyword' in data and 'qq' in data and 'start_date' in data:
                group_ids = data.get('group', [])
                keywords = data.get('keyword', [])
                YOUR_QQ_NUMBER = data.get('qq')
                send_word = data.get('send_word')
            else:
                print("Error: data.json does not contain 'group', 'keyword' or 'qq'.")
                sys.exit(1)
except Exception as e:
    print(f"Error reading data: {e}")
    sys.exit(1)

bot = get_bot()

# 定义查询信息的命令处理函数
@on_command('get_info', aliases=('查询信息',), only_to_me=False)
async def get_info(session: CommandSession):
    await session.send(f'当前关键词列表为：{keywords}\n当前QQ号为：{YOUR_QQ_NUMBER}')

# 定义处理群聊消息的函数
@bot.on_message('group')
async def handle_group_message(ctx):
    global keywords
    global group_ids
    global YOUR_QQ_NUMBER
    global send_word

    group_id = ctx['group_id']
    if str(group_id) not in group_ids:  # 如果这个群不在目标群聊列表中，就跳过这条消息
        print("这个群不在目标群聊列表中")
        return
    message = ctx['message']  # 获取 Message 对象

    message_text = str(message)  # 将 Message 对象转换为字符串

    for keyword in keywords:
        if re.search(keyword, message_text, re.IGNORECASE):  # 使用正则表达式进行匹配，忽略大小写
            sender_id = ctx['sender']['user_id']
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取当前时间

            print(f'关键字 "{keyword}" 在 "{message}"找到. 尝试发送到 QQ "{YOUR_QQ_NUMBER}".')
            try:
                group_info = await bot.get_group_info(group_id=group_id)
                group_name = group_info['group_name']

                sender_info = await bot.get_stranger_info(user_id=sender_id)
                sender_nickname = sender_info['nickname']

                print(f'群名: {group_info}')
                print(f'发送者qq号: {sender_info}')
            except Exception as e:
                print(f'获取群名或者昵称错误: {e}')
                continue

            try:
                # 在群聊中回复“1”
                await bot.send_group_msg(group_id=group_id, message=f'{send_word}')
                # 将消息转发至反馈QQ号
                for _ in range(3):
                    await bot.send_private_msg(user_id=YOUR_QQ_NUMBER,
                                               message=f'群名称: {group_name}\n发送者: {sender_nickname} (QQ: {sender_id})\n发送时间: {time}\n消息: {message}\n已对这个任务扣{send_word}，请核对行程看是否撤回！')
                print('Message sent successfully.')
            except Exception as e:
                print(f'Error sending message: {e}')