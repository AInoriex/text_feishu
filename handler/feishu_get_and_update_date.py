import requests
import json
import os
from database.feishu_model import Fields
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# 飞书开放平台 API 的 URL
API_URL = os.getenv("API_URL")
# 替换为你自己的 App ID 和 App Secret
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# 获取 tenant_access_token
def get_tenant_access_token() -> str:
    """
    
    """
    url = f"{API_URL}auth/v3/tenant_access_token/internal/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("tenant_access_token")
    else:
        print("获取 tenant_access_token 失败")
        return None

# 从多维数据表读取数据,并进行校验是否唯一
def get_data_from_multidimensional_sheet(tenant_access_token:str, channel_urls:str, dicts:Fields) -> str:
    app_token = os.getenv("APP_TOKEN")
    table_id = os.getenv("TABLE_ID")
    url = f"{API_URL}bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "view_id": os.getenv("VIEW_ID")
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        links = []
        record_ids = []
        total = response_data['data']['total']  # 获取列表数量用于遍历
        for i in range(0,total):
            record_id = response_data['data']['items'][i]['record_id']
            fields = response_data['data']['items'][i].get('fields',{})
            if '文本' in fields:
                link = fields['文本']['link']
                if link == channel_urls:
                    links.append(link)
                    record_ids.append(record_id)
        if len(links) >= 2 and len(record_ids) >= 2:
            return None
        else:
            record_id = record_ids[0]
            insert_or_update_data_to_multidimensional_sheet(tenant_access_token, record_id, dicts)
            return record_id
    else:
        print(f"从多维数据表获取数据失败: {response.text}")
        return []

# 向数据表插入数据
def insert_or_update_data_to_multidimensional_sheet(tenant_access_token:str, record_id:str, dicts:Fields) -> str:
    """
    
    """
    if record_id:
        app_token = os.getenv("APP_TOKEN")
        table_id = os.getenv("TABLE_ID")
        url = f"{API_URL}bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        # update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "fields": {
                "状态": dicts.status
            }
        }
        response = requests.put(url, headers=headers, json=body)
        if response.status_code == 200:
            print("数据插入成功")
            return ("数据插入成功")
        else:
            print(f"数据插入失败: {response.text}")
            return (f"数据插入失败: {response.text}")
    else:
        print(f"没有获取到{record_id}, 请检查")
        return (f"没有获取到{record_id}, 请检查")

if __name__ == "__main__":
    
    # 获取 tenant_access_token
    tenant_access_token = get_tenant_access_token()
    channel_urls = "https://www.youtube.com/@TVItalia"

    if tenant_access_token:
        # 替换为你的飞书多维数据表的 app_token
        app_token = os.getenv("APP_TOKEN")
        table_id = os.getenv("TABLE_ID")
        data = Fields()
        record_id = get_data_from_multidimensional_sheet(tenant_access_token, channel_urls, data)
        print(record_id)
        