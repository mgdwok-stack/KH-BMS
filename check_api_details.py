#!/usr/bin/env python3
"""
공공데이터포털 API 상세 정보 확인
"""
import os
import httpx
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv('PROCUREMENT_API_KEY')
BASE_URL = os.getenv('PROCUREMENT_API_BASE_URL', 'http://apis.data.go.kr/1230000/ScsbidInfoService')

print("=" * 70)
print("🔍 API 상세 정보 확인")
print("=" * 70)

# 낙찰정보서비스 테스트 (당신이 필요한 것!)
print("\n📋 낙찰정보서비스 테스트 (getOpengBidInfoServc01)")
print("-" * 70)

url = f"{BASE_URL}/getOpengBidInfoServc01"
params = {
    'serviceKey': API_KEY,
    'numOfRows': 1,
    'pageNo': 1,
    'inqryDiv': '1',  # 조회구분 (1: 기간별)
    'inqryBgnDt': '202603010000',  # 시작일시
    'inqryEndDt': '202603060000',  # 종료일시
    'type': 'json'
}

print(f"URL: {url}")
print(f"파라미터: {json.dumps(params, indent=2, ensure_ascii=False)}")

try:
    response = httpx.get(url, params=params, timeout=10)
    print(f"\n응답 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 성공!")
        print(f"\n응답 데이터:\n{json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
    else:
        print(f"❌ 실패")
        print(f"응답: {response.text[:500]}")
        
        # URL 인코딩 문제 가능성 체크
        print("\n" + "=" * 70)
        print("🔧 URL 인코딩 없이 재시도")
        print("=" * 70)
        
        # serviceKey를 URL에 직접 포함
        direct_url = f"{url}?serviceKey={API_KEY}&numOfRows=1&pageNo=1&inqryDiv=1&inqryBgnDt=202603010000&inqryEndDt=202603060000&type=json"
        print(f"Direct URL (처음 100자): {direct_url[:100]}...")
        
        response2 = httpx.get(direct_url, timeout=10)
        print(f"\n응답 코드: {response2.status_code}")
        
        if response2.status_code == 200:
            data = response2.json()
            print(f"✅ 성공! (URL 직접 사용)")
            print(f"\n응답 데이터:\n{json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"❌ 여전히 실패")
            print(f"응답: {response2.text[:500]}")
            
except Exception as e:
    print(f"❌ 오류 발생: {e}")

print("\n" + "=" * 70)
