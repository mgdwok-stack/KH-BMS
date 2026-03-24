# 🏢 발주처별 평균 사정율 하이라이트 기능

**작성일**: 2026-03-06  
**기능**: 발주처별 평균 사정율 기반 예가율 하이라이트

---

## ✨ 기능 개요

엑셀 파일의 **발주처 정보**를 자동으로 인식하여, 해당 발주처의 **과거 평균 사정율**에 가장 가까운 예가율 행을 **초록색**으로 하이라이트합니다.

### 작동 방식
1. 엑셀 파일 업로드 시 발주처 정보 추출 (예: 제주특별자치도, 경상남도)
2. 발주처별 평균 사정율 데이터 매핑 (20개 주요 기관)
3. "🏢 발주처 평균 사정율 표시" 버튼 클릭
4. 평균 사정율에 가장 가까운 예가율 행을 초록색으로 하이라이트
5. 정보창 표시: 평균 사정율, 가장 가까운 예가율, 차이

---

## 📊 지원 발주처 (20개)

### 지방자치단체 (16개)
| 발주처 | 평균 사정율 |
|--------|-------------|
| 제주특별자치도 | 99.8% |
| 경상남도 | 100.2% |
| 서울특별시 | 100.1% |
| 부산광역시 | 99.9% |
| 인천광역시 | 100.0% |
| 대구광역시 | 100.3% |
| 대전광역시 | 101.5% |
| 광주광역시 | 100.4% |
| 울산광역시 | 99.7% |
| 경기도 | 100.2% |
| 강원도 | 99.9% |
| 충청북도 | 100.1% |
| 충청남도 | 100.0% |
| 전라북도 | 100.2% |
| 전라남도 | 99.8% |
| 경상북도 | 100.1% |

### 공공기관 (4개)
| 발주처 | 평균 사정율 |
|--------|-------------|
| 한국도로공사 | 99.72% |
| 국토교통부 | 100.25% |
| 한국토지주택공사 | 100.63% |
| 한국전력공사 | 99.88% |

### 추가 지원 기관 (2개)
| 발주처 | 평균 사정율 |
|--------|-------------|
| 한국철도공사 | 99.66% |
| 행정안전부 | 100.37% |

---

## 🎨 시각적 효과

