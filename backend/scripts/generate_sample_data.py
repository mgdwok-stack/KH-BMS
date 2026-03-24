#!/usr/bin/env python3
"""
Generate realistic sample bid data for demonstration
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

# Sample data pools
INSTITUTIONS = [
    '행정안전부', '국토교통부', '환경부', '산업통상자원부', '보건복지부',
    '서울특별시', '부산광역시', '인천광역시', '대전광역시', '광주광역시',
    '한국도로공사', '한국철도공사', '한국수자원공사', '한국토지주택공사', '한국전력공사'
]

REGIONS = [
    '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
    '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'
]

INDUSTRIES = [
    '토목건축공사', '전문공사', '전기공사', '정보통신공사', '소방시설공사',
    '문화재수리공사', '조경공사', '산림사업', '시설물유지관리', '전기통신공사'
]

def generate_sample_data(num_announcements=200):
    """Generate sample bid data"""
    print("🚀 Generating sample bid data...")
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Generate announcements
        base_date = datetime(2024, 12, 1)
        announcements_created = 0
        results_created = 0
        
        for i in range(num_announcements):
            # Random dates
            ntce_date = base_date + timedelta(days=random.randint(0, 60))
            bid_close_date = ntce_date + timedelta(days=random.randint(7, 21))
            opng_date = bid_close_date + timedelta(days=random.randint(1, 3))
            
            # Random basis price (100M ~ 10B KRW)
            basis_prc = random.randint(100_000_000, 10_000_000_000)
            basis_prc = round(basis_prc / 1_000_000) * 1_000_000  # Round to millions
            
            # Create announcement
            bid_ntce_no = f"2024{10000 + i:05d}-00"
            institution = random.choice(INSTITUTIONS)
            region = random.choice(REGIONS)
            industry = random.choice(INDUSTRIES)
            
            announcement = BidAnnouncement(
                bid_ntce_no=bid_ntce_no,
                bid_ntce_nm=f"{institution} {industry}",
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
                    'bidNtceNm': f"{institution} {industry}",
                    'ntceInsttNm': institution,
                    'dminsttNm': region,
                    'industryTyNm': industry,
                    'basisPrce': str(basis_prc)
                }
            )
            session.add(announcement)
            announcements_created += 1
            
            # Generate result (85% success rate)
            if random.random() < 0.85:
                # Realistic prediction rate (95% ~ 105%)
                prdprc_rate = random.gauss(100.0, 2.5)
                prdprc_rate = max(95.0, min(105.0, prdprc_rate))
                
                # Calculate predicted price
                prdprc = basis_prc * (prdprc_rate / 100.0)
                
                # Success bid rate (usually 88% ~ 92% of predicted price)
                sucbid_rate = random.gauss(90.0, 1.5)
                sucbid_rate = max(87.0, min(93.0, sucbid_rate))
                
                # Calculate success bid price
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
        
        print(f"\n✅ Sample data generated successfully!")
        print(f"  📊 Announcements: {announcements_created}")
        print(f"  📊 Results: {results_created}")
        print(f"  📊 Success Rate: {results_created/announcements_created*100:.1f}%")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    generate_sample_data(200)
