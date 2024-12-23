class Fields:

    def __init__(
        self,
        video_num:int = 0,
        duatrtion_sum:int = 0,
        update_time:str = "",
        status:str = "待处理..."
        ):
        self.video_num = video_num
        self.duatrtion_sum = duatrtion_sum
        self.update_time = update_time
        self.status = status

    def __dict__(self):
        return {
            "视频数量（条）": self.video_num,
            "视频时长（秒）": self.duatrtion_sum,
            "采集结束更新时间": self.update_time,
            "状态": self.status
        }

    def __str__(self):
        return "sueecss"
    
if __name__ == '__main__':
    # fields = Fields(
    #     video_num=10,
    #     duatrtion_sum=100,
    #     update_time="2024-1-1",
    #     status="正在处理..."
    # )
    pass