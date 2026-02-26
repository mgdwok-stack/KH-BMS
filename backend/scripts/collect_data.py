#!/usr/bin/env python3
"""
Real data collection script from 나라장터 API
Fetches bid announcements and results
"""
import sys
import os
from pathlib import Path
import argparse
from datetime import datetime, timedelta
import time
import requests
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.database import BidAnnouncement, BidResult

class DataCollector:
    """Collect data from 나라장터 API"""
    
    def __init__(self):
        self.api_key = settings.PROCUREMENT_API_KEY
        self.base_url = "https://apis.data.go.kr/1230000/ScsbidInfoService"
        self.engine = create_engine(settings.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
    def fetch_announcements(self, in_qry_dt: str, num_of_rows: int = 100) -> List[Dict]:
        """Fetch bid announcements for a specific date"""
        url = f"{self.base_url}/getDataSetOpnStdBidPblancInfo"
        
        params = {
            'serviceKey': self.api_key,
            'pageNo': 1,
            'numOfRows': num_of_rows,
            'type': 'json',
            'inqryDiv': '1',  # 입찰공고
            'inqryBgnDt': in_qry_dt,
            'inqryEndDt': in_qry_dt
        }
        
        try:
            print(f"  📡 Fetching announcements for {in_qry_dt}...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"  ⚠️  API returned status {response.status_code}")
                return []
            
            data = response.json()
            
            # Handle different response structures
            if 'response' in data:
                body = data['response'].get('body', {})
                items = body.get('items', [])
                
                # Items can be a list or a dict with 'item' key
                if isinstance(items, dict):
                    items = items.get('item', [])
                
                # Ensure items is a list
                if not isinstance(items, list):
                    items = [items] if items else []
                
                total_count = body.get('totalCount', len(items))
                print(f"  ✅ Found {len(items)} announcements (total: {total_count})")
                return items
            else:
                print(f"  ⚠️  Unexpected response format")
                return []
                
        except Exception as e:
            print(f"  ❌ Error fetching announcements: {e}")
            return []
    
    def fetch_results(self, in_qry_dt: str, num_of_rows: int = 100) -> List[Dict]:
        """Fetch bid results for a specific date"""
        url = f"{self.base_url}/getDataSetOpnStdScsbidInfo"
        
        params = {
            'serviceKey': self.api_key,
            'pageNo': 1,
            'numOfRows': num_of_rows,
            'type': 'json',
            'inqryDiv': '2',  # 낙찰결과
            'inqryBgnDt': in_qry_dt,
            'inqryEndDt': in_qry_dt
        }
        
        try:
            print(f"  📡 Fetching results for {in_qry_dt}...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"  ⚠️  API returned status {response.status_code}")
                return []
            
            data = response.json()
            
            if 'response' in data:
                body = data['response'].get('body', {})
                items = body.get('items', [])
                
                if isinstance(items, dict):
                    items = items.get('item', [])
                
                if not isinstance(items, list):
                    items = [items] if items else []
                
                total_count = body.get('totalCount', len(items))
                print(f"  ✅ Found {len(items)} results (total: {total_count})")
                return items
            else:
                print(f"  ⚠️  Unexpected response format")
                return []
                
        except Exception as e:
            print(f"  ❌ Error fetching results: {e}")
            return []
    
    def save_announcements(self, items: List[Dict]) -> int:
        """Save announcements to database"""
        session = self.Session()
        saved_count = 0
        
        try:
            for item in items:
                # Check if already exists
                bid_ntce_no = item.get('bidNtceNo')
                if not bid_ntce_no:
                    continue
                
                existing = session.query(BidAnnouncement).filter_by(
                    bid_ntce_no=bid_ntce_no
                ).first()
                
                if existing:
                    continue
                
                # Parse basis price
                basis_prc = item.get('basisPrce')
                if basis_prc:
                    try:
                        basis_prc = float(str(basis_prc).replace(',', ''))
                    except:
                        basis_prc = None
                
                # Create new announcement
                announcement = BidAnnouncement(
                    bid_ntce_no=bid_ntce_no,
                    bid_ntce_nm=item.get('bidNtceNm'),
                    ntce_instt_nm=item.get('ntceInsttNm'),
                    dminstt_nm=item.get('dminsttNm'),
                    industry_ty_nm=item.get('industryTyNm'),
                    ntce_dt=item.get('ntceDt'),
                    bid_clse_dt=item.get('bidClseDt'),
                    opng_dt=item.get('opngDt'),
                    basis_prc=basis_prc,
                    bid_status='진행중' if not item.get('opngDt') else '개찰완료',
                    raw_data=item
                )
                
                session.add(announcement)
                saved_count += 1
            
            session.commit()
            return saved_count
            
        except Exception as e:
            session.rollback()
            print(f"  ❌ Error saving announcements: {e}")
            return 0
        finally:
            session.close()
    
    def save_results(self, items: List[Dict]) -> int:
        """Save results to database"""
        session = self.Session()
        saved_count = 0
        
        try:
            for item in items:
                bid_ntce_no = item.get('bidNtceNo')
                if not bid_ntce_no:
                    continue
                
                existing = session.query(BidResult).filter_by(
                    bid_ntce_no=bid_ntce_no
                ).first()
                
                if existing:
                    continue
                
                # Parse numeric fields
                def parse_float(value):
                    if value:
                        try:
                            return float(str(value).replace(',', ''))
                        except:
                            return None
                    return None
                
                # Create new result
                result = BidResult(
                    bid_ntce_no=bid_ntce_no,
                    opng_dt=item.get('opngDt'),
                    prdprc_rate=parse_float(item.get('prdprcRate')),
                    prdprc=parse_float(item.get('prdprc')),
                    sucbid_prc=parse_float(item.get('sucbidPrc')),
                    sucbid_rate=parse_float(item.get('sucbidRate')),
                    bidprc_plnprc=parse_float(item.get('bidprcPlnprc')),
                    raw_data=item
                )
                
                session.add(result)
                saved_count += 1
            
            session.commit()
            return saved_count
            
        except Exception as e:
            session.rollback()
            print(f"  ❌ Error saving results: {e}")
            return 0
        finally:
            session.close()
    
    def collect_date_range(self, start_date: datetime, end_date: datetime):
        """Collect data for a date range"""
        print("🚀 Bid-Bot Clone - Data Collection")
        print("=" * 60)
        print(f"📅 Period: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        current_date = start_date
        total_announcements = 0
        total_results = 0
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y%m%d')
            print(f"\n📆 Processing {current_date.strftime('%Y-%m-%d')}...")
            
            # Fetch and save announcements
            announcements = self.fetch_announcements(date_str)
            if announcements:
                saved = self.save_announcements(announcements)
                total_announcements += saved
                print(f"  💾 Saved {saved} new announcements")
            
            # Fetch and save results
            results = self.fetch_results(date_str)
            if results:
                saved = self.save_results(results)
                total_results += saved
                print(f"  💾 Saved {saved} new results")
            
            # Rate limiting
            time.sleep(0.5)
            
            # Move to next day
            current_date += timedelta(days=1)
        
        print("\n" + "=" * 60)
        print("✅ Data Collection Complete!")
        print(f"  📊 Total Announcements: {total_announcements}")
        print(f"  📊 Total Results: {total_results}")
        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Collect bid data from 나라장터 API')
    parser.add_argument('--mode', choices=['recent', 'historical'], default='recent',
                        help='Collection mode: recent (last 7 days) or historical (date range)')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to collect (for recent mode)')
    parser.add_argument('--start-date', type=str,
                        help='Start date (YYYY-MM-DD) for historical mode')
    parser.add_argument('--end-date', type=str,
                        help='End date (YYYY-MM-DD) for historical mode')
    
    args = parser.parse_args()
    
    collector = DataCollector()
    
    if args.mode == 'recent':
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
    else:
        if not args.start_date or not args.end_date:
            print("❌ Error: --start-date and --end-date required for historical mode")
            sys.exit(1)
        
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    collector.collect_date_range(start_date, end_date)

if __name__ == "__main__":
    main()
