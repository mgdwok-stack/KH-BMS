"""
간단한 FastAPI 데모 서버 (데이터베이스 없이 실행)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 앱 생성
app = FastAPI(
    title="Bid-Bot Clone API",
    version="1.0.0",
    description="AI 입찰 분석 솔루션 - 데모 서버"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🎯 Bid-Bot Clone API가 실행 중입니다!",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "features": [
            "입찰공고 조회 API",
            "AI 예측 API",
            "분석 및 통계 API"
        ]
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "app_name": "Bid-Bot Clone",
        "version": "1.0.0"
    }


@app.get("/api/v1/demo")
async def demo():
    """데모 데이터"""
    return {
        "message": "데모 모드입니다. 완전한 기능을 사용하려면 PostgreSQL을 설정해주세요.",
        "sample_data": {
            "bid_announcement": {
                "id": 1,
                "bid_ntce_no": "20260001234-00",
                "bid_ntce_nm": "청사 건물 유지보수 공사",
                "instt_nm": "행정안전부",
                "rgn_nm": "서울",
                "basis_prce": 1000000000
            },
            "ai_prediction": {
                "final_predicted_rate": 99.52,
                "predicted_prdprc": 995200000,
                "recommended_bid_amt": 872993044,
                "dnbp_predicted_rate": 99.54,
                "lstm_predicted_rate": 99.48
            }
        }
    }


@app.get("/api/v1/analytics/summary")
async def analytics_summary():
    """분석 요약 (데모 데이터)"""
    return {
        "total_statistics": {
            "total_announcements": 12345,
            "total_results": 10234,
            "total_predictions": 8901,
            "overall_avg_rate": 99.48
        },
        "recent_30_days": {
            "results_count": 234,
            "avg_rate": 99.51
        },
        "ai_performance": {
            "validated_predictions": 150,
            "avg_prediction_error": 0.08,
            "accuracy_rate": 94.5
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Bid-Bot Clone 데모 서버 시작...")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🔗 서버 주소: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
