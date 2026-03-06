"""
Generate sample Excel file for bid simulation
"""
import pandas as pd
import numpy as np
from pathlib import Path


def generate_sample_excel():
    """
    Generate a sample Excel file with bid simulation data.
    """
    
    # Create output directory
    output_dir = Path("/home/user/webapp/data/samples")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "bid_simulation_sample.xlsx"
    
    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # ============================================================================
        # Sheet 1: Basic Information
        # ============================================================================
        
        # Create metadata rows
        metadata = []
        metadata.append(['발주처', '경상남도'])
        metadata.append(['공사명', '진촌항 개발사업 실시설계용역'])
        metadata.append(['추정가격', '614,836,364'])
        metadata.append(['예가범위', '97% ~ 103%'])
        metadata.append([])  # Empty row
        
        # Company information header
        metadata.append(['순번', '업체명', '환산점수 합계', '투찰가능 상한', '투찰가능 하한'])
        
        # Sample companies (최대 20개)
        companies = [
            [1, '수성+세일', 92.5, 633401615, 596491474],
            [2, '삼안+혜인', 91.8, 632731458, 595892184],
            [3, '나우+서울', 90.2, 631155729, 594402365],
            [4, '한국해양+무영', 89.5, 630485573, 593763075],
            [5, '경림+시스포', 88.9, 629915416, 593223784],
            [6, '하천해양+대원', 88.2, 629245260, 592584494],
            [7, '유신+동양', 87.6, 628675103, 592045204],
            [8, '세종+명보', 87.0, 628104946, 591505914],
            [9, '동일+종합', 86.3, 627434789, 590866624],
            [10, '태영+미래', 85.7, 626864632, 590327333],
            [11, '부림+창조', 85.0, 626194476, 589688043],
            [12, '우리+새한', 84.4, 625624319, 589148753],
            [13, '광진+토목', 83.8, 625054162, 588609463],
            [14, '대한+종합', 83.1, 624384005, 587970172],
            [15, '중앙+엔지니어링', 82.5, 623813848, 587430882],
            [16, '한일+건설', 81.8, 623143692, 586791592],
            [17, '성지+기술공사', 81.2, 622573535, 586252302],
            [18, '평화+종합건설', 80.6, 622003378, 585713011],
            [19, '신한+엔지니어링', 79.9, 621333221, 585073721],
            [20, '동부+건설기술', 79.3, 620763065, 584534431]
        ]
        
        metadata.extend(companies)
        metadata.append([])  # Empty row
        
        # ============================================================================
        # Simulation Matrix Header
        # ============================================================================
        
        metadata.append(['예가율', '예정가격'] + [f'업체{i+1}' for i in range(20)])
        
        # Create DataFrame for metadata and save
        df_meta = pd.DataFrame(metadata)
        df_meta.to_excel(writer, sheet_name='입찰 시뮬레이션', index=False, header=False)
        
        # ============================================================================
        # Simulation Matrix Data
        # ============================================================================
        
        # Generate simulation data for rates from 97.0% to 103.0%
        estimated_price = 614_836_364
        simulation_data = []
        
        for rate_int in range(970, 1031):  # 97.0% to 103.0% in 0.1% steps
            rate = rate_int / 10.0
            predicted_price = estimated_price * (rate / 100.0)
            
            row = [f'{rate}%', f'{predicted_price:,.0f}']
            
            # Generate bid amounts for each company (20 companies)
            # Each company bids slightly differently based on their strategy
            for company_idx in range(20):
                # Companies bid between 99.5% ~ 99.9% of predicted price
                bid_rate = 0.995 + (company_idx * 0.0005) + np.random.uniform(-0.001, 0.001)
                bid_amount = predicted_price * bid_rate
                row.append(f'{bid_amount:,.0f}')
            
            simulation_data.append(row)
        
        # Append simulation data starting from the next row
        worksheet = writer.sheets['입찰 시뮬레이션']
        start_row = len(metadata) + 1
        
        for row_idx, row_data in enumerate(simulation_data):
            for col_idx, cell_value in enumerate(row_data):
                worksheet.cell(row=start_row + row_idx, column=col_idx + 1, value=cell_value)
    
    print(f"✅ Sample Excel file created: {output_file}")
    print(f"   - Estimated price: {estimated_price:,}원")
    print(f"   - Number of companies: 20")
    print(f"   - Simulation range: 97.0% ~ 103.0%")
    return str(output_file)


if __name__ == "__main__":
    generate_sample_excel()
