import subprocess

from database.ytb_model import Video

def yt_dlp_read_url_from_file(url:str, language:str="") -> list:
    """
    使用 yt-dlp 从指定的 YouTube 频道页面 URL 中提取视频信息。  
    :param url: YouTube 频道页面的 URL - 例如:https://www.youtube.com/@Nhyxinhne/videos     
    :param language (str, optional) - 语言代码. Defaults to "".     
    :return: List[Video,Video]] - 返回包含视频网页链接和时长的列表.格式为   
        (Video(vid=None, position=1, source_id=UCgdiE5jT-77eUMLXn66NLCQ, source_type=3, source_link=https://www.youtube.com/watch?v=XYjL_pXK8V8, duration=328, cloud_type=0, cloud_path=None, language=None, status=0, `lock`=0, info={}))
    """
    # 目前下载的主要是 webpage_url 和 duration , playlist_channel_id 三个字段信息，使用 yt-dlp 命令获取视频网页链接和时长
    command = f'yt-dlp --flat-playlist --print "%(webpage_url)s %(duration)s %(playlist_channel_id)s" --sleep-requests 1.5 -v {url}'
    output_lines = []
    # 使用 Popen 捕获 yt-dlp 输出
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True, encoding="utf-8")
    for line in process.stdout:
        # print(line, end='')
        if line.startswith("https://www.youtube.com"):
            line = str(line.strip().split('\n')[0])
            output_lines.append(line)
    process.wait()
    # 错误检查
    if process.stderr:
        error_message = process.stderr.decode('utf-8').strip()
        raise ValueError(f"yt-dlp解析失败, {error_message}")
    output_list = []
    for line in output_lines:
        # 检查每行数据并解析网页链接和视频时长
        parts = line.split(' ')
        if len(parts) >= 3:
            video_url = parts[0]
            duration = int(float(parts[1])) if parts[1] != 'NA' else 0
            channel_id = parts[2]
            output_list.append(Video(source_link=video_url, duration=duration , source_id=channel_id, language=language, blogger_url=url))
        else:
            print(f"Warning: 无法解析数据行: '{line}'")
    print(f"共获取到 {len(output_list)} 条视频数据")
    
    return output_list

if __name__ == '__main__':
    url = 'https://www.youtube.com/@TheDoShow0909/videos'
    lang = 'text'
    a = yt_dlp_read_url_from_file(url, lang)
    print(a)