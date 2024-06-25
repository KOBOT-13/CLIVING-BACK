# 프로젝트 소개
---
# 역할 분담
---
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

### secrets.json 설치하기
```bash
.../cliving/page/
```
위 위치에 secrets.json 을 설치합니다.

### postgreSQL DB 설치
```bash
https://www.postgresql.org/download/ # 원하는 버전을 설치합니다.
# 설치 과정에서 입력하는 superuser의 비밀번호를 잘 기억해야 합니다.
```
웹에서 postgreSQL을 설치하고 초기 비밀번호를 설정합니다.
설치된 SQL Shell을 실행하여 엔터를 몇번 누른 뒤, 패스워드 입력란에 초기 비밀번호를 입력합니다.

### postgreSQL과 장고 연동하기
```bash
CREATE DATABASE ('데이터베이스 이름');
CREATE USER ('유저명') WITH PASSWORD ('비밀번호');
ALTER ROLE ('유저명') SET client_encoding TO 'utf8';
ALTER ROLE ('유저명') SET default_transaction_isolation TO 'read committed';
ALTER ROLE ('유저명') SET TIME ZONE 'Asia/Seoul';
GRANT ALL PRIVILEGES ON DATABASE data_planet_db TO root;
ALTER USER ('유저명') SUPERUSER;
```
secrets.json 파일에 설정되어 있는 '데이터베이스 이름', '유저명', '비밀번호'를 보고
위 명령어를 차례로 SQL Shell 에서 실행합니다.

### postgreSQL이 작동을 멈추었을 경우(Windows)
```bash
윈도우 로고 우클릭 > 컴퓨터 관리 > 서비스 및 응용 프로그램 > 서비스 > postgresql-x64-16 을 찾아 우클릭 > 시작
```
윈도우 최적화 프로그램 등을 사용했을 때, 콘솔이 꺼지는 듯 합니다.
꺼지면 python manage.py runserver가 동작하지 않으므로 오류 발생시 잘 켜주도록 합시다.


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


### 테스트 데이터 추가
```bash
python manage.py create_page
```
위 명령어를 활용하여 데이터페이스에 테스트를 위한 여러 페이지를 자동 생성합니다.
이를 통계 api 활용에 사용할 수 있습니다.



