#!/usr/bin/env python3
"""
나라장터 API 키 업데이트 도구
사용법: python3 update_api_key.py
"""

import os
import sys
from datetime import datetime

def main():
    print("="*70)
    print("🔑 나라장터 API 키 업데이트 도구")
    print("="*70)
    print()
    
    # 현재 디렉토리 확인
    current_dir = os.getcwd()
    env_path = os.path.join(current_dir, '.env')
    
    print(f"📂 현재 디렉토리: {current_dir}")
    print(f"📝 .env 파일 경로: {env_path}")
    print()
    
    # .env 파일 존재 확인
    if not os.path.exists(env_path):
        print(f"❌ 오류: .env 파일을 찾을 수 없습니다!")
        print(f"   경로: {env_path}")
        print()
        print("💡 해결 방법:")
        print("   1. 프로젝트 디렉토리로 이동: cd /home/user/webapp")
        print("   2. 다시 실행: python3 update_api_key.py")
        sys.exit(1)
    
    # 현재 API 키 읽기
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    old_api_key = None
    api_key_line_index = None
    
    for i, line in enumerate(lines):
        if line.startswith('PROCUREMENT_API_KEY='):
            old_api_key = line.split('=', 1)[1].strip()
            api_key_line_index = i
            break
    
    if old_api_key is None:
        print("❌ 오류: .env 파일에서 PROCUREMENT_API_KEY를 찾을 수 없습니다!")
        sys.exit(1)
    
    print("✅ 현재 API 키 확인:")
    print(f"   앞 10자: {old_api_key[:10]}...")
    print(f"   뒤 10자: ...{old_api_key[-10:]}")
    print(f"   전체 길이: {len(old_api_key)} 문자")
    print()
    
    # 새 API 키 입력 받기
    print("─" * 70)
    print("📋 새 API 키를 입력해주세요 (64자 문자열)")
    print("   공공데이터포털(data.go.kr)에서 발급받은 키를 붙여넣으세요.")
    print("─" * 70)
    print()
    
    new_api_key = input("새 API 키: ").strip()
    
    # 입력 검증
    if not new_api_key:
        print("❌ API 키가 입력되지 않았습니다.")
        sys.exit(1)
    
    if len(new_api_key) != 64:
        print(f"❌ 오류: API 키는 64자여야 합니다.")
        print(f"   입력된 길이: {len(new_api_key)} 문자")
        print()
        print("💡 확인사항:")
        print("   - 앞뒤 공백이 없는지 확인")
        print("   - 줄바꿈이 포함되지 않았는지 확인")
        print("   - 복사할 때 전체 키를 선택했는지 확인")
        sys.exit(1)
    
    # 기존 키와 동일한지 확인
    if new_api_key == old_api_key:
        print("⚠️  새 API 키가 기존 키와 동일합니다.")
        print("   변경하지 않고 종료합니다.")
        sys.exit(0)
    
    print()
    print("="*70)
    print("🔍 변경 내용 확인")
    print("="*70)
    print(f"기존 API 키: {old_api_key[:10]}...{old_api_key[-10:]}")
    print(f"새 API 키:   {new_api_key[:10]}...{new_api_key[-10:]}")
    print()
    
    # 확인 받기
    confirm = input("이대로 변경하시겠습니까? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ 취소되었습니다.")
        sys.exit(0)
    
    # 백업 생성
    backup_path = f"{env_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w') as f:
        f.writelines(lines)
    print()
    print(f"✅ 백업 생성: {backup_path}")
    
    # API 키 업데이트
    lines[api_key_line_index] = f'PROCUREMENT_API_KEY={new_api_key}\n'
    
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ API 키 업데이트 완료!")
    print()
    
    # 변경 확인
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('PROCUREMENT_API_KEY='):
                updated_key = line.split('=', 1)[1].strip()
                print("🔍 업데이트된 API 키 확인:")
                print(f"   앞 10자: {updated_key[:10]}...")
                print(f"   뒤 10자: ...{updated_key[-10:]}")
                print(f"   전체 길이: {len(updated_key)} 문자")
                break
    
    print()
    print("="*70)
    print("📝 다음 단계")
    print("="*70)
    print("1. API 연결 테스트:")
    print("   python3 test_api_connection.py")
    print()
    print("2. 백엔드 서버 재시작:")
    print("   # 기존 서버 찾기")
    print("   ps aux | grep real_data_server")
    print("   # 서버 중지 (PID는 위에서 확인)")
    print("   kill -9 <PID>")
    print("   # 서버 재시작")
    print("   cd /home/user/webapp/backend && python real_data_server.py &")
    print()
    print("="*70)
    print("✅ 완료!")
    print("="*70)

if __name__ == "__main__":
    main()
