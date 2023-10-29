from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import ssl
import time
import logging

# logging.basicConfig(level=logging.DEBUG)
ssl._create_default_https_context = ssl._create_unverified_context

bot_token=''
channel_id=''

def get_yesterday_timestamp():
    now = int(time.time())
    now_tuple = time.localtime(now)
    year = now_tuple.tm_year
    month = now_tuple.tm_mon
    day = now_tuple.tm_mday
    
    yesterday = day - 1
    
    from time import struct_time
    yesterday_tuple = struct_time((year, month, yesterday, 0, 0, 0, 0, 0, 0))
    yesterday_stamp = int(time.mktime(yesterday_tuple))
    
    return yesterday_stamp

def delete_msg(ts):
    client = WebClient(token=bot_token)
    history = client.conversations_history(
        channel=channel_id,
        latest=ts
        )
    if len(history['messages'])<10:
        print('不足10个消息了,不删除')
        return 
    for msg in history['messages']:
        try:
            result = client.chat_delete( channel=channel_id, ts = msg.get('ts'))
            print(result)
        except SlackApiError as e:
            print(f"Error deleting message: {e}")

ts = get_yesterday_timestamp()
delete_msg(ts)
