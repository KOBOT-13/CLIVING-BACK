# CLIVING Setup 문서
### 가상환경 세팅
```bash
virtualenv venv
```
또는
```bash
python -m venv venv
```

명령어를 활용하여 가상환경을 만들어 줍니다.

```bash
source venv/bin/activate
```
명령어를 활용하여 가상환경을 활성화 시켜줍니다.

### 의존성 패키지 설치
```bash
pip install -r requirements.txt
```
동봉되어있는 requirements.txt를 활용하여 의존성 패키지를 설치하여 줍니다.

### 데이터베이스 초기화
```bash
python manage.py makemigrations
python manage.py migrate
```
위 명령어를 활용하여 데이터베이스를 초기화해 줍니다.
makemigrations 명령어를 실행시키면 각 앱별로 데이터베이스 마이그레이션 파일들이 생성되니 git을 활용할 때,
이때 만들어지는 마이그레이션 파일들도 푸시해 줍니다.


### api
```bash
statistics/montly/climbing-time/ #이번달의 클라이밍 토탈 시간 반환
statistics/annual/climbing-time/ #올해의 클라이밍 토탈 시간 반환
statistics/climbing/년(ex:24)/월(ex:6)/ #특정 년, 월의 클라이밍 토탈 시간 반환
statistics/montly/color-tries/ #이번달의 색깔별 try 횟수 반환
statistics/annual/color-tries/ #올해의 색깔별 try 횟수 반환
```