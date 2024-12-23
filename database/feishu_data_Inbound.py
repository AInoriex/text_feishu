import os
import re
import sys
import uuid
import time
import multiprocessing
from utils.logger import init_logger
from utils import logger
from utils.ip import get_local_ip, get_public_ip
from utils.lark import alarm_lark_text
from utils.utime import get_now_time_string, format_second_to_time_string
from database import ytb_api_v2
from database import ytb_model
from json import dumps
from dotenv import load_dotenv
load_dotenv()

local_ip = get_local_ip()
public_ip = get_public_ip()
logger = init_logger('feishu_data_Inbound')

def get_ytb_blogger_url(video_url:str, duration:int, language:str, task_id:str, source_id:str, )->ytb_model.Video:
    ''' 格式化视频信息为数据库模型 
    @Paras video_url: 博主url;eg:"https://www.youtube.com/@failarmy/videos"
    @Return [Video]
    '''
    if video_url.split('//')[1].split('/')[1].startswith('playlist'):
        pattern = r'list=([^&]+)'
        vid = re.search(pattern, video_url).group().split('=')[1].split(' ')[0]
        print('希望不会炸, 希望不会炸')
    elif video_url.split('//')[1].split('/')[1].startswith('watch'):
        pattern = r'v=([^&]+)'
        vid = re.search(pattern, video_url).group().split('=')[1].split(' ')[0]
    else:
        print("yt_dlp -> 解析的video_url不匹配")
    info_dict ={}
    info_dict['cloud_save_path'] = ""
    info_dict['task_id'] = task_id
    info = dumps(info_dict)

    db_video = ytb_model.Video(
        id=int(0),
        vid="ytb_" + vid,
        position=int(3),
        source_type=int(3),
        cloud_type=int(0),
        cloud_path="",
        source_link=video_url,
        language=language,
        duration=duration,
        info=info,
        source_id=source_id
    )
    return db_video

def import_data_to_db_pip(video_urls:ytb_model.Video, pool_num:int, pid:int, task_id:str):
    """
    油管信息导入数据库

    :param video_urls: 视频信息 Video(tuple, tuple, ...)
    :param pool_num: 线程编号
    :param spend_scrape_time: 采集总时间
    :param pid: 进程ID
    :param task_id: 任务ID
    """
    # 数据导入数据库
    index = 0
    for video_info in video_urls:
        index += 1
        # print(video_info)
        try:
            # logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 开始处理第{index}个数据: {video_info.source_link}")
            # time_st = time.time()
            video_object = get_ytb_blogger_url(
                # file_name = channel_url_name,
                video_url=video_info.source_link,
                language=video_info.language,
                duration=video_info.duration,
                task_id=task_id,
                source_id=video_info.source_id,
            )
            # print(video_object)
            # 将数据更新入库
            # ytb_api.create_video(video_object)
            ytb_api_v2.sign_database(video_object)  # 用于测试
            # print(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据: {video_object.source_link}")
            time.sleep(0.5)

        #     # 日志记录
        #     time_ed = time.time()
        #     spend_time = time_ed - time_st
        #     logger.info(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据: {video_object.source_link} 完毕, 花费时间: {spend_time} seconds")
        #     # alarm to Lark Bot
        #     now_str = get_now_time_string()
        #     notice_text = f"[Youtube Scraper | DEBUG] 数据已采集入库. \
        #         \n\t进程ID: {pid} \
        #         \n\t任务ID: {task_id} \
        #         \n\t频道信息: {video_object.language} | {video_info.blogger_url} \
        #         \n\t线程信息: {f'第{pool_num}个进程, 处理第{index}个数据: {video_object.source_link}'} \
        #         \n\t共处理了{format_second_to_time_string(spend_time)} \
        #         \n\tIP: {local_ip} | {public_ip} \
        #         \n\tTime: {now_str}"
        #     alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
        # except Exception as e:
        #     # continue_fail_count += 1
        #     logger.error(f"import_data_to_db_pip > 第{pool_num}个进程, 处理第{index}个数据 {video_object.source_link} 失败, {e}")
        #     # logger.error(e, stack_info=True)
        #     # alarm to Lark Bot
        #     notice_text = f"[Youtube Scraper | ERROR] 数据采集入库失败 \
        #         \n\t进程ID: {pid} \
        #         \n\t任务ID: {task_id} \
        #         \n\t频道信息: {video_object.language} | {video_object.blogger_url} \
        #         \n\t线程信息: {f'我是第{pool_num}个进程, 处理第{index}个数据: {video_object.source_link}'} \
        #         \n\tError: {e} \
        #         \n\tIP: {local_ip} | {public_ip} \
        #         \n\tTime: {now_str}"
        #     alarm_lark_text(webhook=os.getenv("NOTICE_WEBHOOK"), text=notice_text)
            # continue
            # 失败过多直接退出
            # if continue_fail_count > LIMIT_FAIL_COUNT:
            #     logger.error(f"Scraper Pipeline > pid {pid} unexpectable exit beceuse of too much fail count: {continue_fail_count}")
            #     exit(1)
        except KeyboardInterrupt:
            logger.warning(f"Scraper Pipeline > pid {pid} interrupted processing, exit.")
            pool_num.terminate()  # 直接终止所有子进程
            sys.exit(1)  # 退出程序
            raise KeyboardInterrupt
        finally:
            #time.sleep(1)
            pass

def ytb_main(channel_urls:list, total_count):
    pid = os.getpid()  # 捕获进程
    task_id = str(uuid.uuid4())  # 获取任务ID
    try:
        # 使用多进程处理video_url_list入库 # 创建进程池
        with multiprocessing.Pool(5) as pool:
            # 将列表分成5个子集，分配给每个进程
            # chunks = np.array_split(target_youtuber_blogger_urls, 5)
            chunk_size = len(channel_urls) // 5
            chunks = [channel_urls[i:i + chunk_size] for i in range(0, total_count, chunk_size)]
            # print(chunks)
            # 列表的长度可能会有剩余的元素，我们将它们分配到最后一个子集中
            if len(chunks) < 5:
                chunks.append(channel_urls[len(chunks)*chunk_size:])
            # 启动进程池中的进程，传递各自的子集和进程ID
            for pool_num, chunk in enumerate(chunks):
                pool.apply_async(import_data_to_db_pip, (chunk, pool_num, pid, task_id))
                time.sleep(0.5)
            pool.close()
            pool.join()  # 等待所有进程结束
            # 频道通知开始
    except KeyboardInterrupt:
        # 捕获到 Ctrl+C 时，确保终止所有子进程
        logger.warning("KeyboardInterrupt detected, terminating pool...")
        pool.terminate()
        sys.exit()  # 退出主程序
            

if __name__ == '__main__':
    ytb_main()