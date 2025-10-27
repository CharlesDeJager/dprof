#!/usr/bin/env python3

import asyncio
import json
from app.exporters.profile_exporter import ProfileExporter

# Sample profile data to test the enhanced HTML export
sample_profile_data = {
    "employees": {
        "total_rows": 5,
        "columns": {
            "id": {
                "data_type": "INTEGER",
                "non_null_count": 5,
                "null_count": 0,
                "null_percentage": 0.0,
                "unique_count": 5,
                "min_value": 1,
                "max_value": 5,
                "mean": 3.0,
                "std_dev": 1.58
            },
            "name": {
                "data_type": "VARCHAR",
                "non_null_count": 5,
                "null_count": 0,
                "null_percentage": 0.0,
                "unique_count": 5,
                "min_length": 8,
                "max_length": 13,
                "avg_length": 10.4,
                "empty_count": 0
            },
            "age": {
                "data_type": "INTEGER", 
                "non_null_count": 4,
                "null_count": 1,
                "null_percentage": 20.0,
                "unique_count": 4,
                "min_value": 28,
                "max_value": 42,
                "mean": 34.0,
                "std_dev": 5.83
            },
            "salary": {
                "data_type": "FLOAT",
                "non_null_count": 4,
                "null_count": 1,
                "null_percentage": 20.0,
                "unique_count": 4,
                "min_value": 65000.75,
                "max_value": 95000.25,
                "mean": 80250.38,
                "std_dev": 12567.43
            },
            "department": {
                "data_type": "VARCHAR",
                "non_null_count": 4,
                "null_count": 1,
                "null_percentage": 20.0,
                "unique_count": 3,
                "min_length": 5,
                "max_length": 11,
                "avg_length": 8.75,
                "empty_count": 0
            },
            "email": {
                "data_type": "VARCHAR",
                "non_null_count": 4,
                "null_count": 0,
                "null_percentage": 0.0,
                "unique_count": 4,
                "min_length": 0,
                "max_length": 25,
                "avg_length": 20.0,
                "empty_count": 1
            },
            "is_active": {
                "data_type": "BOOLEAN",
                "non_null_count": 5,
                "null_count": 0,
                "null_percentage": 0.0,
                "unique_count": 2,
                "min_value": False,
                "max_value": True
            }
        }
    },
    "departments": {
        "total_rows": 3,
        "columns": {
            "dept_id": {
                "data_type": "INTEGER",
                "non_null_count": 3,
                "null_count": 0,
                "null_percentage": 0.0,
                "unique_count": 3,
                "min_value": 1,
                "max_value": 3,
                "mean": 2.0,
                "std_dev": 1.0
            },
            "dept_name": {
                "data_type": "VARCHAR",
                "non_null_count": 3,
                "null_count": 0,
                "null_percentage": 0.0,
                "unique_count": 3,
                "min_length": 5,
                "max_length": 11,
                "avg_length": 8.33,
                "empty_count": 0
            }
        }
    }
}

async def test_html_export():
    """Test the enhanced HTML export functionality"""
    print("🧪 Testing Enhanced HTML Export...")
    
    exporter = ProfileExporter()
    
    try:
        # Generate HTML export
        html_content, filename = await exporter.export_to_html(sample_profile_data)
        
        # Save to file for testing
        output_path = f"/Users/charlesdejager/dev/dprof/backend/exports/{filename}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML export successful!")
        print(f"📄 File saved as: {output_path}")
        print(f"🔗 Open in browser: file://{output_path}")
        print(f"📊 Generated {len(html_content):,} characters of HTML content")
        
        # Print some stats about the content
        import re
        table_sections = len(re.findall(r'class="table-section"', html_content))
        column_cards = len(re.findall(r'class="column-card"', html_content))
        quality_scores = len(re.findall(r'class="quality-score"', html_content))
        
        print(f"📋 Contains {table_sections} table sections")
        print(f"🔍 Contains {column_cards} column detail cards")
        print(f"📈 Contains {quality_scores} data quality visualizations")
        
    except Exception as e:
        print(f"❌ HTML export failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_html_export())