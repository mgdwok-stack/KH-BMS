#!/usr/bin/env python3
"""
업체별 PQ 순위별 투찰 성향 분석 시스템

CSV 파일로부터 각 업체의 PQ 순위별 투찰률(추정예가) 성향을 분석하고
통계 데이터베이스를 구축하는 파이프라인
"""

import pandas as pd
import sqlite3
import numpy as np
from pathlib import Path
import glob
from typing import Dict, List, Tuple, Optional


class PQStatsAnalyzer:
    """PQ 순위별 투찰 성향 분석 클래스"""
    
    def __init__(self, db_path: str = "data/bidbot_data.db"):
        """
        초기화
        
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        
        # 데이터베이스 디렉토리 생성
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터베이스 초기화
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 및 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Company_PQ_Stats 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Company_PQ_Stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                공고번호 TEXT NOT NULL,
                대표사 TEXT NOT NULL,
                업체명 TEXT,
                PQ점수 REAL,
                PQ순위 INTEGER,
                투찰률 REAL,
                기초금액 TEXT,
                예정금액 TEXT,
                예가 REAL,
                낙찰여부 TEXT,
                공고일자 TEXT,
                사업명 TEXT,
                발주처 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 인덱스 생성 (조회 성능 향상)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_rank 
            ON Company_PQ_Stats(대표사, PQ순위)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_announcement 
            ON Company_PQ_Stats(공고번호)
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✅ 데이터베이스 초기화 완료: {self.db_path}")
    
    def preprocess_csv(self, csv_path: str) -> pd.DataFrame:
        """
        CSV 파일 전처리
        
        1. PQ 순위 계산: PQ공고 NO. 기준으로 그룹화하여 PQ점수 내림차순 순위 부여
        2. 대표사 추출: 업체명에서 '+' 기준으로 분리하여 첫 번째 업체명 추출
        
        Args:
            csv_path: CSV 파일 경로
            
        Returns:
            전처리된 pandas DataFrame
        """
        print(f"\n📄 CSV 파일 읽는 중: {csv_path}")
        
        # CSV 파일 읽기
        df = pd.read_csv(csv_path, encoding='cp949', low_memory=False)
        
        print(f"   - 원본 데이터: {len(df)}건")
        
        # 1. PQ 순위 계산
        # PQ공고 NO.로 그룹화하여 PQ점수 내림차순으로 순위 부여
        # NaN 값 처리: PQ점수가 없는 행은 제외
        df = df[df['PQ점수'].notna()]
        df['PQ순위'] = df.groupby('PQ공고 NO.')['PQ점수'].rank(
            method='dense',  # 동점자는 같은 순위
            ascending=False  # 점수가 높을수록 순위가 높음
        ).astype(int)
        
        # 2. 대표사 추출
        # 업체명에서 '+' 기준으로 분리하여 첫 번째 업체 추출
        df['대표사'] = df['업체명'].apply(self._extract_lead_company)
        
        # 3. 낙찰여부 통일 (O/X → Y/N)
        if '낙찰여부' in df.columns:
            df['낙찰여부'] = df['낙찰여부'].apply(self._normalize_win_status)
        
        # 4. 컬럼명 정리
        df = df.rename(columns={
            'PQ공고 NO.': '공고번호',
            '추정예가': '투찰률'
        })
        
        print(f"   - 전처리 완료: PQ순위, 대표사 컬럼 생성")
        print(f"   - 추출된 대표사: {df['대표사'].nunique()}개")
        
        return df
    
    @staticmethod
    def _extract_lead_company(company_name: str) -> str:
        """
        업체명에서 대표사 추출
        
        Args:
            company_name: 업체명 (예: "수성+세일" 또는 "도화+케이베츠")
            
        Returns:
            대표사명 (예: "수성", "도화")
        """
        if pd.isna(company_name):
            return ""
        
        # '+' 기준으로 분리
        parts = str(company_name).split('+')
        
        # 첫 번째 부분 반환 (공백 제거)
        return parts[0].strip()
    
    @staticmethod
    def _normalize_win_status(status) -> str:
        """
        낙찰여부 통일 (O/X → Y/N)
        
        Args:
            status: 낙찰여부 ('O', 'X', 'Y', 'N', None 등)
            
        Returns:
            'Y' (낙찰) 또는 'N' (미낙찰)
        """
        if pd.isna(status):
            return 'N'
        
        status_str = str(status).strip().upper()
        
        # O → Y, X → N
        if status_str in ['O', 'Y', '1', 'TRUE', '낙찰']:
            return 'Y'
        else:
            return 'N'
    
    def insert_to_database(self, df: pd.DataFrame, clear_existing: bool = False):
        """
        전처리된 데이터를 데이터베이스에 삽입
        
        Args:
            df: 전처리된 DataFrame
            clear_existing: 기존 데이터 삭제 여부
        """
        conn = sqlite3.connect(self.db_path)
        
        if clear_existing:
            print("\n🗑️  기존 데이터 삭제 중...")
            conn.execute("DELETE FROM Company_PQ_Stats")
            conn.commit()
        
        print(f"\n💾 데이터베이스에 저장 중...")
        
        # 저장할 컬럼 선택
        columns_to_save = [
            '공고번호', '대표사', '업체명', 'PQ점수', 'PQ순위', '투찰률',
            '기초금액', '예정금액', '예가', '낙찰여부', 
            '공고일자', '사업명', '발주처'
        ]
        
        # DataFrame을 SQL에 삽입
        df[columns_to_save].to_sql(
            'Company_PQ_Stats',
            conn,
            if_exists='append',
            index=False
        )
        
        conn.commit()
        
        # 통계 출력
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Company_PQ_Stats")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT 대표사) FROM Company_PQ_Stats")
        company_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT 공고번호) FROM Company_PQ_Stats")
        announcement_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"   ✅ 저장 완료!")
        print(f"   - 총 레코드: {total_count}건")
        print(f"   - 대표사: {company_count}개")
        print(f"   - 공고: {announcement_count}개")
    
    def analyze_company_stats(
        self, 
        company_name: str, 
        threshold: float = 99.9
    ) -> Dict:
        """
        특정 업체의 PQ 순위별 투찰 성향 통계 분석
        
        Args:
            company_name: 분석할 대표사명 (예: "수성", "도화")
            threshold: 기준 투찰률 (기본값: 99.9%)
            
        Returns:
            통계 결과 딕셔너리
        """
        conn = sqlite3.connect(self.db_path)
        
        # 해당 업체의 모든 데이터 조회
        query = """
            SELECT PQ순위, 투찰률, 공고번호
            FROM Company_PQ_Stats
            WHERE 대표사 = ?
            ORDER BY PQ순위, 투찰률
        """
        
        df = pd.read_sql_query(query, conn, params=(company_name,))
        conn.close()
        
        if len(df) == 0:
            return {
                'error': f"'{company_name}' 업체의 데이터를 찾을 수 없습니다.",
                'company': company_name
            }
        
        # 순위별 통계 계산
        stats = {
            'company': company_name,
            'total_bids': len(df),
            'threshold': threshold,
            'rank_stats': {}
        }
        
        # 각 순위별로 통계 계산
        for rank in sorted(df['PQ순위'].unique()):
            rank_data = df[df['PQ순위'] == rank]['투찰률']
            
            # 기본 통계
            rank_stats = {
                'count': len(rank_data),
                'mean': round(rank_data.mean(), 2),
                'std': round(rank_data.std(), 2),
                'min': round(rank_data.min(), 2),
                'max': round(rank_data.max(), 2),
                'median': round(rank_data.median(), 2)
            }
            
            # 기준점 기반 확률 계산
            above_threshold = (rank_data >= threshold).sum()
            below_threshold = (rank_data < threshold).sum()
            
            rank_stats['above_threshold_count'] = above_threshold
            rank_stats['below_threshold_count'] = below_threshold
            rank_stats['above_threshold_probability'] = round(
                (above_threshold / len(rank_data)) * 100, 2
            )
            rank_stats['below_threshold_probability'] = round(
                (below_threshold / len(rank_data)) * 100, 2
            )
            
            stats['rank_stats'][int(rank)] = rank_stats
        
        return stats
    
    def get_company_list(self) -> List[Tuple[str, int]]:
        """
        데이터베이스에 있는 모든 대표사 목록 조회
        
        Returns:
            (대표사명, 참여 횟수) 튜플 리스트
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 대표사, COUNT(*) as count
            FROM Company_PQ_Stats
            GROUP BY 대표사
            ORDER BY count DESC
        """)
        
        companies = cursor.fetchall()
        conn.close()
        
        return companies
    
    def print_analysis_report(self, company_name: str, threshold: float = 99.9):
        """
        업체 분석 결과를 보기 좋게 출력
        
        Args:
            company_name: 대표사명
            threshold: 기준 투찰률
        """
        stats = self.analyze_company_stats(company_name, threshold)
        
        if 'error' in stats:
            print(f"\n❌ {stats['error']}")
            return
        
        print("\n" + "="*80)
        print(f"📊 '{company_name}' 업체 PQ 순위별 투찰 성향 분석")
        print("="*80)
        
        print(f"\n📈 전체 통계:")
        print(f"   - 총 입찰 참여: {stats['total_bids']}건")
        print(f"   - 기준 투찰률: {stats['threshold']}%")
        
        print(f"\n🎯 순위별 상세 분석:\n")
        
        for rank, rank_stats in sorted(stats['rank_stats'].items()):
            print(f"━━━ PQ {rank}위일 때 ━━━")
            print(f"  참여 횟수: {rank_stats['count']}건")
            print(f"  평균 투찰률: {rank_stats['mean']}%")
            print(f"  중앙값: {rank_stats['median']}%")
            print(f"  최소~최대: {rank_stats['min']}% ~ {rank_stats['max']}%")
            print(f"  표준편차: {rank_stats['std']}%")
            print()
            print(f"  📊 기준점({threshold}%) 기준:")
            print(f"     • {threshold}% 이상 투찰: {rank_stats['above_threshold_count']}건 "
                  f"({rank_stats['above_threshold_probability']}%)")
            print(f"     • {threshold}% 미만 투찰: {rank_stats['below_threshold_count']}건 "
                  f"({rank_stats['below_threshold_probability']}%)")
            print()
        
        # 전략 제안
        print("💡 투찰 전략 인사이트:")
        rank_stats = stats['rank_stats']
        
        if 1 in rank_stats:
            rank1 = rank_stats[1]
            if rank1['above_threshold_probability'] > 50:
                print(f"   • {company_name}이(가) 1위일 때: "
                      f"주로 {threshold}% 이상 투찰 (확률 {rank1['above_threshold_probability']}%)")
            else:
                print(f"   • {company_name}이(가) 1위일 때: "
                      f"주로 {threshold}% 미만 투찰 (확률 {rank1['below_threshold_probability']}%)")
        
        if 2 in rank_stats:
            rank2 = rank_stats[2]
            if rank2['below_threshold_probability'] > 50:
                print(f"   • {company_name}이(가) 2위일 때: "
                      f"주로 {threshold}% 미만 투찰 (확률 {rank2['below_threshold_probability']}%)")
            else:
                print(f"   • {company_name}이(가) 2위일 때: "
                      f"주로 {threshold}% 이상 투찰 (확률 {rank2['above_threshold_probability']}%)")
        
        print("\n" + "="*80)
    
    def process_all_csv_files(self, csv_dir: str = "data/upload_files"):
        """
        지정된 디렉토리의 모든 CSV 파일을 처리하여 DB에 저장
        
        Args:
            csv_dir: CSV 파일이 있는 디렉토리
        """
        csv_files = glob.glob(f"{csv_dir}/*.CSV") + glob.glob(f"{csv_dir}/*.csv")
        
        if not csv_files:
            print(f"❌ {csv_dir}에서 CSV 파일을 찾을 수 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print(f"🔄 PQ 통계 데이터베이스 구축 시작")
        print(f"{'='*80}")
        print(f"\n📁 발견된 CSV 파일: {len(csv_files)}개")
        
        all_data = []
        
        for csv_file in csv_files:
            try:
                df = self.preprocess_csv(csv_file)
                all_data.append(df)
            except Exception as e:
                print(f"   ❌ 오류: {e}")
                continue
        
        if all_data:
            # 모든 데이터 합치기
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # DB에 저장 (기존 데이터 삭제)
            self.insert_to_database(combined_df, clear_existing=True)
            
            print(f"\n{'='*80}")
            print(f"✅ 데이터베이스 구축 완료!")
            print(f"{'='*80}")
        else:
            print("\n❌ 처리할 데이터가 없습니다.")


def main():
    """메인 실행 함수"""
    import sys
    
    # 분석기 초기화
    analyzer = PQStatsAnalyzer()
    
    # 명령줄 인자 확인
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "build":
            # DB 구축
            analyzer.process_all_csv_files()
            
        elif command == "analyze":
            # 업체 분석
            if len(sys.argv) < 3:
                print("사용법: python3 pq_stats_analyzer.py analyze <업체명> [기준투찰률]")
                print("예시: python3 pq_stats_analyzer.py analyze 수성 99.9")
                return
            
            company_name = sys.argv[2]
            threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 99.9
            
            analyzer.print_analysis_report(company_name, threshold)
            
        elif command == "list":
            # 업체 목록 출력
            companies = analyzer.get_company_list()
            
            print("\n📋 등록된 대표사 목록:")
            print("="*60)
            for i, (name, count) in enumerate(companies, 1):
                print(f"{i:3d}. {name:20s} ({count}건)")
            print("="*60)
            print(f"총 {len(companies)}개 업체")
            
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """사용법 출력"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  PQ 순위별 투찰 성향 분석 시스템                              ║
╚════════════════════════════════════════════════════════════════════════════╝

사용법:
-------
1. 데이터베이스 구축:
   python3 pq_stats_analyzer.py build

2. 업체 분석:
   python3 pq_stats_analyzer.py analyze <업체명> [기준투찰률]
   예시: python3 pq_stats_analyzer.py analyze 수성 99.9

3. 업체 목록 보기:
   python3 pq_stats_analyzer.py list

예제:
-----
# 1단계: CSV 파일로부터 DB 구축
python3 pq_stats_analyzer.py build

# 2단계: 업체 목록 확인
python3 pq_stats_analyzer.py list

# 3단계: 특정 업체 분석
python3 pq_stats_analyzer.py analyze 도화 99.9
    """)


if __name__ == "__main__":
    main()
