# CSV 파일 자동 업데이트 시스템 가이드

## 🎯 개요

CSV 파일을 `data/upload_files/` 폴더에 추가하거나 수정하면 자동으로 모든 발주처 DB가 업데이트됩니다.

---

## 🚀 사용 방법

### 방법 1: 자동 업데이트 스크립트 실행 (권장)

#### 1-1. 기본 실행 (변경사항만 업데이트)

```bash
python3 auto_update_dbs.py
```

**동작:**
- CSV 파일의 변경사항 자동 감지
- 새 파일, 수정된 파일 확인
- 변경사항이 있으면 모든 발주처 DB 업데이트
- 변경사항이 없으면 건너뜀

**예시 출력:**
```
================================================================================
🔄 데이터베이스 자동 업데이트 시작
================================================================================

📄 새 파일: 1개
   + 25년12월.CSV

🏢 발견된 발주처: 5개

[1/5] 🔄 경상남도 업데이트 중...
           ✅ 20건 업데이트 완료
[2/5] 🔄 경상남도 합천군 업데이트 중...
           ✅ 18건 업데이트 완료
...

================================================================================
✅ 업데이트 완료: 성공 5개, 실패 0개
📅 업데이트 시간: 2026-03-19 12:00:00
================================================================================
```

#### 1-2. 강제 업데이트 (변경사항 없어도 실행)

```bash
python3 auto_update_dbs.py --force
# 또는
python3 auto_update_dbs.py -f
```

**사용 시나리오:**
- DB 파일이 손상되었을 때
- 전체 재생성이 필요할 때
- 테스트 목적

---

### 방법 2: API로 업데이트 (웹에서)

#### 2-1. 변경사항 확인

```bash
curl http://localhost:8000/api/v1/check-updates
```

**응답 예시:**
```json
{
  "has_changes": true,
  "changes": {
    "new_files": ["25년12월.CSV"],
    "modified_files": ["25년11월.CSV"],
    "deleted_files": []
  },
  "csv_files": [
    {
      "name": "25년10월.CSV",
      "path": "data/upload_files/25년10월.CSV",
      "size": 4527,
      "modified": 1773905638.80
    }
  ],
  "total_csv_files": 3
}
```

#### 2-2. 자동 업데이트 실행

```bash
# 기본 업데이트 (변경사항만)
curl -X POST http://localhost:8000/api/v1/update-all-databases

# 강제 업데이트
curl -X POST "http://localhost:8000/api/v1/update-all-databases?force=true"
```

**응답:**
```json
{
  "message": "데이터베이스 업데이트가 백그라운드에서 실행됩니다.",
  "force": false,
  "status": "started"
}
```

**브라우저에서:**
1. https://8000-...sandbox.novita.ai/docs 접속
2. `POST /api/v1/update-all-databases` 찾기
3. "Try it out" 클릭
4. "Execute" 클릭

---

## 📁 CSV 파일 추가/수정하기

### 새 CSV 파일 추가

```bash
# 1. data/upload_files/ 폴더에 CSV 파일 복사
cp 25년12월.CSV data/upload_files/

# 2. 자동 업데이트 실행
python3 auto_update_dbs.py
```

**자동으로 수행되는 작업:**
1. ✅ 새 파일 감지
2. ✅ 파일에서 발주처 추출
3. ✅ 각 발주처별 DB 생성/업데이트
4. ✅ 상태 저장 (다음 번 변경 감지용)

### 기존 CSV 파일 수정

```bash
# 1. 파일 수정 (예: 데이터 추가)
# (data/upload_files/25년11월.CSV 파일 편집)

# 2. 자동 업데이트 실행
python3 auto_update_dbs.py
```

**동작:**
- 파일 해시값으로 변경 감지
- 수정된 파일 포함하여 DB 재생성

---

## 🔄 작동 원리

### 변경 감지 메커니즘

1. **파일 해시 계산**: 각 CSV 파일의 MD5 해시 계산
2. **상태 저장**: `data/.update_state.json`에 파일 정보 저장
3. **변경 비교**: 이전 상태와 현재 상태 비교
4. **자동 업데이트**: 변경사항 발견 시 DB 재생성

### 상태 파일 (data/.update_state.json)

```json
{
  "data/upload_files/25년10월.CSV": {
    "hash": "a1b2c3d4e5f6...",
    "modified": 1773905638.80,
    "size": 4527
  },
  "data/upload_files/25년11월.CSV": {
    "hash": "f6e5d4c3b2a1...",
    "modified": 1773905589.34,
    "size": 3223
  }
}
```

---

## 📊 업데이트 프로세스

```
1. CSV 파일 스캔
   ↓
2. 변경사항 확인 (해시 비교)
   ↓
3. 발주처 목록 추출
   ↓
4. 각 발주처별 DB 생성
   │
   ├─ 기존 DB 삭제
   ├─ 새 DB 생성
   ├─ CSV에서 데이터 필터링
   ├─ bid_data 테이블 생성
   └─ 데이터 삽입
   ↓
5. 상태 저장
```

