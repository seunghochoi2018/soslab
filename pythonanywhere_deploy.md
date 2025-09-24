# PythonAnywhere 배포 가이드

## 1. 회원가입
1. https://www.pythonanywhere.com 접속
2. "Sign up" 클릭
3. "Create a Beginner account" 선택 (무료)
4. 사용자명, 이메일, 비밀번호 입력

## 2. 파일 업로드
1. 대시보드에서 "Files" 탭 클릭
2. "mysite" 폴더 생성
3. 다음 파일들 업로드:
   - server.py
   - requirements.txt
   - point_data.json
   - employee_data.json
   - templates/ 폴더 전체
   - static/ 폴더 (있다면)

## 3. 콘솔에서 패키지 설치
1. "Consoles" 탭 클릭
2. "Bash" 콘솔 열기
3. 다음 명령어 실행:
```bash
cd mysite
pip3.10 install --user -r requirements.txt
```

## 4. 웹 앱 설정
1. "Web" 탭 클릭
2. "Add a new web app" 클릭
3. "Next" 클릭 (무료 도메인 사용)
4. "Flask" 선택
5. Python 3.10 선택
6. 경로: /home/[사용자명]/mysite/server.py

## 5. WSGI 파일 수정
1. "Web" 탭에서 "WSGI configuration file" 링크 클릭
2. 내용을 다음과 같이 수정:

```python
import sys
path = '/home/[사용자명]/mysite'
if path not in sys.path:
    sys.path.append(path)

from server import app as application
```

## 6. 정적 파일 설정 (선택사항)
"Web" 탭에서 Static files 섹션:
- URL: /static/
- Directory: /home/[사용자명]/mysite/static/

## 7. 앱 재시작
"Web" 탭에서 "Reload" 버튼 클릭

## 접속 주소
https://[사용자명].pythonanywhere.com

## 주의사항
- 무료 계정은 3개월마다 갱신 필요
- 외부 API 호출 제한 있음 (화이트리스트 API만 가능)
- 일일 CPU 시간 제한 있음
- uploads 폴더 권한 설정 필요할 수 있음