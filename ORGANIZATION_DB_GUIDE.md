# 발주처별 입찰 데이터베이스 시스템 사용 가이드

## 🎯 시스템 개요

CSV 파일에서 입찰 데이터를 읽어 발주처별로 SQLite 데이터베이스를 생성하고, 
웹 API를 통해 데이터를 조회할 수 있는 시스템입니다.

### 주요 기능
- ✅ CSV 파일에서 발주처별 데이터 추출
- ✅ 발주처명으로 SQLite DB 자동 생성 (예: `경상남도.db`)
- ✅ 사업명, 발주처, 기초금액, 예정금액, 예가, 낙찰업체 포함
- ✅ RESTful API로 데이터 조회
- ✅ 통계 및 검색 기능

---

## 📁 파일 구조

```
/home/user/webapp/
├── data/
│   ├── upload_files/        # CSV 파일 위치
│   │   ├── 25년10월.CSV
│   │   └── 25년11월.CSV
│   └── databases/           # 생성된 DB 파일
│       ├── 경상남도.db
│       ├── 경상남도 합천군.db
│       └── 충청북도 청주시.db
├── create_db_by_org.py      # CLI 프로그램
└── org_db_server.py         # API 서버
```

---

## 🖥️ 방법 1: 명령줄(CLI) 사용

### 1-1. 대화형 모드

```bash
cd /home/user/webapp
python3 create_db_by_org.py
```

실행하면 사용 가능한 발주처 목록이 표시되고, 번호 또는 이름으로 선택할 수 있습니다.

**예시:**
```
============================================================
🏢 발주처별 데이터베이스 생성 프로그램
============================================================

📋 사용 가능한 발주처 목록 (4개):
   1. 경상남도
   2. 경상남도 합천군
   3. 충청북도 청주시
   4. 한국어촌어항공단

============================================================
📝 발주처 이름을 입력하세요 (또는 번호): 1
```

### 1-2. 직접 실행 모드

```bash
# 발주처 이름을 인자로 전달
python3 create_db_by_org.py "경상남도"
```

**출력 예시:**
```
============================================================
✅ 데이터베이스 생성 완료!
============================================================
📍 파일 위치: data/databases/경상남도.db
📊 통계:
   - 전체 입찰 기록: 14건
   - 프로젝트 수: 1개
   - 낙찰 기록: 1건
============================================================
```

---

## 🌐 방법 2: 웹 API 사용

### 2-1. API 서버 실행

```bash
cd /home/user/webapp
python3 org_db_server.py
```

서버가 시작되면:
- 🌐 **서버 주소**: http://localhost:8000
- 📖 **API 문서**: http://localhost:8000/docs
- 💚 **헬스 체크**: http://localhost:8000/health

### 2-2. 주요 API 엔드포인트

#### 📋 생성된 발주처 목록 조회
```bash
curl http://localhost:8000/api/v1/organizations
```

**응답 예시:**
```json
[
  {
    "name": "경상남도",
    "db_file": "data/databases/경상남도.db",
    "total_records": 14,
    "total_projects": 1,
    "winner_count": 1
  }
]
```

#### 🔍 특정 발주처 데이터 조회
```bash
# 기본 조회 (최대 100건)
curl "http://localhost:8000/api/v1/organizations/경상남도"

# 개수 제한
curl "http://localhost:8000/api/v1/organizations/경상남도?limit=5"

# 낙찰업체만 조회
curl "http://localhost:8000/api/v1/organizations/경상남도?winner_only=true"
```

#### 📊 발주처 통계 조회
```bash
curl "http://localhost:8000/api/v1/organizations/경상남도/stats"
```

**응답 예시:**
```json
{
  "organization": "경상남도",
  "total_records": 14,
  "total_projects": 1,
  "winner_count": 1,
  "avg_estimated_rate": 100.13,
  "avg_predicted_rate": 100.46,
  "winners": [
    {
      "company": "수성+세일",
      "count": 1
    }
  ]
}
```

#### 🆕 새 발주처 DB 생성
```bash
# Python으로 생성 (URL 인코딩 필요)
python3 << 'EOF'
import requests
import urllib.parse

org_name = "충청북도 청주시"
encoded_name = urllib.parse.quote(org_name)
url = f"http://localhost:8000/api/v1/create-db/{encoded_name}"

response = requests.post(url)
print(response.json())
EOF
```

#### 🔎 프로젝트 검색
```bash
# 모든 DB에서 검색
curl "http://localhost:8000/api/v1/search?keyword=진촌항"

# 특정 발주처에서만 검색
curl "http://localhost:8000/api/v1/search?keyword=진촌항&org_name=경상남도"
```

#### 📋 CSV에서 사용 가능한 발주처 목록
```bash
curl "http://localhost:8000/api/v1/available-organizations"
```

---

## 🗄️ 데이터베이스 구조

