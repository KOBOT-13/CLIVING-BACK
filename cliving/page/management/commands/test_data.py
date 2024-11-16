import random
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker
from ...models import Page

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate test data for the Page model'

    def handle(self, *args, **kwargs):
        faker = Faker('ko_KR')  # 한국어 데이터 사용
        users = User.objects.all()  # 모든 사용자 가져오기

        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Create at least one user before running this command.'))
            return

        num_data = 100  # 생성할 테스트 데이터 개수
        for _ in range(num_data):
            user = random.choice(users)  # 무작위로 사용자 선택

            # 랜덤 날짜 생성
            random_date = faker.date_between(start_date='-1y', end_date='today')  # 지난 1년 내 날짜
            formatted_date = random_date.strftime('%y%m%d')  # YYMMDD 형식

            # 랜덤 bouldering_clear_color 데이터
            color_choices = ['red', 'blue', 'green', 'yellow', 'black']
            bouldering_colors = random.choices(color_choices, k=random.randint(1, 3))  # 랜덤 색상 리스트

            # 랜덤 카운터 데이터
            counters = [random.randint(1, 10) for _ in range(len(bouldering_colors))]

            # 랜덤 시간 및 플레이 시간
            start_time = faker.time_object()  # 랜덤 시작 시간
            end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=random.randint(1, 3))).time()  # 1~3시간 후 종료 시간
            play_time = random.randint(60, 3600)  # 1분~1시간 플레이 타임

            # Page 객체 생성
            Page.objects.create(
                user=user,
                date=formatted_date,
                climbing_center_name=faker.company(),
                bouldering_clear_color=bouldering_colors,
                bouldering_clear_color_counter=counters,
                today_start_time=start_time,
                today_end_time=end_time,
                play_time=play_time,
            )

        self.stdout.write(self.style.SUCCESS(f'{num_data} test Page objects created successfully!'))
