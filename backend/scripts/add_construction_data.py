#!/usr/bin/env python3
"""
토목/건설 관련 주요 발주기관 데이터 추가
"""
import sys
import os
from pathlib import Path
import random
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.database import BidAnnouncement, BidResult

# 토목/건설 관련 주요 발주기관
CONSTRUCTION_INSTITUTIONS = [
    '한국전력공사',
    '한국도로공사',
    '한국철도공사',
    '한국수자원공사',
    '한국토지주택공사',
    '국토교통부',
    '서울시설공단',
    '인천도시공사',
    '경기도시공사',
    '부산도시공사',
    '한국농어촌공사',
    '한국가스공사',
    '한국석유공사',
    '산림청',
    '해양수산부'
]

# 토목/건설 관련 업종
CONSTRUCTION_INDUSTRIES = [
    '토목건축공사',
    '전문공사',
    '전기공사',
    '조경공사',
    '시설물유지관리',
    '정보통신공사',
    '소방시설공사',
    '문화재수리공사'
]

REGIONS = [
    '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
    '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'
]

def add_construction_data(num_records=100):
    """토목/건설 데이터 추가"""
    print("🏗️ 토목/건설 관련 발주기관 데이터 추가")
    print("=" * 70)
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 현재 최대 ID 찾기
        max_id = session.query(BidAnnouncement).count()
        base_date = datetime(2024, 12, 1)
        
        announcements_created = 0
        results_created = 0
        
        for i in range(num_records):
            # 날짜 생성
            ntce_date = base_date + timedelta(days=random.randint(0, 60))
            bid_close_date = ntce_date + timedelta(days=random.randint(7, 21))
            opng_date = bid_close_date + timedelta(days=random.randint(1, 3))
            
            # 토목/건설 관련 기관 및 업종 선택
            institution = random.choice(CONSTRUCTION_INSTITUTIONS)
            industry = random.choice(CONSTRUCTION_INDUSTRIES)
            region = random.choice(REGIONS)
            
            # 기초금액 (토목/건설은 보통 고액)
            # 500M ~ 20B KRW
            basis_prc = random.randint(500_000_000, 20_000_000_000)
            basis_prc = round(basis_prc / 1_000_000) * 1_000_000
            
            # 공고번호
            bid_ntce_no = f"2024{20000 + max_id + i:05d}-00"
            
            # 공고 생성
            announcement = BidAnnouncement(
                bid_ntce_no=bid_ntce_no,
                bid_ntce_nm=f"{institution} {industry} 공사",
                ntce_instt_nm=institution,
                dminstt_nm=region,
                industry_ty_nm=industry,
                ntce_dt=ntce_date.strftime('%Y%m%d%H%M%S'),
                bid_clse_dt=bid_close_date.strftime('%Y%m%d%H%M%S'),
                opng_dt=opng_date.strftime('%Y%m%d%H%M%S'),
                basis_prc=float(basis_prc),
                bid_status='개찰완료',
                raw_data={
                    'bidNtceNo': bid_ntce_no,
                    'bidNtceNm': f"{institution} {industry} 공사",
                    'ntceInsttNm': institution,
                    'dminsttNm': region,
                    'industryTyNm': industry,
                    'basisPrce': str(basis_prc)
                }
            )
            session.add(announcement)
            announcements_created += 1
            
            # 낙찰 결과 생성 (90% 확률)
            if random.random() < 0.90:
                # 사정률 (토목/건설은 99~101% 사이에 집중)
                prdprc_rate = random.gauss(100.0, 1.0)
                prdprc_rate = max(98.0, min(102.0, prdprc_rate))
                
                # 예정가격
                prdprc = basis_prc * (prdprc_rate / 100.0)
                
                # 낙찰율 (88~92%)
                sucbid_rate = random.gauss(90.0, 1.0)
                sucbid_rate = max(88.0, min(92.0, sucbid_rate))
                
                # 낙찰금액
                sucbid_prc = prdprc * (sucbid_rate / 100.0)
                
                result = BidResult(
                    bid_ntce_no=bid_ntce_no,
                    opng_dt=opng_date.strftime('%Y%m%d%H%M%S'),
                    prdprc_rate=round(prdprc_rate, 2),
                    prdprc=round(prdprc, 0),
                    sucbid_prc=round(sucbid_prc, 0),
                    sucbid_rate=round(sucbid_rate, 2),
                    bidprc_plnprc=round(sucbid_prc, 0),
                    raw_data={
                        'bidNtceNo': bid_ntce_no,
                        'prdprcRate': str(round(prdprc_rate, 2)),
                        'prdprc': str(round(prdprc, 0)),
                        'sucbidPrc': str(round(sucbid_prc, 0)),
                        'sucbidRate': str(round(sucbid_rate, 2))
                    }
                )
                session.add(result)
                results_created += 1
        
        session.commit()
        
        print(f"\n✅ 토목/건설 데이터 추가 완료!")
        print(f"  📊 추가된 공고: {announcements_created}건")
        print(f"  📊 추가된 낙찰: {results_created}건")
        print(f"  📊 성공률: {results_created/announcements_created*100:.1f}%")
        
        # 기관별 통계
        print(f"\n🏛️ 추가된 발주기관 통계:")
        from sqlalchemy import func
        stats = session.query(
            BidAnnouncement.ntce_instt_nm,
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidAnnouncement.basis_prc).label('avg_price')
        ).filter(
            BidAnnouncement.ntce_instt_nm.in_(CONSTRUCTION_INSTITUTIONS)
        ).group_by(
            BidAnnouncement.ntce_instt_nm
        ).order_by(
            func.count(BidAnnouncement.id).desc()
        ).all()
        
        for inst, count, avg_price in stats:
            print(f"  • {inst:20s}: {count:3d}건, 평균 {avg_price/1_000_000_000:.2f}B KRW")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    add_construction_data(100)
