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