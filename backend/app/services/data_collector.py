"""
조달청 나라장터 Open API 데이터 수집 서비스
"""
import httpx
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import time

from ..config import settings
from ..models.bid import BidAnnouncement
from ..models.result import BidResult

logger = logging.getLogger(__name__)


class DataCollector:
    """
    조달청 공공데이터 Open API 연동 서비스
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.PROCUREMENT_API_KEY
        self.base_url = settings.PROCUREMENT_API_BASE_URL
        self.max_retries = settings.MAX_RETRIES
        self.timeout = settings.REQUEST_TIMEOUT
        
        if not self.api_key:
            logger.warning("PROCUREMENT_API_KEY가 설정되지 않았습니다. API 호출이 실패할 수 있습니다.")
    
    async def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        retry_count: int = 0
    ) -> Optional[Dict]:
        """
        조달청 API HTTP 요청 (재시도 로직 포함)
        
        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터
            retry_count: 현재 재시도 횟수
            
        Returns:
            API 응답 데이터 또는 None
        """
        try:
            # API 키를 파라미터에 추가
            params['serviceKey'] = self.api_key
            params['type'] = 'json'  # JSON 응답 요청
            
            url = f"{self.base_url}/{endpoint}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"API 요청: {endpoint}, 파라미터: {params}")
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return data
                elif response.status_code == 429:  # Rate limit
                    logger.warning(f"API Rate Limit 초과. 10초 대기 후 재시도...")
                    time.sleep(10)
                    if retry_count < self.max_retries:
                        return await self._make_request(endpoint, params, retry_count + 1)
                else:
                    logger.error(f"API 요청 실패: {response.status_code}, {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"API 요청 타임아웃: {endpoint}")
            if retry_count < self.max_retries:
                logger.info(f"재시도 {retry_count + 1}/{self.max_retries}...")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return await self._make_request(endpoint, params, retry_count + 1)
            return None
            
        except Exception as e:
            logger.error(f"API 요청 중 예외 발생: {e}")
            return None
    
    async def collect_bid_announcements(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        num_of_rows: int = 100
    ) -> List[Dict]:
        """
        입찰공고 정보 수집
        API: getDataSetOpnStdBidPblancInfo
        
        Args:
            start_date: 조회 시작일 (YYYYMMDD)
            end_date: 조회 종료일 (YYYYMMDD)
            page: 페이지 번호
            num_of_rows: 한 페이지 결과 수
            
        Returns:
            입찰공고 데이터 리스트
        """
        endpoint = "getDataSetOpnStdBidPblancInfo"
        
        # 기본값: 오늘부터 30일 후까지
        if not start_date:
            start_date = datetime.now().strftime("%Y%m%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y%m%d")
        
        params = {
            'inqryBgnDt': start_date,  # 조회 시작일
            'inqryEndDt': end_date,    # 조회 종료일
            'pageNo': page,
            'numOfRows': num_of_rows
        }
        
        response = await self._make_request(endpoint, params)
        
        if not response:
            return []
        
        # 응답 데이터 파싱
        try:
            body = response.get('response', {}).get('body', {})
            items = body.get('items', [])
            
            if isinstance(items, dict):
                items = [items]  # 단일 결과인 경우 리스트로 변환
            
            total_count = body.get('totalCount', 0)
            logger.info(f"입찰공고 수집 완료: {len(items)}건 (전체: {total_count}건)")
            
            return items
            
        except Exception as e:
            logger.error(f"입찰공고 데이터 파싱 오류: {e}")
            return []
    
    async def collect_bid_results(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        num_of_rows: int = 100
    ) -> List[Dict]:
        """
        낙찰결과 정보 수집
        API: getDataSetOpnStdScsbidInfo
        
        Args:
            start_date: 개찰 시작일 (YYYYMMDD)
            end_date: 개찰 종료일 (YYYYMMDD)
            page: 페이지 번호
            num_of_rows: 한 페이지 결과 수
            
        Returns:
            낙찰결과 데이터 리스트
        """
        endpoint = "getDataSetOpnStdScsbidInfo"
        
        # 기본값: 30일 전부터 오늘까지
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        
        params = {
            'inqryBgnDt': start_date,  # 개찰 시작일
            'inqryEndDt': end_date,    # 개찰 종료일
            'pageNo': page,
            'numOfRows': num_of_rows
        }
        
        response = await self._make_request(endpoint, params)
        
        if not response:
            return []
        
        # 응답 데이터 파싱
        try:
            body = response.get('response', {}).get('body', {})
            items = body.get('items', [])
            
            if isinstance(items, dict):
                items = [items]
            
            total_count = body.get('totalCount', 0)
            logger.info(f"낙찰결과 수집 완료: {len(items)}건 (전체: {total_count}건)")
            
            return items
            
        except Exception as e:
            logger.error(f"낙찰결과 데이터 파싱 오류: {e}")
            return []
    
    def save_bid_announcement(self, data: Dict) -> Optional[BidAnnouncement]:
        """
        입찰공고 데이터를 DB에 저장
        
        Args:
            data: API에서 받은 입찰공고 데이터
            
        Returns:
            저장된 BidAnnouncement 객체 또는 None
        """
        try:
            # 중복 체크 (bid_ntce_no 기준)
            bid_ntce_no = data.get('bidNtceNo')
            existing = self.db.query(BidAnnouncement).filter(
                BidAnnouncement.bid_ntce_no == bid_ntce_no
            ).first()
            
            if existing:
                logger.debug(f"이미 존재하는 입찰공고: {bid_ntce_no}")
                # 기존 데이터 업데이트 (상태 변경 등)
                existing.bid_status = self._determine_bid_status(data)
                existing.bidder_count = data.get('bidderCount', 0)
                self.db.commit()
                return existing
            
            # 새로운 입찰공고 생성
            announcement = BidAnnouncement(
                bid_ntce_no=data.get('bidNtceNo'),
                bid_ntce_ord=data.get('bidNtceOrd'),
                bid_ntce_nm=data.get('bidNtceNm'),
                instt_cd=data.get('insttCd'),
                instt_nm=data.get('insttNm'),
                dminstt_cd=data.get('dminsttCd'),
                dminstt_nm=data.get('dminsttNm'),
                bid_methd_nm=data.get('bidMethdNm'),
                cntrct_cnclsn_methd_nm=data.get('cntrctCnclsnMethdNm'),
                presmpt_prce=self._parse_int(data.get('presmptPrce')),
                basis_prce=self._parse_int(data.get('basisPrce')),
                prdprc_rate=self._parse_float(data.get('prdprcRate')),
                bid_qlfct_rgst_dt=self._parse_datetime(data.get('bidQlfctRgstDt')),
                bid_begdt=self._parse_datetime(data.get('bidBegDt')),
                bid_clsedt=self._parse_datetime(data.get('bidClseDt')),
                opengdt=self._parse_datetime(data.get('opengDt')),
                rgn_cd=data.get('rgnCd'),
                rgn_nm=data.get('rgnNm'),
                induty_ty_cd=data.get('indutyTyCd'),
                induty_ty_nm=data.get('indutyTyNm'),
                lcns_nm=data.get('lcnsNm'),
                bid_notice_dtl_url=data.get('bidNoticeDtlUrl'),
                bid_status=self._determine_bid_status(data)
            )
            
            self.db.add(announcement)
            self.db.commit()
            self.db.refresh(announcement)
            
            logger.info(f"입찰공고 저장 완료: {bid_ntce_no}")
            return announcement
            
        except Exception as e:
            logger.error(f"입찰공고 저장 실패: {e}")
            self.db.rollback()
            return None
    
    def save_bid_result(self, data: Dict) -> Optional[BidResult]:
        """
        낙찰결과 데이터를 DB에 저장
        
        Args:
            data: API에서 받은 낙찰결과 데이터
            
        Returns:
            저장된 BidResult 객체 또는 None
        """
        try:
            # 중복 체크
            bid_ntce_no = data.get('bidNtceNo')
            existing = self.db.query(BidResult).filter(
                BidResult.bid_ntce_no == bid_ntce_no
            ).first()
            
            if existing:
                logger.debug(f"이미 존재하는 낙찰결과: {bid_ntce_no}")
                return existing
            
            # 해당 입찰공고 찾기
            announcement = self.db.query(BidAnnouncement).filter(
                BidAnnouncement.bid_ntce_no == bid_ntce_no
            ).first()
            
            if not announcement:
                logger.warning(f"입찰공고를 찾을 수 없음: {bid_ntce_no}")
                # 입찰공고가 없으면 생성 (낙찰결과에서 역으로)
                announcement = self._create_announcement_from_result(data)
            
            # 낙찰결과 생성
            result = BidResult(
                bid_announcement_id=announcement.id if announcement else None,
                bid_ntce_no=data.get('bidNtceNo'),
                bid_ntce_ord=data.get('bidNtceOrd'),
                bsnm_bddpr_nm=data.get('bsnmBddprNm'),
                bddpr_corp_no=data.get('bddprCorpNo'),
                prdprc=self._parse_int(data.get('prdprc')),
                basis_prce=self._parse_int(data.get('basisPrce')),
                presmpt_prce=self._parse_int(data.get('presmptPrce')),
                sucsfbid_amt=self._parse_int(data.get('sucsfbidAmt')),
                prdprc_rate=self._parse_float(data.get('prdprcRate')),
                sucsfbid_rate=self._parse_float(data.get('sucsfbidRate')),
                sucsfbid_lwltrate=self._parse_float(data.get('sucsfbidLwltrate')),
                bidder_count=self._parse_int(data.get('bidderCount')),
                opengdt=self._parse_datetime(data.get('opengDt')),
                rgn_nm=data.get('rgnNm'),
                induty_ty_nm=data.get('indutyTyNm'),
                instt_nm=data.get('insttNm'),
                dminstt_nm=data.get('dminsttNm'),
                bid_methd_nm=data.get('bidMethdNm')
            )
            
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            # 입찰공고 상태 업데이트
            if announcement:
                announcement.bid_status = 'opened'
                self.db.commit()
            
            logger.info(f"낙찰결과 저장 완료: {bid_ntce_no}")
            return result
            
        except Exception as e:
            logger.error(f"낙찰결과 저장 실패: {e}")
            self.db.rollback()
            return None
    
    def _create_announcement_from_result(self, data: Dict) -> Optional[BidAnnouncement]:
        """
        낙찰결과 데이터에서 입찰공고 역으로 생성
        """
        try:
            announcement = BidAnnouncement(
                bid_ntce_no=data.get('bidNtceNo'),
                bid_ntce_ord=data.get('bidNtceOrd'),
                bid_ntce_nm=data.get('bidNtceNm', ''),
                instt_nm=data.get('insttNm'),
                dminstt_nm=data.get('dminsttNm'),
                basis_prce=self._parse_int(data.get('basisPrce')),
                presmpt_prce=self._parse_int(data.get('presmptPrce')),
                opengdt=self._parse_datetime(data.get('opengDt')),
                rgn_nm=data.get('rgnNm'),
                induty_ty_nm=data.get('indutyTyNm'),
                bid_methd_nm=data.get('bidMethdNm'),
                bid_status='opened'
            )
            
            self.db.add(announcement)
            self.db.commit()
            self.db.refresh(announcement)
            
            return announcement
            
        except Exception as e:
            logger.error(f"입찰공고 역생성 실패: {e}")
            self.db.rollback()
            return None
    
    def _determine_bid_status(self, data: Dict) -> str:
        """
        입찰 상태 판단
        """
        opengdt = self._parse_datetime(data.get('opengDt'))
        if opengdt and opengdt < datetime.now():
            return 'opened'
        return 'announced'
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """문자열을 정수로 안전하게 변환"""
        if value is None or value == '':
            return None
        try:
            return int(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return None
    
    def _parse_float(self, value: Any) -> Optional[float]:
        """문자열을 실수로 안전하게 변환"""
        if value is None or value == '':
            return None
        try:
            return float(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return None
    
    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        """문자열을 datetime으로 안전하게 변환"""
        if not value:
            return None
        try:
            # YYYYMMDD 또는 YYYYMMDDHHmmss 형식 처리
            value_str = str(value).strip()
            if len(value_str) == 8:  # YYYYMMDD
                return datetime.strptime(value_str, "%Y%m%d")
            elif len(value_str) == 14:  # YYYYMMDDHHmmss
                return datetime.strptime(value_str, "%Y%m%d%H%M%S")
            else:
                return None
        except (ValueError, TypeError):
            return None
