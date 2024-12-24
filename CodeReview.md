# Code Review

> Reviewer: `AInoriex`
>
> Date: 2024.12.24
>
> Branch: `main`
>
> Commit Hash: `276f5af810dadbf6fb440fdad29dd4f726604240`

## 亮点

1. 整体代码结构清晰，`handler`，`utils`分级管理调用
2. 该有的注释基本都有，代码可读性强
3. 使用 `.env` 配置变量
4. 变量命名大小写规范，意义明确



## 改善建议

1. 接口字段定义规范

   1. 接口`kv`值，`key`一般不以中文定义

      - https://github.com/AInoriex/text_feishu/blob/test_xyh/Polling_v2.py#L26

        ```python
        "fields": {
            "视频数量（条）": dicts.video_num,
            "视频时长（秒）": dicts.duatrtion_sum,
            "采集结束更新时间": dicts.update_time,
            "状态": dicts.status
        }
        ```

      - 【建议】`json`的key一般习惯以英文小写以及下划线命名，像`process_status`

   2. 接口`kv`值，`key`一般不以中文判断

      - https://github.com/AInoriex/text_feishu/blob/test_xyh/Polling_v2.py#L62

        ```python
        if '状态' in fields and fields.get('状态', {})[0]['text'] == "已完成":
        ```

      - https://github.com/AInoriex/text_feishu/blob/test_xyh/Polling_v2.py#L64

        ```python
        if '状态' in fields and fields.get('状态', {})[0]['text'] == "正在处理...":
        ```

      - https://github.com/AInoriex/text_feishu/blob/test_xyh/Polling_v2.py#L66

        ```python
        if '状态' in fields and fields.get('状态', {})[0]['text'] == "待处理...":
        ```

      - 【建议】如果是自己用可以不需要这么多条条框框；如果和同事合作协同开发，熟悉学习下 [Restful API 接口规范详解-腾讯云开发者社区-腾讯云](https://cloud.tencent.com/developer/article/2360813) 类似这种接口设计规范。

2. 字符串单双引号混用

   - https://github.com/AInoriex/text_feishu/blob/test_xyh/Polling_v2.py#L62

     ```python
     if '状态' in fields and fields.get('状态', {})[0]['text'] == "已完成":
     ```

   - https://github.com/AInoriex/text_feishu/blob/test_xyh/handler/feishu_get_and_update_date.py#L56

     ```python
     if '文本' in fields:
     	link = fields['文本']['link']
     ```

   - 【建议】我平时习惯统一双引号，单引号一般只用于多行字符串以及注释

     ```python
     def func():
     '''
     	this is comment
     '''
     	lines = f'''
     		string line 1
     		string line 2 
     	'''	
     ```

3. 函数声明返回值与实际返回值不符

   - https://github.com/AInoriex/text_feishu/blob/test_xyh/handler/feishu_get_and_update_date.py#L16

     ```python
     # handler\feishu_get_and_update_date.py:16
     def get_tenant_access_token() -> str:
     	# ...
         # handler\feishu_get_and_update_date.py:30
         return response.json().get("tenant_access_token")
         # handler\feishu_get_and_update_date.py:33
         return None
     ```

   - https://github.com/AInoriex/text_feishu/blob/test_xyh/handler/feishu_get_and_update_date.py#L36

     ```python
     # handler\feishu_get_and_update_date.py:36
     def get_data_from_multidimensional_sheet(tenant_access_token:str, channel_urls:str, dicts:Fields) -> str:
     	# ...
         	# handler\feishu_get_and_update_date.py:62
             return None
         	# handler\feishu_get_and_update_date.py:66
             return record_id
         # handler\feishu_get_and_update_date.py:69
         return []
     ```

   - 【建议】函数返回值尽量减少多种数据类型

4. 函数返回值类型混乱（string? or dict?）

   - https://github.com/AInoriex/text_feishu/blob/test_xyh/Polling_v2.py#L15

     ```python
     # Polling_v2.py:15
     def get_data_from_multidimensional_sheet(tenant_access_token:str, channel_urls:str, dicts:Fields) -> str:
     	# ...
         	# Polling_v2.py:35
             return "数据插入成功"
         	# Polling_v2.py:37
             return {f"数据插入失败: {response.text}"}
         # Polling_v2.py:39
         return "没有获取到  record_id  值"
     ```

   - 【建议】单个函数最好统一使用一种类型的返回值，即尽量以强语言来开发，减少因为数据类型出现意外情况而增加调试成本，额外的类型转换处理成本。

5. 日志可分level级别记录日志，并通过配置文件根据不同代码环境筛选输出记录日志。

   ```python
   logging.debug() # 测试环境, 预发环境，生产环境
   logging.info() # 预发环境，生产环境
   logging.error() # 预发环境，生产环境
   ```

   ​	【建议】`logging`不算很好用，个人推荐`loguru`。

6. 缩进范围过大，以及部分错误处理，临界范围考虑有疏忽

   - https://github.com/AInoriex/text_feishu/blob/test_xyh/Polling_v2.py#L53

     ```python
     try:
     	if response.status_code == 200:
             response_data = response.json()
             for i in response_data['data']['items']:
                 # ...
     except Exception as e:
     	print(f"主处理函数发生错误: {str(e)}")
     ```

   - 【建议】尽量减少缩进层级，同级缩进下代码行数不宜过多

     ```python
     try:
         if response.status_code != 200:
             raise ValueError("")
         for i in response_data['data']['items']:
             # xxxx
      except Exception as e:
     	print(f"主处理函数发生错误: {str(e)}")
     ```

   - 【建议】考虑好数据处理临界范围，对于意料之外的情况做好错误处理（return? raise error?）

   