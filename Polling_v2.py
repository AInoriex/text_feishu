import threading
import requests
import time
import os
from datetime import datetime
from database.feishu_model import Fields
from database.feishu_data_Inbound import ytb_main
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file
from handler.feishu_get_and_update_date import get_tenant_access_token, get_data_from_multidimensional_sheet
from dotenv import load_dotenv
load_dotenv()

# 读取飞书信息是否获取全，例如监听某个单元格，看看是否有值的变化或者标识，然后获取对应的record_id值来进行入库操作以及入库后更新表格操作
# 从多维数据表读取数据
def update_status(tenant_access_token:str, record_id:str, dicts:Fields = "正在处理..."):
    if record_id:
        app_token = os.getenv("APP_TOKEN")
        table_id = os.getenv("TABLE_ID")
        url = f'{os.getenv("API_URL")}bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}'
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "fields": {
                "视频数量（条）": dicts.video_num,
                "视频时长（秒）": dicts.duatrtion_sum,
                "采集结束更新时间": dicts.update_time,
                "状态": dicts.status
            }
        }
        response = requests.put(url, headers=headers, json=body)
        if response.status_code == 200:
            print("数据插入成功")
            return "数据插入成功"
        else:
            return {f"数据插入失败: {response.text}"}
    else:
        return "没有获取到  record_id  值"

def main(tenant_access_token:str) -> str:
    app_token = os.getenv("APP_TOKEN")
    table_id = os.getenv("TABLE_ID")
    url = f'{os.getenv("API_URL")}bitable/v1/apps/{app_token}/tables/{table_id}/records/search'
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "view_id": os.getenv("VIEW_ID")
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        if response.status_code == 200:
            response_data = response.json()
            for i in response_data['data']['items']:
                fields = i.get('fields', {})
                record_id = i.get('record_id', None)
                if '文本' not in fields:  # 排除出现空记录的情况, 就是在数据表上直接操作的情况！！！
                    print(f"此记录 {record_id} 无视频链接, 为空记录")
                    continue
                if '状态' in fields and fields.get('状态', {})[0]['text'] == "已完成":
                    print(f"此记录 {record_id} 已完成")
                if '状态' in fields and fields.get('状态', {})[0]['text'] == "正在处理...":
                    print(f"此记录 {record_id} 正在处理, 请稍后!!!")
                if '状态' in fields and fields.get('状态', {})[0]['text'] == "待处理...":
                    print(f"此记录 {record_id} 正在等待处理, 请稍后!!!")
                    channel_url = fields.get('文本')['link']
                    status = Fields(status="正在处理...")
                    update_status(tenant_access_token, record_id, status)
                    videos = yt_dlp_read_url_from_file(channel_url)
                    # 获取视频总时长(s)
                    total_duration = sum([int(video_info.duration) for video_info in videos])
                    # 统计总视频数量
                    total_count = len(videos)
                    ytb_main(videos, total_count)
                    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                    data = Fields(
                        video_num=total_count,
                        duatrtion_sum=total_duration,
                        update_time=update_time,
                        status="已完成"
                    )
                    update_status(tenant_access_token, record_id, data)
    except Exception as e:
        print(f"主处理函数发生错误: {str(e)}")


















if __name__ == '__main__':
    while True:
        threading.Thread(target=main, args=(get_tenant_access_token(),)).start()
        time.sleep(10)