import time
import logging
import multiprocessing
from datetime import datetime
from flask import Flask, jsonify, request
from database import feishu_model
from handler.yt_dlp_save_url_to_file import yt_dlp_read_url_from_file
from handler.feishu_get_and_update_date import get_data_from_multidimensional_sheet, insert_or_update_data_to_multidimensional_sheet, get_tenant_access_token

app = Flask(__name__)
# 设置日志配置
logging.basicConfig(level=logging.INFO)

# 定义一个简单的路由，响应 HTTP 请求
@app.route('/hello', methods=['GET'])
def hello():
    return "Hello, World!"

@app.route('/api/v1/tasks/scrape/youtube', methods=['POST'])
def start_scraper():
    try:
        if request.method == 'POST':
            # 获取请求体中的 JSON 数据
            json_data = request.json
            # 检查必需的参数是否存在
            if not json_data:
                return jsonify({"错误": "没有提供正确的请求体"}), 400
            # 获取参数
            channel_urls = json_data.get("channel_urls")
            target_language = json_data.get("target_language")
            # 如果缺少任何必需的参数，返回错误响应
            if not channel_urls:
                return jsonify({"错误": "找不到 'channel_urls' 参数"}), 400
            if not target_language:
                return jsonify({"错误": "Missing 'target_language' 参数"}), 400
            # 获取飞书参数
            tenant_access_token = get_tenant_access_token()
            feishu_data = feishu_model.Fields()
            # 检查channel_urls飞书记录是否重复 并且获取 record_id 值
            record_id = get_data_from_multidimensional_sheet(tenant_access_token, channel_urls, feishu_data)  # 已更改，第二版
            if record_id:
                logging.info(f"Received request with channel_urls: {channel_urls} and target_language: {target_language}")
            else:
                logging.info("重复值")
                return jsonify({"错误": f"已存在{channel_urls}, 重复值"}), 404
            return jsonify({
                "status": "success",
                "channel_urls": channel_urls,
                "target_language": target_language,
                "record_id": record_id
            })
    except Exception as e:
        # 捕获异常并记录
        logging.error(f"发生错误: {str(e)}")
        return jsonify({"错误": "服务器错误，请稍后再试"}), 500

if __name__ == '__main__':
    # 运行 Flask 应用，默认会在 localhost:5000 启动
    # app.run(debug=True, host='0.0.0.0', port=443, ssl_context=('server.crt', 'server.key'))
    app.run(debug=True, host='0.0.0.0', port=5000)