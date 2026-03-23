#!/usr/bin/env python3
"""
발주처별 SQLite 데이터베이스 생성 프로그램

CSV 파일에서 데이터를 읽어 발주처별로 DB 파일을 생성합니다.
각 DB에는 사업명, 발주처, 기초금액, 예정금액, 예가, 낙찰업체 정보가 포함됩니다.
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path
import glob


def create_database(org_name: str, output_dir: str = "data/databases"):
    """
    특정 발주처의 데이터베이스를 생성합니다.
    
    Args:
        org_name: 발주처 이름 (예: "경상남도")
        output_dir: DB 파일이 저장될 디렉토리
    
    Returns:
        생성된 DB 파일 경로
    """
    # 출력 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # DB 파일 경로 생성 (발주처명.db)
    db_filename = f"{org_name}.db"
    db_path = os.path.join(output_dir, db_filename)
    
    # 기존 DB 파일이 있으면 삭제
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ 기존 DB 파일 삭제: {db_path}")
    
    # CSV 파일 찾기
    csv_files = glob.glob("data/upload_files/*.CSV") + glob.glob("data/upload_files/*.csv")
    
    if not csv_files:
        print("❌ CSV 파일을 찾을 수 없습니다!")
        return None
    
    print(f"\n📁 발견된 CSV 파일: {len(csv_files)}개")
    for csv_file in csv_files:
        print(f"  - {csv_file}")
    
    # 모든 CSV 파일에서 데이터 수집
    all_data = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='cp949', low_memory=False)
            
            # 발주처 필터링
            org_data = df[df['발주처'] == org_name]
            
            if len(org_data) > 0:
                print(f"\n✓ {csv_file}: {len(org_data)}건 발견")
                all_data.append(org_data)
            else:
                print(f"  {csv_file}: 해당 발주처 데이터 없음")
                
        except Exception as e:
            print(f"❌ {csv_file} 읽기 실패: {e}")
            continue
    
    if not all_data:
        print(f"\n❌ '{org_name}' 발주처의 데이터를 찾을 수 없습니다!")
        print("\n📋 사용 가능한 발주처 목록:")
        
        # 모든 발주처 출력
        all_orgs = set()
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='cp949')
                all_orgs.update(df['발주처'].unique())
            except:
                pass
        
        for org in sorted(all_orgs):
            print(f"  - {org}")
        
        return None
    
    # 데이터프레임 합치기
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n✓ 총 {len(combined_df)}건의 데이터 수집 완료")
    
    # 낙찰여부 정규화 (O/X → Y/N)
    def normalize_win_status(status):
        if pd.isna(status):
            return 'N'
        status_str = str(status).strip().upper()
        if status_str in ['O', 'Y', '1', 'TRUE', '낙찰']:
            return 'Y'
        else:
            return 'N'
    
    combined_df['낙찰여부'] = combined_df['낙찰여부'].apply(normalize_win_status)
    print(f"✓ 낙찰여부 정규화 완료 (O/X → Y/N)")
    
    # SQLite DB 생성 및 데이터 저장
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
    
    # 통계 조회
    cursor.execute("SELECT COUNT(*) FROM bid_data")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT project_name) FROM bid_data")
    project_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM bid_data WHERE is_winner = 'O'")
    winner_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ 데이터베이스 생성 완료!")
    print(f"{'='*60}")
    print(f"📍 파일 위치: {db_path}")
    print(f"📊 통계:")
    print(f"   - 전체 입찰 기록: {total_count}건")
    print(f"   - 프로젝트 수: {project_count}개")
    print(f"   - 낙찰 기록: {winner_count}건")
    print(f"{'='*60}\n")
    
    return db_path


def view_database(db_path: str):
    """데이터베이스 내용 조회"""
    if not os.path.exists(db_path):
        print(f"❌ DB 파일이 존재하지 않습니다: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM bid_data ORDER BY announcement_date DESC", conn)
    conn.close()
    
    print("\n📊 데이터베이스 내용 미리보기:")
    print("="*80)
    
    # 주요 컬럼만 출력
    display_columns = ['project_name', 'organization', 'base_amount', 
                      'estimated_price', 'estimated_rate', 'company_name', 'is_winner']
    
    if len(df) > 0:
        print(df[display_columns].head(10).to_string(index=False))
        
        if len(df) > 10:
            print(f"\n... 외 {len(df)-10}건")
    else:
        print("데이터가 없습니다.")
    
    print("="*80)


def list_all_organizations():
    """사용 가능한 모든 발주처 목록 출력"""
    csv_files = glob.glob("data/upload_files/*.CSV") + glob.glob("data/upload_files/*.csv")
    
    if not csv_files:
        print("❌ CSV 파일을 찾을 수 없습니다!")
        return []
    
    all_orgs = set()
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='cp949', low_memory=False)
            # NaN 값 제거하고 문자열만 추가
            orgs = df['발주처'].dropna().astype(str).unique()
            all_orgs.update([org for org in orgs if org and org != 'nan'])
        except Exception as e:
            print(f"❌ {csv_file} 읽기 실패: {e}")
            continue
    
    # NaN과 빈 문자열 제거
    all_orgs = {org for org in all_orgs if org and str(org) != 'nan'}
    
    return sorted(all_orgs)


def interactive_mode():
    """대화형 모드"""
    print("="*60)
    print("🏢 발주처별 데이터베이스 생성 프로그램")
    print("="*60)
    
    # 사용 가능한 발주처 목록
    orgs = list_all_organizations()
    
    if not orgs:
        print("\n❌ CSV 파일에서 발주처 정보를 찾을 수 없습니다!")
        return
    
    print(f"\n📋 사용 가능한 발주처 목록 ({len(orgs)}개):")
    for i, org in enumerate(orgs, 1):
        print(f"   {i}. {org}")
    
    print("\n" + "="*60)
    org_name = input("📝 발주처 이름을 입력하세요 (또는 번호): ").strip()
    
    # 번호로 입력한 경우
    if org_name.isdigit():
        idx = int(org_name) - 1
        if 0 <= idx < len(orgs):
            org_name = orgs[idx]
        else:
            print("❌ 잘못된 번호입니다!")
            return
    
    print(f"\n🔄 '{org_name}' 데이터베이스 생성 중...\n")
    
    # DB 생성
    db_path = create_database(org_name)
    
    if db_path:
        # 내용 미리보기
        view_database(db_path)
        
        print("\n✅ 완료!")
        print(f"💾 생성된 파일: {db_path}")
        print(f"\n🔍 SQLite로 직접 조회하려면:")
        print(f"   sqlite3 {db_path}")
        print(f"   > SELECT * FROM bid_data LIMIT 5;")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 명령줄 인자로 발주처 이름 전달
        org_name = sys.argv[1]
        db_path = create_database(org_name)
        if db_path:
            view_database(db_path)
    else:
        # 대화형 모드
        interactive_mode()