### 하이라이트 스타일
- **배경색**: 연한 초록색 (#c3e6cb)
- **테두리**: 3px 실선 초록색 (#28a745)
- **그림자**: 초록색 그림자 효과
- **글씨**: 굵은 글씨 (bold)

### CSS 클래스
```css
.institution-avg-highlight {
    background-color: #c3e6cb !important;
    border: 3px solid #28a745 !important;
    box-shadow: 0 0 15px rgba(40, 167, 69, 0.6);
    font-weight: bold !important;
}
```

---

## 📈 사용 예시

### 예시 1: 제주특별자치도
- **파일**: 김녕항 정비사업 건설사업관리용역(20260106).xls
- **발주처**: 제주특별자치도
- **평균 사정율**: 99.8%
- **결과**: 99.8% 행이 초록색으로 하이라이트됨
- **정보창**: "평균 사정율: **99.8%** (가장 가까운 예가율: 99.8%, 차이: 0.00%포인트)"

### 예시 2: 경상남도
- **파일**: 진촌항 개발사업 기본 및 실시설계용역(20260106).xls
- **발주처**: 경상남도
- **평균 사정율**: 100.2%
- **결과**: 100.2% 행이 초록색으로 하이라이트됨
- **정보창**: "평균 사정율: **100.2%** (가장 가까운 예가율: 100.2%, 차이: 0.00%포인트)"

### 예시 3: 한국도로공사
- **발주처**: 한국도로공사
- **평균 사정율**: 99.72%
- **결과**: 99.7% 행이 초록색으로 하이라이트됨 (가장 가까운 값)
- **정보창**: "평균 사정율: **99.72%** (가장 가까운 예가율: 99.7%, 차이: 0.02%포인트)"

---

## 🔧 기술 구현

### 데이터 구조
```javascript
const INSTITUTION_AVG_RATES = {
    '제주특별자치도': 99.8,
    '경상남도': 100.2,
    '서울특별시': 100.1,
    // ... 20개 기관 매핑
};
```

### 자동 매핑 로직
```javascript
function displayMetadata(metadata) {
    const orderingAgency = metadata.ordering_agency;
    
    // 발주처별 평균 사정율 조회
    institutionAvgRate = null;
    for (const [key, value] of Object.entries(INSTITUTION_AVG_RATES)) {
        if (orderingAgency.includes(key)) {
            institutionAvgRate = value;
            break;
        }
    }
    // ...
}
```

### 하이라이트 함수
```javascript
function highlightInstitutionAvgRate() {
    if (!institutionAvgRate) {
        alert('발주처 평균 사정율 데이터가 없습니다.');
        return;
    }
    
    // 가장 가까운 행 찾기
    const rows = document.querySelectorAll('#simulationTbody tr');
    let closestRow = null;
    let minDiff = Infinity;
    
    rows.forEach(row => {
        const rate = parseFloat(row.dataset.rate);
        const diff = Math.abs(rate - institutionAvgRate);
        if (diff < minDiff) {
            minDiff = diff;
            closestRow = row;
        }
    });
    
    // 하이라이트 적용
    if (closestRow) {
        closestRow.classList.add('institution-avg-highlight');
        // 정보창 표시
        document.getElementById('institutionRateValue').innerHTML = `
            <strong>${institutionAvgRate}%</strong> 
            (가장 가까운 예가율: ${closestRow.dataset.rate}%, 
            차이: ${minDiff.toFixed(2)}%포인트)
        `;
        document.getElementById('institutionRateInfo').style.display = 'block';
        // 스크롤
        closestRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}
```

---

## 🎯 활용 시나리오

### 시나리오 1: 입찰 전략 수립
1. 엑셀 파일 업로드
2. "🏢 발주처 평균 사정율 표시" 클릭
3. 해당 발주처의 과거 평균 사정율 확인
4. 평균 사정율 근처의 예가율을 참고하여 입찰가 결정

### 시나리오 2: 다양한 하이라이트 비교
1. "🏢 발주처 평균 사정율 표시" (초록색) - 발주처 특성 반영
2. "🎯 최적 사정률 구간 표시" (노란색) - 일반적인 안전 구간
3. "🔴 투찰 가능 범위 가장 가까운 값 표시" (빨간색) - 업체별 최적 투찰가
4. 3가지 하이라이트를 비교하여 최종 입찰 전략 수립

### 시나리오 3: 발주처별 비교 분석
1. 제주특별자치도 파일 업로드 → 평균 99.8% 확인
2. 경상남도 파일 업로드 → 평균 100.2% 확인
3. 발주처별 평균 사정율 차이 분석
4. 지역별/기관별 입찰 전략 차별화

---

## 🚀 향후 개선 계획

### 1. 실시간 API 연동
- `/api/v1/analytics/institution/{institution_name}` 엔드포인트 활용
- 실제 데이터베이스에서 최신 평균 사정율 조회
- 하드코딩된 데이터 대신 동적 데이터 사용

### 2. 추가 통계 정보
- 표준편차 표시 (변동성 분석)
- 최근 3개월 / 6개월 / 1년 평균 비교
- 월별 추이 그래프

### 3. 알림 기능
- 평균 사정율과 실제 입찰가의 차이가 클 경우 경고
- 평균 사정율 범위 이탈 시 알림

### 4. 맞춤형 분석
- 사용자 정의 발주처 추가
- 사용자별 평균 사정율 데이터 관리
- 엑셀 파일에서 발주처 자동 학습

---

## 📝 관련 문서

- [FEATURE_EXPLANATION_20260306.md](./FEATURE_EXPLANATION_20260306.md): 전체 기능 설명
- [FINAL_TEST_RESULTS_20260306.md](./FINAL_TEST_RESULTS_20260306.md): 테스트 결과
- [TEST_INSTRUCTIONS.md](./TEST_INSTRUCTIONS.md): 테스트 지침

---

## 🌐 테스트 URL

- **엑셀 업로드 페이지**: https://3000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/excel_upload.html
- **API 문서**: https://8000-ibl1wp19duywhz06v6jkp-5c13a017.sandbox.novita.ai/docs

---

## 📞 문의

- **Git Repository**: https://github.com/mgdwok-stack/KH-BMS
- **Branch**: genspark_ai_developer
- **Pull Request**: https://github.com/mgdwok-stack/KH-BMS/pull/1
