#!/usr/bin/env python3
"""
나라장터 API 연결 테스트 도구
사용법: python3 test_api_connection.py
"""

import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

def main():
    print("="*70)
    print("🔍 나라장터 API 연결 테스트")
    print("="*70)
    print()
    
    # .env 파일 로드
    env_path = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(env_path):
        print(f"❌ 오류: .env 파일을 찾을 수 없습니다!")
        print(f"   경로: {env_path}")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    # API 설정 확인
    api_key = os.getenv('PROCUREMENT_API_KEY', '')
    base_url = os.getenv('PROCUREMENT_API_BASE_URL', '')
    
    print("📋 API 설정 확인")
    print("─" * 70)
    print(f"API 키 존재: {'✅' if api_key else '❌'}")
    print(f"API 키 길이: {len(api_key)} 문자 {'✅' if len(api_key) == 64 else '❌'}")
    print(f"API 키 앞 10자: {api_key[:10]}...")
    print(f"API URL: {base_url}")
    print()
    
    if not api_key or len(api_key) != 64:
        print("❌ API 키가 올바르지 않습니다.")
        print("   update_api_key.py를 실행하여 API 키를 업데이트하세요.")
        sys.exit(1)
    
    # 테스트 엔드포인트 목록
    endpoints = [
        'getBidPblancListInfoServc01',
        'getOpengBidInfoServc01',
        'getPblancListInfoServc01'
    ]
    
    print("🔍 API 엔드포인트 테스트")
    print("─" * 70)
    
    success_count = 0
    
    for endpoint in endpoints:
        test_url = f"{base_url}/{endpoint}"
        params = {
            'serviceKey': api_key,
            'type': 'json',
            'pageNo': 1,
            'numOfRows': 1
        }
        
        print(f"\n📡 테스트: {endpoint}")
        print(f"   URL: {test_url}")
        
        try:
            response = requests.get(test_url, params=params, timeout=10)
            print(f"   응답 코드: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ 성공!")
                try:
                    data = response.json()
                    if 'response' in data:
                        print(f"   📊 응답 구조: {list(data['response'].keys())}")
                        if 'body' in data['response']:
                            body = data['response']['body']
                            if 'items' in body:
                                print(f"   📊 데이터 건수: {len(body.get('items', []))}건")
                    success_count += 1
                except:
                    print(f"   ⚠️  JSON 파싱 실패")
            else:
                print(f"   ❌ 실패")
                print(f"   응답: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"   ❌ 타임아웃 (10초)")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print()
    print("="*70)
    print("📊 테스트 결과 요약")
    print("="*70)
    print(f"총 테스트: {len(endpoints)}개")
    print(f"성공: {success_count}개 {'✅' if success_count > 0 else '❌'}")
    print(f"실패: {len(endpoints) - success_count}개")
    print()
    
    if success_count > 0:
        print("✅ API 연결 성공!")
        print()
        print("📝 다음 단계:")
        print("   백엔드 서버를 재시작하여 새 API 키를 적용하세요.")
        print("   1. 기존 서버 중지: kill -9 <PID>")
        print("   2. 새 서버 시작: cd backend && python real_data_server.py &")
    else:
        print("❌ API 연결 실패")
        print()
        print("💡 문제 해결:")
        print("   1. 공공데이터포털에서 API 키 상태 확인")
        print("      https://www.data.go.kr/")
        print("   2. 활용신청이 승인되었는지 확인")
        print("   3. API 키가 만료되지 않았는지 확인")
        print("   4. 새 API 키로 재발급 후 update_api_key.py 실행")
    
    print()
    print("="*70)

if __name__ == "__main__":
    main()
