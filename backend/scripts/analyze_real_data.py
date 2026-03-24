#!/usr/bin/env python3
"""
Analyze real bid data from database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.database import BidAnnouncement, BidResult
import pandas as pd

def analyze_data():
    print("🚀 Bid-Bot Clone - Data Analysis")
    print("=" * 70)
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Basic Statistics
        total_announcements = session.query(BidAnnouncement).count()
        total_results = session.query(BidResult).count()
        
        print(f"\n📊 Database Statistics:")
        print(f"  • Total Announcements: {total_announcements:,}")
        print(f"  • Total Results: {total_results:,}")
        print(f"  • Success Rate: {total_results/total_announcements*100:.1f}%")
        
        # 2. Bid Announcement Statistics
        avg_basis_prc = session.query(func.avg(BidAnnouncement.basis_prc)).scalar()
        min_basis_prc = session.query(func.min(BidAnnouncement.basis_prc)).scalar()
        max_basis_prc = session.query(func.max(BidAnnouncement.basis_prc)).scalar()
        
        print(f"\n💰 Basis Price Analysis:")
        print(f"  • Average: {avg_basis_prc/1_000_000_000:.2f}B KRW")
        print(f"  • Minimum: {min_basis_prc/1_000_000:.0f}M KRW")
        print(f"  • Maximum: {max_basis_prc/1_000_000_000:.2f}B KRW")
        
        # 3. Prediction Rate Statistics
        avg_prdprc_rate = session.query(func.avg(BidResult.prdprc_rate)).scalar()
        min_prdprc_rate = session.query(func.min(BidResult.prdprc_rate)).scalar()
        max_prdprc_rate = session.query(func.max(BidResult.prdprc_rate)).scalar()
        
        print(f"\n🎯 Prediction Rate (사정률) Analysis:")
        print(f"  • Average: {avg_prdprc_rate:.2f}%")
        print(f"  • Minimum: {min_prdprc_rate:.2f}%")
        print(f"  • Maximum: {max_prdprc_rate:.2f}%")
        print(f"  • Range: {max_prdprc_rate - min_prdprc_rate:.2f}%")
        
        # 4. Regional Analysis
        print(f"\n🗺️  Regional Distribution (Top 10):")
        regional_stats = session.query(
            BidAnnouncement.dminstt_nm,
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidAnnouncement.basis_prc).label('avg_price')
        ).group_by(BidAnnouncement.dminstt_nm).order_by(func.count(BidAnnouncement.id).desc()).limit(10).all()
        
        for region, count, avg_price in regional_stats:
            print(f"  • {region:8s}: {count:3d} bids, avg {avg_price/1_000_000_000:.2f}B KRW")
        
        # 5. Industry Analysis
        print(f"\n🏭 Industry Distribution (Top 10):")
        industry_stats = session.query(
            BidAnnouncement.industry_ty_nm,
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidAnnouncement.basis_prc).label('avg_price')
        ).group_by(BidAnnouncement.industry_ty_nm).order_by(func.count(BidAnnouncement.id).desc()).limit(10).all()
        
        for industry, count, avg_price in industry_stats:
            print(f"  • {industry:20s}: {count:3d} bids, avg {avg_price/1_000_000_000:.2f}B KRW")
        
        # 6. Institution Analysis
        print(f"\n🏛️  Institution Distribution (Top 10):")
        institution_stats = session.query(
            BidAnnouncement.ntce_instt_nm,
            func.count(BidAnnouncement.id).label('count'),
            func.avg(BidAnnouncement.basis_prc).label('avg_price')
        ).group_by(BidAnnouncement.ntce_instt_nm).order_by(func.count(BidAnnouncement.id).desc()).limit(10).all()
        
        for institution, count, avg_price in institution_stats:
            print(f"  • {institution:20s}: {count:3d} bids, avg {avg_price/1_000_000_000:.2f}B KRW")
        
        # 7. Prediction Rate Distribution
        print(f"\n📈 Prediction Rate Distribution:")
        rate_ranges = [
            (0, 95, '< 95%'),
            (95, 98, '95-98%'),
            (98, 100, '98-100%'),
            (100, 102, '100-102%'),
            (102, 105, '102-105%'),
            (105, 1000, '> 105%')
        ]
        
        for min_rate, max_rate, label in rate_ranges:
            count = session.query(BidResult).filter(
                BidResult.prdprc_rate >= min_rate,
                BidResult.prdprc_rate < max_rate
            ).count()
            if count > 0:
                pct = count / total_results * 100
                bar = '█' * int(pct / 2)
                print(f"  • {label:10s}: {count:3d} ({pct:5.1f}%) {bar}")
        
        # 8. Sample Records
        print(f"\n📋 Sample Records (First 5):")
        samples = session.query(BidAnnouncement, BidResult).join(
            BidResult, BidAnnouncement.bid_ntce_no == BidResult.bid_ntce_no
        ).limit(5).all()
        
        for announcement, result in samples:
            print(f"\n  📌 {announcement.bid_ntce_no}")
            print(f"     Name: {announcement.bid_ntce_nm[:50]}")
            print(f"     Institution: {announcement.ntce_instt_nm}")
            print(f"     Region: {announcement.dminstt_nm}")
            print(f"     Basis Price: {announcement.basis_prc/1_000_000_000:.2f}B KRW")
            print(f"     Prediction Rate: {result.prdprc_rate:.2f}%")
            print(f"     Success Bid Rate: {result.sucbid_rate:.2f}%")
        
        print("\n" + "=" * 70)
        print("✅ Analysis Complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    analyze_data()