---

## 💡 실전 예제

### 예제 1: 매월 CSV 파일 업데이트

```bash
# 12월 데이터가 나왔을 때
cd /home/user/webapp

# 1. CSV 파일 복사
cp ~/Downloads/25년12월.CSV data/upload_files/

# 2. 파일 확인
ls -lh data/upload_files/

# 3. 자동 업데이트 실행
python3 auto_update_dbs.py

# 4. 결과 확인
ls -lh data/databases/
```

### 예제 2: 데이터 수정 후 업데이트

```bash
# 기존 파일 수정
nano data/upload_files/25년11월.CSV
# (데이터 편집 후 저장)

# 자동 업데이트 (수정 감지)
python3 auto_update_dbs.py

# 특정 발주처 확인
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('data/databases/경상남도.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM bid_data")
print(f"총 데이터: {cursor.fetchone()[0]}건")
conn.close()
EOF
```

### 예제 3: 크론탭으로 자동화

```bash
# 크론탭 편집
crontab -e

# 매일 오전 9시에 자동 업데이트
0 9 * * * cd /home/user/webapp && python3 auto_update_dbs.py >> logs/auto_update.log 2>&1

# 또는 매시간 확인
0 * * * * cd /home/user/webapp && python3 auto_update_dbs.py >> logs/auto_update.log 2>&1
```

---

## 🔍 문제 해결

### Q1: 업데이트가 실행되지 않아요

**A:** 변경사항이 없을 수 있습니다.

```bash
# 강제 업데이트
python3 auto_update_dbs.py --force

# 또는 상태 파일 삭제 후 재실행
rm data/.update_state.json
python3 auto_update_dbs.py
```

### Q2: 특정 발주처만 업데이트하고 싶어요

**A:** 기존 CLI 프로그램 사용

```bash
python3 create_db_by_org.py "경상남도"
```

### Q3: CSV 파일이 감지되지 않아요

**A:** 파일 위치와 확장자 확인

```bash
# 파일 위치 확인
ls -la data/upload_files/*.CSV
ls -la data/upload_files/*.csv

# 파일 이름 대소문자 확인 (.CSV vs .csv)
```

### Q4: 업데이트 실패 시

**A:** 로그 확인 및 수동 재시도

```bash
# 자세한 출력으로 실행
python3 auto_update_dbs.py --force

# CSV 파일 인코딩 확인
file data/upload_files/*.CSV

# 특정 파일 테스트
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('data/upload_files/25년11월.CSV', encoding='cp949')
print(f"행 수: {len(df)}")
print(f"컬럼: {df.columns.tolist()}")
EOF
```

---

## 🎯 모범 사례

### 1. 정기적인 업데이트

```bash
# 매월 1일 오전 9시에 자동 업데이트
0 9 1 * * cd /home/user/webapp && python3 auto_update_dbs.py
```

### 2. 백업 후 업데이트

```bash
# DB 백업 후 업데이트
tar -czf backup_$(date +%Y%m%d).tar.gz data/databases/
python3 auto_update_dbs.py
```

### 3. 로그 기록

```bash
# 로그 디렉토리 생성
mkdir -p logs

# 로그와 함께 실행
python3 auto_update_dbs.py 2>&1 | tee logs/update_$(date +%Y%m%d_%H%M%S).log
```

### 4. 업데이트 전 변경사항 확인

```bash
# API로 확인
curl -s http://localhost:8000/api/v1/check-updates | python3 -m json.tool

# 변경사항이 있으면 업데이트
if curl -s http://localhost:8000/api/v1/check-updates | grep '"has_changes": true'; then
    python3 auto_update_dbs.py
fi
```

---

## 📈 성능 최적화

### 대용량 CSV 처리

```python
# 청크 단위로 읽기 (필요시 auto_update_dbs.py 수정)
for chunk in pd.read_csv(csv_file, encoding='cp949', chunksize=1000):
    # 처리
    pass
```

### 병렬 처리 (고급)

```python
# 여러 발주처 동시 처리
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(update_organization_db, organizations)
```

---

## ✅ 요약

**CSV 파일 업데이트 워크플로우:**

1. 📁 CSV 파일을 `data/upload_files/`에 추가/수정
2. 🔄 `python3 auto_update_dbs.py` 실행
3. ✅ 자동으로 모든 발주처 DB 업데이트
4. 📊 결과 확인

**핵심 명령어:**
- `python3 auto_update_dbs.py` - 자동 업데이트
- `python3 auto_update_dbs.py --force` - 강제 업데이트
- `curl http://localhost:8000/api/v1/check-updates` - 변경사항 확인
- `curl -X POST http://localhost:8000/api/v1/update-all-databases` - API 업데이트

**이제 CSV 파일만 추가하면 자동으로 DB가 업데이트됩니다! 🎉**
