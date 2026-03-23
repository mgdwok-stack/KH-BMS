#!/usr/bin/env python3
"""
CSV 파일 자동 감지 및 데이터베이스 자동 업데이트 스크립트

CSV 파일이 추가/변경되면 자동으로 모든 발주처 DB를 업데이트합니다.
"""

import os
import glob
import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import hashlib


class DatabaseAutoUpdater:
    """데이터베이스 자동 업데이트 관리 클래스"""
    
    def __init__(self, csv_dir="data/upload_files", db_dir="data/databases", state_file="data/.update_state.json"):
        self.csv_dir = csv_dir
        self.db_dir = db_dir
        self.state_file = state_file
        
        # 디렉토리 생성
        os.makedirs(self.csv_dir, exist_ok=True)
        os.makedirs(self.db_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
    
    def get_file_hash(self, file_path):
        """파일의 MD5 해시값 계산"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"❌ 파일 해시 계산 실패 {file_path}: {e}")
            return None
    
    def load_state(self):
        """이전 상태 로드"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_state(self, state):
        """현재 상태 저장"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 상태 저장 실패: {e}")
    
    def get_csv_files(self):
        """모든 CSV 파일 찾기"""
        csv_files = []
        for pattern in ["*.CSV", "*.csv"]:
            csv_files.extend(glob.glob(os.path.join(self.csv_dir, pattern)))
        return csv_files
    
    def check_for_changes(self):
        """CSV 파일 변경사항 확인"""
        current_state = {}
        csv_files = self.get_csv_files()
        
        for csv_file in csv_files:
            file_hash = self.get_file_hash(csv_file)
            if file_hash:
                current_state[csv_file] = {
                    'hash': file_hash,
                    'modified': os.path.getmtime(csv_file),
                    'size': os.path.getsize(csv_file)
                }
        
        previous_state = self.load_state()
        
        # 변경사항 분석
        changes = {
            'new_files': [],
            'modified_files': [],
            'deleted_files': []
        }
        
        # 새 파일 또는 수정된 파일
        for file_path, info in current_state.items():
            if file_path not in previous_state:
                changes['new_files'].append(file_path)
            elif previous_state[file_path]['hash'] != info['hash']:
                changes['modified_files'].append(file_path)
        
        # 삭제된 파일
        for file_path in previous_state:
            if file_path not in current_state:
                changes['deleted_files'].append(file_path)
        
        return changes, current_state
    
    def get_all_organizations(self):
        """CSV에서 모든 발주처 목록 가져오기"""
        csv_files = self.get_csv_files()
        all_orgs = set()
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='cp949')
                all_orgs.update(df['발주처'].unique())
            except Exception as e:
                print(f"❌ {csv_file} 읽기 실패: {e}")
        
        return sorted(list(all_orgs))
    
    def update_organization_db(self, org_name):
        """특정 발주처의 DB 업데이트"""
        csv_files = self.get_csv_files()
        
        if not csv_files:
            return False, "CSV 파일을 찾을 수 없습니다."
        
        # 데이터 수집
        all_data = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='cp949')
                org_data = df[df['발주처'] == org_name]
                if len(org_data) > 0:
                    all_data.append(org_data)
            except Exception as e:
                print(f"  ⚠️  {csv_file} 읽기 실패: {e}")
                continue
        
        if not all_data:
            return False, f"'{org_name}' 발주처의 데이터를 찾을 수 없습니다."
        
        # 데이터프레임 합치기
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # DB 파일 경로
        db_path = os.path.join(self.db_dir, f"{org_name}.db")
        
        # 기존 파일 삭제
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # SQLite DB 생성
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bid_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pq_no TEXT,
                announcement_date TEXT,
                project_name TEXT,
                organization TEXT,
                bid_type TEXT,
                base_amount TEXT,
                estimated_price TEXT,
                estimated_rate REAL,
                company_name TEXT,
                pq_score REAL,
                bid_amount TEXT,
                predicted_rate REAL,
                is_winner TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 데이터 삽입
        for _, row in combined_df.iterrows():
            cursor.execute("""
                INSERT INTO bid_data (
                    pq_no, announcement_date, project_name, organization, bid_type,
                    base_amount, estimated_price, estimated_rate, company_name,
                    pq_score, bid_amount, predicted_rate, is_winner
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['PQ공고 NO.'],
                row['공고일자'],
                row['사업명'],
                row['발주처'],
                row['입찰구분'],
                row['기초금액'],
                row['예정금액'],
                row['예가'],
                row['업체명'],
                row['PQ점수'],
                row['투찰금액'],
                row['추정예가'],
                row['낙찰여부']
            ))
        
        conn.commit()
        
        # 통계
        cursor.execute("SELECT COUNT(*) FROM bid_data")
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return True, f"{total_count}건 업데이트 완료"
    
    def update_all_databases(self, force=False):
        """모든 발주처 DB 업데이트"""
        print("\n" + "="*80)
        print("🔄 데이터베이스 자동 업데이트 시작")
        print("="*80 + "\n")
        
        # 변경사항 확인
        changes, current_state = self.check_for_changes()
        
        has_changes = (len(changes['new_files']) > 0 or 
                      len(changes['modified_files']) > 0 or 
                      len(changes['deleted_files']) > 0)
        
        if not has_changes and not force:
            print("✅ CSV 파일에 변경사항이 없습니다. 업데이트를 건너뜁니다.")
            print("   (강제 업데이트하려면 --force 옵션 사용)")
            return
        
        # 변경사항 출력
        if changes['new_files']:
            print(f"📄 새 파일: {len(changes['new_files'])}개")
            for f in changes['new_files']:
                print(f"   + {os.path.basename(f)}")
        
        if changes['modified_files']:
            print(f"✏️  수정된 파일: {len(changes['modified_files'])}개")
            for f in changes['modified_files']:
                print(f"   ~ {os.path.basename(f)}")
        
        if changes['deleted_files']:
            print(f"🗑️  삭제된 파일: {len(changes['deleted_files'])}개")
            for f in changes['deleted_files']:
                print(f"   - {os.path.basename(f)}")
        
        print()
        
        # 모든 발주처 가져오기
        organizations = self.get_all_organizations()
        
        if not organizations:
            print("❌ CSV 파일에서 발주처를 찾을 수 없습니다.")
            return
        
        print(f"🏢 발견된 발주처: {len(organizations)}개")
        print()
        
        # 각 발주처별 DB 업데이트
        success_count = 0
        fail_count = 0
        
        for i, org_name in enumerate(organizations, 1):
            print(f"[{i}/{len(organizations)}] 🔄 {org_name} 업데이트 중...")
            
            success, message = self.update_organization_db(org_name)
            
            if success:
                print(f"           ✅ {message}")
                success_count += 1
            else:
                print(f"           ❌ {message}")
                fail_count += 1
        
        print()
        print("="*80)
        print(f"✅ 업데이트 완료: 성공 {success_count}개, 실패 {fail_count}개")
        print(f"📅 업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        # 상태 저장
        self.save_state(current_state)
        
        return {
            'success': success_count,
            'failed': fail_count,
            'total': len(organizations),
            'changes': changes,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """메인 함수"""
    import sys
    
    updater = DatabaseAutoUpdater()
    
    # 명령줄 인자 확인
    force = '--force' in sys.argv or '-f' in sys.argv
    
    if force:
        print("🔧 강제 업데이트 모드")
    
    result = updater.update_all_databases(force=force)
    
    if result:
        # 결과 요약 출력
        print("\n📊 업데이트 결과 요약:")
        print(f"   - 총 발주처: {result['total']}개")
        print(f"   - 성공: {result['success']}개")
        print(f"   - 실패: {result['failed']}개")
        
        if result['changes']['new_files']:
            print(f"   - 새 파일: {len(result['changes']['new_files'])}개")
        if result['changes']['modified_files']:
            print(f"   - 수정된 파일: {len(result['changes']['modified_files'])}개")


if __name__ == "__main__":
    main()
