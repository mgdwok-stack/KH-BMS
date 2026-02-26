"""
Excel Parser Service
Parses bid simulation Excel files uploaded by users.
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
        self.simulation_matrix = None
        
    def parse(self) -> Dict[str, Any]:
        """
        Main parsing method.
        Returns a dictionary containing all extracted data.
        """
        try:
            # Read Excel file
            self.df = pd.read_excel(self.file_path, sheet_name=0)
            
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
        Expected format:
        - 발주처: [value]
        - 공사명: [value]
        - 추정가격: [value]
        - 예가범위: 97% ~ 103%
        """
        metadata = {}
        
        # Try to find metadata in first few rows
        for idx in range(min(20, len(self.df))):
            row = self.df.iloc[idx]
            row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
            
            # 발주처 (Ordering Agency)
            if '발주처' in row_str or '발주기관' in row_str:
                metadata['ordering_agency'] = self._extract_value_after_keyword(row_str, ['발주처', '발주기관'])
            
            # 공사명 (Project Name)
            if '공사명' in row_str or '사업명' in row_str:
                metadata['project_name'] = self._extract_value_after_keyword(row_str, ['공사명', '사업명'])
            
            # 추정가격 (Estimated Price)
            if '추정가격' in row_str or '기초금액' in row_str:
                price_str = self._extract_value_after_keyword(row_str, ['추정가격', '기초금액'])
                metadata['estimated_price'] = self._parse_price(price_str)
            
            # 예가범위 (Price Range)
            if '예가범위' in row_str or '예정가격범위' in row_str:
                range_str = self._extract_value_after_keyword(row_str, ['예가범위', '예정가격범위'])
                metadata['price_range'] = self._parse_price_range(range_str)
        
        # Default values if not found
        metadata.setdefault('ordering_agency', 'Unknown')
        metadata.setdefault('project_name', 'Unknown Project')
        metadata.setdefault('estimated_price', 0)
        metadata.setdefault('price_range', {'min': 97.0, 'max': 103.0})
        
        self.metadata = metadata
    
    def extract_companies(self):
        """
        Extract participating company information.
        Expected format in rows:
        순번 | 업체명 | 환산점수 합계 | 투찰가능 상한 | 투찰가능 하한
        """
        companies = []
        
        # Find the row that contains company headers
        company_header_row = None
        for idx in range(len(self.df)):
            row = self.df.iloc[idx]
            row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
            
            if '업체' in row_str and ('환산점수' in row_str or '합계' in row_str):
                company_header_row = idx
                break
        
        if company_header_row is not None:
            # Parse company data starting from the next row
            for idx in range(company_header_row + 1, len(self.df)):
                row = self.df.iloc[idx]
                
                # Stop if we hit an empty row or next section
                if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                    break
                
                # Check if this looks like a company row (starts with number or company name)
                first_cell = str(row.iloc[0]).strip()
                if first_cell and (first_cell.isdigit() or len(first_cell) > 2):
                    company_info = self._parse_company_row(row)
                    if company_info:
                        companies.append(company_info)
        
        self.companies = companies
    
    def extract_simulation_matrix(self):
        """
        Extract the simulation matrix showing bid amounts for each company
        at different expected price rates.
        
        Expected format:
        예가율 | 예정가격 | 업체1 | 업체2 | ... | 업체N
        97.0%  | XXX     | YYY   | ZZZ   | ... | AAA
        97.1%  | XXX     | YYY   | ZZZ   | ... | AAA
        ...
        """
        matrix_data = []
        
        # Find the row that contains simulation matrix headers
        matrix_header_row = None
        for idx in range(len(self.df)):
            row = self.df.iloc[idx]
            row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
            
            if '예가율' in row_str and '예정가격' in row_str:
                matrix_header_row = idx
                break
        
        if matrix_header_row is not None:
            # Get headers
            headers = []
            header_row = self.df.iloc[matrix_header_row]
            for cell in header_row:
                if pd.notna(cell):
                    headers.append(str(cell).strip())
            
            # Parse matrix data
            for idx in range(matrix_header_row + 1, len(self.df)):
                row = self.df.iloc[idx]
                
                # Stop if empty row
                if pd.isna(row.iloc[0]):
                    break
                
                # Parse row data
                row_data = {}
                first_cell = str(row.iloc[0]).strip()
                
                # Check if this is a valid data row (starts with percentage like 97.0%)
                if '%' in first_cell or self._is_percentage_value(first_cell):
                    rate = self._parse_percentage(first_cell)
                    if rate:
                        row_data['rate'] = rate
                        
                        # Extract predicted price and company bids
                        for col_idx, header in enumerate(headers):
                            if col_idx < len(row):
                                value = row.iloc[col_idx]
                                if pd.notna(value):
                                    if '예정가격' in header:
                                        row_data['predicted_price'] = self._parse_price(str(value))
                                    elif col_idx > 1:  # Company columns
                                        company_name = header
                                        bid_amount = self._parse_price(str(value))
                                        if 'companies' not in row_data:
                                            row_data['companies'] = {}
                                        row_data['companies'][company_name] = bid_amount
                        
                        matrix_data.append(row_data)
        
        self.simulation_matrix = matrix_data
    
    def _extract_value_after_keyword(self, text: str, keywords: List[str]) -> str:
        """Extract value after a keyword."""
        for keyword in keywords:
            if keyword in text:
                parts = text.split(keyword)
                if len(parts) > 1:
                    value = parts[1].strip()
                    # Remove common separators
                    value = value.lstrip(':：').strip()
                    # Take first part before any newline or tab
                    value = value.split()[0] if value.split() else ''
                    return value
        return ''
    
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
    
    def _parse_price_range(self, range_str: str) -> Dict[str, float]:
        """Parse price range string like '97% ~ 103%'."""
        try:
            # Extract percentages
            percentages = re.findall(r'[\d.]+', range_str)
            if len(percentages) >= 2:
                return {
                    'min': float(percentages[0]),
                    'max': float(percentages[1])
                }
            return {'min': 97.0, 'max': 103.0}
        except:
            return {'min': 97.0, 'max': 103.0}
    
    def _parse_company_row(self, row) -> Optional[Dict[str, Any]]:
        """Parse a company information row."""
        try:
            company_info = {}
            
            # Expected columns: 순번, 업체명, 환산점수 합계, 상한, 하한
            # Adjust indices based on actual file structure
            
            # Get company name (usually in column 1 or 2)
            for idx in range(min(3, len(row))):
                cell = str(row.iloc[idx]).strip()
                if cell and not cell.isdigit() and len(cell) > 1:
                    company_info['name'] = cell
                    break
            
            if 'name' not in company_info:
                return None
            
            # Try to extract score and bid range
            numeric_values = []
            for cell in row:
                if pd.notna(cell):
                    parsed = self._parse_price(str(cell))
                    if parsed > 0:
                        numeric_values.append(parsed)
            
            if len(numeric_values) >= 3:
                company_info['total_score'] = numeric_values[0]
                company_info['bid_upper_limit'] = numeric_values[1]
                company_info['bid_lower_limit'] = numeric_values[2]
            
            return company_info
        except:
            return None
    
    def _is_percentage_value(self, value: str) -> bool:
        """Check if a string looks like a percentage value."""
        try:
            # Check if it's a number between 95 and 105
            num = float(value)
            return 95.0 <= num <= 105.0
        except:
            return False


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
