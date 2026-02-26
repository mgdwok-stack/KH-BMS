#!/usr/bin/env python3
"""
Database initialization script
Creates tables and indexes for Bid-Bot Clone
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings
from app.models.database import Base, BidAnnouncement, BidResult, Prediction, UserPreference

def init_database():
    """Initialize database with tables and indexes"""
    print("🚀 Bid-Bot Clone - Database Initialization")
    print("=" * 60)
    
    # Create engine
    print(f"📍 Connecting to: {settings.DATABASE_URL[:50]}...")
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # Test connection
        with engine.connect() as conn:
            if 'sqlite' in settings.DATABASE_URL:
                result = conn.execute(text("SELECT sqlite_version();"))
                version = result.fetchone()[0]
                print(f"✅ SQLite connected: v{version}")
            else:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL connected: {version.split(',')[0]}")
        
        # Create all tables
        print("\n📊 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Create indexes
        print("\n🔍 Creating indexes...")
        with engine.connect() as conn:
            # Indexes for bid_announcements
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bid_announcement_ntce_dt 
                ON bid_announcements(ntce_dt DESC);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bid_announcement_region 
                ON bid_announcements(dminstt_nm);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bid_announcement_industry 
                ON bid_announcements(industry_ty_nm);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bid_announcement_status 
                ON bid_announcements(bid_status);
            """))
            
            # Indexes for bid_results
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bid_result_opng_dt 
                ON bid_results(opng_dt DESC);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bid_result_rate 
                ON bid_results(prdprc_rate);
            """))
            
            # Indexes for predictions
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_prediction_created 
                ON predictions(predicted_at DESC);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_prediction_status 
                ON predictions(status);
            """))
            
            conn.commit()
            print("✅ All indexes created successfully")
        
        # Print table information
        print("\n📋 Database Schema:")
        with engine.connect() as conn:
            if 'sqlite' in settings.DATABASE_URL:
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name;
                """))
                for row in result:
                    count_result = conn.execute(text(f"PRAGMA table_info({row[0]});"))
                    column_count = len(list(count_result))
                    print(f"  • {row[0]}: {column_count} columns")
            else:
                result = conn.execute(text("""
                    SELECT table_name, 
                           (SELECT COUNT(*) FROM information_schema.columns 
                            WHERE table_name = t.table_name) as column_count
                    FROM information_schema.tables t
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """))
                for row in result:
                    print(f"  • {row[0]}: {row[1]} columns")
        
        print("\n" + "=" * 60)
        print("✅ Database initialization completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    init_database()
