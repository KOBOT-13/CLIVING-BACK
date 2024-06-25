from django.core.management.base import BaseCommand
from ...models import Page
import random
from datetime import datetime

class Command(BaseCommand):
    help = 'Create multiple Page entries in the database'

    def handle(self, *args, **kwargs):
        # 예시 데이터
        center_names = ['더클라임 클라이밍짐 홍대점', '피커스 클라이밍 종로점', '서울숲 클라이밍 뚝섬점']
        colors = ['pink', 'orange', 'blue', 'yellow', 'green', 'black']
        rand_colors = []

        for i in range(13):
            rand_colors.append('pink')
        for i in range(9):
            rand_colors.append('orange')
            rand_colors.append('blue')
        for i in range(4):
            rand_colors.append('yellow')
            rand_colors.append('green')
            rand_colors.append('black')

        random.shuffle(rand_colors)

        month_date = [[2, 8, 9, 15, 18, 19, 27, 29],
                      [5, 8, 9, 13, 14, 15, 22, 25, 26],
                      [3, 5, 7, 28, 31],
                      [3, 6, 12, 19, 21, 23, 28],
                      [7, 9, 11, 13, 17, 23, 29, 30],
                      [1, 8, 9, 15, 22]
                      ]

        for i in range(1, 7):
            for j in month_date[i-1]:
                date_str = (datetime.now().strftime('%y')+f"{i:02}"+f"{j:02}")
                print(date_str)
                center_name = random.choice(center_names)
                color_success_counter = [0]
                color_fail_counter = [0]

                if(date_str == 240412):
                    bouldering_clear_color = ['black', 'pink']
                    bouldering_clear_color_counter = [8, 11]
                    start_time = datetime.strptime('09:15:11', '%H:%M:%S').time()
                    end_time = datetime.strptime('10:40:35', '%H:%M:%S').time()
                    play_time = 5000

                elif (date_str == 240419):
                    bouldering_clear_color = ['orange', 'blue']
                    bouldering_clear_color_counter = [7, 10]
                    start_time = datetime.strptime('11:05:11', '%H:%M:%S').time()
                    end_time = datetime.strptime('13:10:35', '%H:%M:%S').time()
                    play_time = 5000

                elif (date_str == 240505):
                    bouldering_clear_color = ['green', 'yellow']
                    bouldering_clear_color_counter = [6, 7]
                    start_time = datetime.strptime('14:59:11', '%H:%M:%S').time()
                    end_time = datetime.strptime('16:27:35', '%H:%M:%S').time()
                    play_time = 5000

                else:
                    bouldering_clear_color = [rand_colors.pop()]
                    bouldering_clear_color_counter = [10]
                    start_time = datetime.strptime('14:59:11', '%H:%M:%S').time()
                    end_time = datetime.strptime('16:27:35', '%H:%M:%S').time()
                    if (i == 1):
                        play_time = 5000
                    elif (i == 2):
                        play_time = 5252
                    elif (i == 3):
                        play_time = 4999
                    elif (i == 4):
                        play_time = random.randrange(4800, 5000)
                    elif (i == 5):
                        play_time = 3690
                    else:
                        play_time = random.randrange(3690, 5000)

                page = Page(
                    date=date_str,
                    dateFieldValue = datetime.now().date(),
                    climbing_center_name=center_name,
                    bouldering_clear_color=bouldering_clear_color,
                    bouldering_clear_color_counter=bouldering_clear_color_counter,
                    color_success_counter=color_success_counter,
                    color_fail_counter=color_fail_counter,
                    today_start_time=start_time,
                    today_end_time=end_time,
                    play_time=play_time
                )
                page.save()

        self.stdout.write(self.style.SUCCESS('Successfully created multiple Page entries'))
