"""
Excel Parser Service
Parses bid simulation Excel files uploaded by users.
Updated to handle real bid file format.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import re


class ExcelParser:
    """
    Parse bid simulation Excel files to extract:
    1. Basic metadata (발주처, 공사명, 추정가격, 예가범위)
    2. Participant company information (업체명, 환산점수, 투찰범위)
    3. Simulation matrix (예가율별 업체별 투찰 금액)
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.metadata = {}
        self.companies = []
        self.company_columns = []  # Store column indices
        self.simulation_matrix = None
        
    def parse(self) -> Dict[str, Any]:
        """
        Main parsing method.
        Returns a dictionary containing all extracted data.
        """
        try:
            # Read Excel file - try multiple engines
            try:
                # Try openpyxl first (for .xlsx)
                self.df = pd.read_excel(self.file_path, sheet_name=0, engine='openpyxl', header=None)
            except:
                try:
                    # Try xlrd (for .xls)
                    self.df = pd.read_excel(self.file_path, sheet_name=0, engine='xlrd', header=None)
                except:
                    # Fallback to default
                    self.df = pd.read_excel(self.file_path, sheet_name=0, header=None)
            
            # Extract different sections
            self.extract_metadata()
            self.extract_companies()
            self.extract_simulation_matrix()
            
            return {
                "success": True,
                "metadata": self.metadata,
                "companies": self.companies,
                "simulation_matrix": self.simulation_matrix,
                "summary": {
                    "total_companies": len(self.companies),
                    "price_range": self.metadata.get("price_range", {}),
                    "estimated_price": self.metadata.get("estimated_price", 0),
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {},
                "companies": [],
                "simulation_matrix": None
            }
    
    def extract_metadata(self):
        """
        Extract basic metadata from the Excel file.
        Real format:
        Row 1: 건명 (col 0) | ... | 공사명 (col 2) | ... | 기초금액 (col 9) | value (col 10)
        Row 2: 발주처 (col 0) | ... | 발주처명 (col 2) | ... | 추정가격 (col 9) | value (col 10)
        """
        metadata = {}
        
        # Row 1: 건명 and 기초금액
        if len(self.df) > 1:
            row1 = self.df.iloc[1]
            # 건명 (Project Name) at column 2
            if pd.notna(row1.iloc[2]):
                project_name = str(row1.iloc[2]).strip()
                if len(project_name) > 3:
                    metadata['project_name'] = project_name
            
            # 기초금액 at column 10
            if len(row1) > 10 and pd.notna(row1.iloc[10]):
                try:
                    base_price = float(row1.iloc[10])
                    if base_price > 100000:
                        metadata['base_price'] = base_price
                except:
                    pass
        
        # Row 2: 발주처 and 추정가격
        if len(self.df) > 2:
            row2 = self.df.iloc[2]
            # 발주처 (Ordering Agency) at column 2
            if pd.notna(row2.iloc[2]):
                ordering_agency = str(row2.iloc[2]).strip()
                if len(ordering_agency) > 1:
                    metadata['ordering_agency'] = ordering_agency
            
            # 추정가격 at column 10
            if len(row2) > 10 and pd.notna(row2.iloc[10]):
                try:
                    estimated_price = float(row2.iloc[10])
                    if estimated_price > 100000:
                        metadata['estimated_price'] = estimated_price
                except:
                    pass
            
            # 예가범위 at column 12
            if len(row2) > 12 and pd.notna(row2.iloc[12]):
                range_str = str(row2.iloc[12])
                if '~' in range_str or '～' in range_str:
                    # Parse "97% ~ 103%"
                    percentages = re.findall(r'(\d+\.?\d*)%', range_str)
                    if len(percentages) >= 2:
                        try:
                            metadata['price_range'] = {
                                'min': float(percentages[0]),
                                'max': float(percentages[1])
                            }
                        except:
                            pass
        
        # Default values if not found
        metadata.setdefault('ordering_agency', 'Unknown')
        metadata.setdefault('project_name', 'Unknown Project')
        metadata.setdefault('estimated_price', 0)
        metadata.setdefault('price_range', {'min': 97.0, 'max': 103.0})
        
        self.metadata = metadata
    
    def extract_companies(self):
        """
        Extract participating company information.
        Real format:
        Row 4: 항만부 (col 0) | ... | 1.업체1 (col 4) | 2.업체2 (col 5) | 3.업체3 (col 6) | ...
        Row 9: 환산점수 합계 | ... | 점수1 (col 4) | 점수2 (col 5) | 점수3 (col 6) | ...
        Row 10-11: 투찰범위 하한선/상한선
        """
        companies = []
        company_columns = []  # Store column indices where companies are found
        
        # Row 4 contains company names starting from column 4
        company_row_idx = None
        score_row_idx = None
        lower_bound_row_idx = None
        upper_bound_row_idx = None
        
        # Find specific rows
        for idx in range(min(15, len(self.df))):
            row = self.df.iloc[idx]
            first_cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
            
            # Row 4: 항만부/토목부 + company names
            if '항만부' in first_cell or '토목부' in first_cell or '건축부' in first_cell:
                company_row_idx = idx
            
            # Row 9: 환산점수 합계
            if '환산점수' in first_cell and '합계' in first_cell:
                score_row_idx = idx
            
            # Row 10: 투찰범위 - 하한선
            if '투' in first_cell and '찰' in first_cell and '범' in first_cell:
                # Next row should be 하한선
                if idx + 1 < len(self.df):
                    next_cell = str(self.df.iloc[idx + 1, 0]) if pd.notna(self.df.iloc[idx + 1, 0]) else ""
                    if '하한' in next_cell:
                        lower_bound_row_idx = idx + 1
                        upper_bound_row_idx = idx + 2
        
        # Extract company data starting from column 4
        if company_row_idx is not None and len(self.df) > company_row_idx:
            company_row = self.df.iloc[company_row_idx]
            
            # Companies start from column 4 - scan all columns
            for col_idx in range(4, len(company_row)):
                cell = company_row.iloc[col_idx]
                if pd.notna(cell):
                    company_name = str(cell).strip()
                    # Valid company name: at least 2 chars, starts with number or contains company identifier
                    if len(company_name) >= 2:
                        # Skip non-company cells
                        if company_name.replace('.', '').replace('-', '').replace('%', '').replace('(', '').replace(')', '').isdigit():
                            continue
                        # Skip header/label cells
                        skip_keywords = ['점수', '합계', '투찰', '범위', '신인도', '순위', '등급', '평가', '지명업체']
                        if any(keyword in company_name for keyword in skip_keywords):
                            continue
                        # Only include if starts with a number (e.g., "1.", "2.", etc.)
                        if not company_name[0].isdigit():
                            continue
                        
                        company_info = {
                            'name': company_name,
                            'column_index': col_idx  # Store column index for simulation matrix
                        }
                        
                        # Extract score
                        if score_row_idx is not None and col_idx < len(self.df.iloc[score_row_idx]):
                            score = self.df.iloc[score_row_idx, col_idx]
                            if pd.notna(score):
                                try:
                                    company_info['total_score'] = float(score)
                                except:
                                    pass
                        
                        # Extract lower bound
                        if lower_bound_row_idx is not None and col_idx < len(self.df.iloc[lower_bound_row_idx]):
                            lower = self.df.iloc[lower_bound_row_idx, col_idx]
                            if pd.notna(lower):
                                try:
                                    company_info['bid_lower_limit'] = float(lower)
                                except:
                                    pass
                        
                        # Extract upper bound
                        if upper_bound_row_idx is not None and col_idx < len(self.df.iloc[upper_bound_row_idx]):
                            upper = self.df.iloc[upper_bound_row_idx, col_idx]
                            if pd.notna(upper):
                                try:
                                    company_info['bid_upper_limit'] = float(upper)
                                except:
                                    pass
                        
                        # Only add if it has at least a score
                        if 'total_score' in company_info:
                            companies.append(company_info)
                            company_columns.append(col_idx)
        
        self.companies = companies
        self.company_columns = company_columns  # Store for use in simulation matrix
    
    def extract_simulation_matrix(self):
        """
        Extract the simulation matrix showing bid amounts for each company
        at different expected price rates.
        
        Real format:
        Row 16: 예가율(%) (col 0) | 예정가격 (col 2) | 투찰범위 (col 4+)
        Row 17+: 103 | 696609600 | company1_bid | company2_bid | ...
        """
        matrix_data = []
        
        # Find simulation matrix header row
        matrix_start_row = None
        for idx in range(len(self.df)):
            row = self.df.iloc[idx]
            first_cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
            
            if '예가율' in first_cell:
                matrix_start_row = idx + 1  # Data starts next row
                break
        
        if matrix_start_row is None:
            self.simulation_matrix = []
            return
        
        # Get company info with column indices
        company_info_list = [(c['name'], c['column_index']) for c in self.companies if 'total_score' in c and 'column_index' in c]
        
        # Extract matrix data
        for idx in range(matrix_start_row, len(self.df)):
            row = self.df.iloc[idx]
            
            # Column 0: rate (percentage)
            rate_cell = row.iloc[0]
            if pd.isna(rate_cell):
                break
            
            rate = self._parse_percentage(str(rate_cell))
            if rate is None or rate < 95 or rate > 105:
                break
            
            # Column 2: predicted price
            predicted_price = 0
            if len(row) > 2 and pd.notna(row.iloc[2]):
                try:
                    predicted_price = int(float(row.iloc[2]))
                except:
                    pass
            
            # If no predicted price in excel, calculate it
            if predicted_price == 0:
                estimated_price = self.metadata.get('estimated_price', 0)
                if estimated_price > 0 and rate:
                    predicted_price = int(estimated_price * rate / 100)
            
            # Build row data
            row_data = {
                'rate': rate,
                'predicted_price': predicted_price,
                'companies': {}
            }
            
            # Extract company bids using stored column indices
            for company_name, col_idx in company_info_list:
                if col_idx < len(row) and pd.notna(row.iloc[col_idx]):
                    try:
                        bid_amount = int(float(row.iloc[col_idx]))
                        if bid_amount > 0:
                            row_data['companies'][company_name] = bid_amount
                    except:
                        pass
            
            if len(row_data['companies']) > 0:
                matrix_data.append(row_data)
        
        self.simulation_matrix = matrix_data
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float."""
        try:
            # Remove common formatting
            price_str = str(price_str).replace(',', '').replace('원', '').replace('₩', '')
            price_str = price_str.replace(' ', '').strip()
            
            # Extract numeric value
            match = re.search(r'[\d.]+', price_str)
            if match:
                return float(match.group())
            return 0.0
        except:
            return 0.0
    
    def _parse_percentage(self, percent_str: str) -> Optional[float]:
        """Parse percentage string to float."""
        try:
            percent_str = str(percent_str).replace('%', '').replace(' ', '').strip()
            match = re.search(r'[\d.]+', percent_str)
            if match:
                return float(match.group())
            return None
        except:
            return None


def parse_excel_file(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse an Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary containing parsed data
    """
    parser = ExcelParser(file_path)
    return parser.parse()