### 테이블: `bid_data`

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | INTEGER | 자동 증가 ID |
| pq_no | TEXT | PQ공고 번호 |
| announcement_date | TEXT | 공고일자 |
| project_name | TEXT | **사업명** |
| organization | TEXT | **발주처** |
| bid_type | TEXT | 입찰구분 |
| base_amount | TEXT | **기초금액** |
| estimated_price | TEXT | **예정금액** |
| estimated_rate | REAL | **예가** |
| company_name | TEXT | 업체명 |
| pq_score | REAL | PQ점수 |
| bid_amount | TEXT | 투찰금액 |
| predicted_rate | REAL | 추정예가 |
| is_winner | TEXT | **낙찰여부** (O/X) |
| created_at | TIMESTAMP | 생성일시 |

---

## 💡 사용 예시

### 예시 1: 경상남도 DB 생성 및 조회

```bash
# 1. DB 생성
python3 create_db_by_org.py "경상남도"

# 2. Python으로 조회
python3 << 'EOF'
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/databases/경상남도.db')
df = pd.read_sql_query("""
    SELECT 
        project_name AS '사업명',
        base_amount AS '기초금액',
        estimated_price AS '예정금액',
        estimated_rate AS '예가',
        company_name AS '업체명',
        is_winner AS '낙찰'
    FROM bid_data
    WHERE is_winner = 'O'
""", conn)
print(df)
conn.close()
EOF
```

### 예시 2: API로 통계 조회

```bash
# Python 스크립트로 여러 발주처 통계 조회
python3 << 'EOF'
import requests

orgs = ["경상남도", "경상남도 합천군", "충청북도 청주시"]

for org in orgs:
    url = f"http://localhost:8000/api/v1/organizations/{requests.utils.quote(org)}/stats"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"\n🏢 {org}")
        print(f"   총 입찰: {data['total_records']}건")
        print(f"   평균 예가: {data['avg_estimated_rate']}%")
        if data['winners']:
            print(f"   낙찰업체: {data['winners'][0]['company']}")
EOF
```

---

## 🔧 SQLite 직접 조회

```bash
# SQLite CLI 사용 (설치되어 있는 경우)
sqlite3 data/databases/경상남도.db

# Python으로 조회
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('data/databases/경상남도.db')
cursor = conn.cursor()

# 낙찰업체 조회
cursor.execute("""
    SELECT project_name, company_name, base_amount, bid_amount
    FROM bid_data
    WHERE is_winner = 'O'
""")

for row in cursor.fetchall():
    print(f"사업: {row[0]}")
    print(f"업체: {row[1]}")
    print(f"기초: {row[2]}, 투찰: {row[3]}\n")

conn.close()
EOF
```

---

## 📊 현재 상태

### 생성된 데이터베이스

| 발주처 | 기록 수 | 프로젝트 | 낙찰 |
|--------|---------|----------|------|
| 경상남도 | 14건 | 1개 | 1건 |
| 경상남도 합천군 | 18건 | 1개 | 1건 |
| 충청북도 청주시 | 5건 | 1개 | 1건 |

### CSV 파일의 발주처 목록
- 경상남도
- 경상남도 합천군
- 충청북도 청주시
- 한국어촌어항공단

---

## 🚀 서버 정보

### 공개 URL
```
https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai
```

### API 문서
```
https://8000-i8d6tr442sut34dncpp8y-b237eb32.sandbox.novita.ai/docs
```

### 주요 엔드포인트
- `GET /api/v1/organizations` - 발주처 목록
- `GET /api/v1/organizations/{name}` - 발주처 데이터
- `GET /api/v1/organizations/{name}/stats` - 발주처 통계
- `POST /api/v1/create-db/{name}` - DB 생성
- `GET /api/v1/search?keyword={keyword}` - 검색
- `GET /api/v1/available-organizations` - CSV 발주처 목록

---

## 🎓 추가 기능 아이디어

### 1. 새 CSV 파일 추가
```bash
# data/upload_files/ 디렉토리에 CSV 파일 추가
cp 새로운파일.CSV data/upload_files/

# 기존 DB 재생성 (최신 데이터 반영)
python3 create_db_by_org.py "경상남도"
```

### 2. 데이터 분석
```python
import sqlite3
import pandas as pd

# 여러 DB 데이터 병합 분석
dbs = ['경상남도.db', '경상남도 합천군.db']
all_data = []

for db in dbs:
    conn = sqlite3.connect(f'data/databases/{db}')
    df = pd.read_sql_query("SELECT * FROM bid_data", conn)
    all_data.append(df)
    conn.close()

combined = pd.concat(all_data)
print(f"전체 데이터: {len(combined)}건")
print(f"평균 예가: {combined['estimated_rate'].mean():.2f}%")
```

---

## ✅ 완료!

이제 발주처를 입력하면 자동으로:
1. ✅ CSV에서 해당 발주처 데이터 추출
2. ✅ `{발주처명}.db` 파일 생성
3. ✅ 사업명, 발주처, 기초금액, 예정금액, 예가, 낙찰업체 포함
4. ✅ API로 조회 가능

**Happy Coding! 🎯**
