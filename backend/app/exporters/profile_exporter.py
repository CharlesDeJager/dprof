import pandas as pd
import json
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
import xlsxwriter
from io import BytesIO
from jinja2 import Template

class ProfileExporter:
    """
    Handles exporting profiling results to various formats (XLSX, JSON, HTML)
    """
    
    def __init__(self):
        self.export_templates = {
            'html': self._get_html_template()
        }
    
    async def export_to_xlsx(self, profile_data: Dict[str, Any]) -> Tuple[bytes, str]:
        """
        Export profiling results to Excel format
        """
        filename = f"data_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Create Excel file in memory
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'text_wrap': True
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00'
        })
        
        percentage_format = workbook.add_format({
            'border': 1,
            'num_format': '0.00%'
        })
        
        # Create summary sheet
        summary_sheet = workbook.add_worksheet('Summary')
        self._write_summary_sheet(summary_sheet, profile_data, header_format, cell_format)
        
        # Create detailed sheets for each table
        for table_name, table_data in profile_data.items():
            if 'error' in table_data:
                continue
                
            # Clean sheet name (Excel has restrictions)
            sheet_name = self._clean_sheet_name(table_name)
            detail_sheet = workbook.add_worksheet(sheet_name)
            
            self._write_detail_sheet(
                detail_sheet, table_data, 
                header_format, cell_format, number_format, percentage_format
            )
        
        workbook.close()
        output.seek(0)
        
        return output.getvalue(), filename
    
    async def export_to_json(self, profile_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Export profiling results to JSON format
        """
        filename = f"data_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Create export structure
        export_data = {
            'export_metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_tables': len(profile_data),
                'export_format': 'json',
                'version': '1.0'
            },
            'tables': profile_data
        }
        
        json_content = json.dumps(export_data, indent=2, default=str)
        
        return json_content, filename
    
    async def export_to_html(self, profile_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Export profiling results to clean, navigable HTML format
        """
        filename = f"data_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Simple HTML export to identify the issue
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Profile Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .table {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ccc; }}
                .column {{ margin: 10px 0; padding: 10px; background: #f5f5f5; }}
            </style>
        </head>
        <body>
            <h1>Data Profile Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total Tables: {len(profile_data)}</p>
        """
        
        for table_name, table_data in profile_data.items():
            if 'error' in table_data:
                html_content += f"""
                <div class="table">
                    <h2>{table_name}</h2>
                    <p style="color: red;">Error: {table_data['error']}</p>
                </div>
                """
            else:
                html_content += f"""
                <div class="table">
                    <h2>{table_name}</h2>
                    <p>Records: {table_data.get('total_records', 'N/A')}</p>
                    <p>Columns: {table_data.get('total_columns', 'N/A')}</p>
                </div>
                """
        
        html_content += """
        </body>
        </html>
        """
        
        return html_content, filename
    
    def _write_summary_sheet(self, worksheet, profile_data, header_format, cell_format):
        """
        Write summary information to Excel sheet
        """
        # Headers
        headers = ['Table Name', 'Total Records', 'Total Columns', 'Profiled At', 'Status']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        row = 1
        for table_name, table_data in profile_data.items():
            if 'error' in table_data:
                worksheet.write(row, 0, table_name, cell_format)
                worksheet.write(row, 1, 'N/A', cell_format)
                worksheet.write(row, 2, 'N/A', cell_format)
                worksheet.write(row, 3, 'N/A', cell_format)
                worksheet.write(row, 4, f"Error: {table_data['error']}", cell_format)
            else:
                worksheet.write(row, 0, table_name, cell_format)
                worksheet.write(row, 1, table_data.get('total_records', 0), cell_format)
                worksheet.write(row, 2, table_data.get('total_columns', 0), cell_format)
                worksheet.write(row, 3, table_data.get('profiled_at', ''), cell_format)
                worksheet.write(row, 4, 'Success', cell_format)
            row += 1
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 2, 12)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 15)
    
    def _write_detail_sheet(self, worksheet, table_data, header_format, cell_format, number_format, percentage_format):
        """
        Write detailed column information to Excel sheet
        """
        # Headers
        headers = [
            'Column Name', 'Data Type', 'Total Values', 'Null Count', 'Null %',
            'Blank Count', 'Blank %', 'Distinct Count', 'Distinct %',
            'Quality Score', 'Completeness', 'Min Value', 'Max Value', 'Average'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        row = 1
        columns_data = table_data.get('columns', {})
        
        for col_name, col_data in columns_data.items():
            if 'error' in col_data:
                worksheet.write(row, 0, col_name, cell_format)
                worksheet.write(row, 1, f"Error: {col_data['error']}", cell_format)
                row += 1
                continue
            
            worksheet.write(row, 0, col_name, cell_format)
            worksheet.write(row, 1, col_data.get('data_type', ''), cell_format)
            worksheet.write(row, 2, col_data.get('total_values', 0), cell_format)
            worksheet.write(row, 3, col_data.get('null_count', 0), cell_format)
            worksheet.write(row, 4, col_data.get('null_percentage', 0) / 100, percentage_format)
            worksheet.write(row, 5, col_data.get('blank_count', 0), cell_format)
            worksheet.write(row, 6, col_data.get('blank_percentage', 0) / 100, percentage_format)
            worksheet.write(row, 7, col_data.get('distinct_count', 0), cell_format)
            worksheet.write(row, 8, col_data.get('distinct_percentage', 0) / 100, percentage_format)
            worksheet.write(row, 9, col_data.get('data_quality_score', 0), number_format)
            worksheet.write(row, 10, col_data.get('completeness', 0) / 100, percentage_format)
            worksheet.write(row, 11, col_data.get('min_value', ''), cell_format)
            worksheet.write(row, 12, col_data.get('max_value', ''), cell_format)
            worksheet.write(row, 13, col_data.get('average', ''), number_format)
            
            row += 1
        
        # Auto-adjust column widths
        for col in range(len(headers)):
            worksheet.set_column(col, col, 12)
    
    def _clean_sheet_name(self, name: str) -> str:
        """
        Clean sheet name for Excel compatibility
        """
        # Remove invalid characters
        invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
        clean_name = name
        
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '_')
        
        # Limit length (Excel sheet names max 31 chars)
        if len(clean_name) > 31:
            clean_name = clean_name[:28] + '...'
        
        return clean_name
    
    def _get_html_template(self) -> str:
        """
        Return HTML template for data profiling report
        """
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Profile Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .meta {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .summary-card h3 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 5px;
        }
        
        .summary-card p {
            color: #666;
            font-size: 0.9em;
        }
        
        .table-section {
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .table-header {
            background: #667eea;
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .table-header:hover {
            background: #5a6fd8;
        }
        
        .table-header h2 {
            font-size: 1.3em;
        }
        
        .table-stats {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .table-content {
            padding: 0;
            display: none;
        }
        
        .table-content.active {
            display: block;
        }
        
        .columns-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        
        .column-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .column-header {
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .column-name {
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
        }
        
        .column-type {
            color: #667eea;
            font-size: 0.9em;
            margin-top: 2px;
        }
        
        .column-body {
            padding: 15px;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding-bottom: 5px;
            border-bottom: 1px dotted #e0e0e0;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .stat-value {
            font-weight: bold;
            color: #333;
        }
        
        .quality-score {
            background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #0abde3, #10ac84);
            height: 8px;
            border-radius: 4px;
            margin: 10px 0;
            position: relative;
        }
        
        .quality-indicator {
            position: absolute;
            top: -2px;
            width: 12px;
            height: 12px;
            background: #333;
            border-radius: 50%;
        }
        
        .patterns-section, .common-values-section {
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
        }
        
        .section-title {
            font-size: 0.9em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }
        
        .pattern-item, .value-item {
            background: #f8f9fa;
            padding: 5px 8px;
            border-radius: 4px;
            margin-bottom: 5px;
            font-size: 0.8em;
        }
        
        .pattern-count, .value-count {
            color: #667eea;
            font-weight: bold;
        }
        
        .issues-list {
            margin-top: 10px;
        }
        
        .issue-item {
            background: #ffe6e6;
            color: #d73035;
            padding: 5px 10px;
            border-radius: 4px;
            margin-bottom: 5px;
            font-size: 0.8em;
        }
        
        .toggle-icon {
            transition: transform 0.3s;
        }
        
        .toggle-icon.rotated {
            transform: rotate(180deg);
        }
        
        @media (max-width: 768px) {
            .columns-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Data Profile Report</h1>
            <div class="meta">
                Generated on {{ export_date }} • {{ total_tables }} table(s) analyzed
            </div>
        </div>
        
        <div class="summary-cards">
            <div class="summary-card">
                <h3>{{ total_tables }}</h3>
                <p>Total Tables</p>
            </div>
            <div class="summary-card">
                <h3>{{ tables|selectattr('total_records')|map(attribute='total_records')|sum }}</h3>
                <p>Total Records</p>
            </div>
            <div class="summary-card">
                <h3>{{ tables|selectattr('total_columns')|map(attribute='total_columns')|sum }}</h3>
                <p>Total Columns</p>
            </div>
        </div>
        
        {% for table in tables %}
        <div class="table-section">
            <div class="table-header" onclick="toggleTable('table-{{ loop.index }}')">
                <div>
                    <h2>{{ table.name }}</h2>
                    {% if table.error %}
                        <div style="color: #ffcccb; font-size: 0.9em;">Error: {{ table.error }}</div>
                    {% endif %}
                </div>
                <div class="table-stats">
                    {% if not table.error %}
                        {{ table.total_records }} records • {{ table.total_columns }} columns
                    {% endif %}
                    <span class="toggle-icon" id="icon-table-{{ loop.index }}">▼</span>
                </div>
            </div>
            
            {% if not table.error %}
            <div class="table-content" id="table-{{ loop.index }}">
                <div class="columns-grid">
                    {% for column in table.columns %}
                    <div class="column-card">
                        <div class="column-header">
                            <div class="column-name">{{ column.name }}</div>
                            <div class="column-type">{{ column.data_type }}</div>
                        </div>
                        <div class="column-body">
                            <div class="stat-row">
                                <span class="stat-label">Completeness</span>
                                <span class="stat-value">{{ "%.1f"|format(column.completeness) }}%</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Uniqueness</span>
                                <span class="stat-value">{{ "%.1f"|format(column.uniqueness) }}%</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Nulls</span>
                                <span class="stat-value">{{ column.null_count }} ({{ "%.1f"|format(column.null_percentage) }}%)</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Blanks</span>
                                <span class="stat-value">{{ column.blank_count }} ({{ "%.1f"|format(column.blank_percentage) }}%)</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Distinct Values</span>
                                <span class="stat-value">{{ column.distinct_count }} ({{ "%.1f"|format(column.distinct_percentage) }}%)</span>
                            </div>
                            
                            <div class="stat-row">
                                <span class="stat-label">Quality Score</span>
                                <span class="stat-value">{{ "%.1f"|format(column.quality_score) }}/100</span>
                            </div>
                            <div class="quality-score">
                                <div class="quality-indicator" style="left: {{ column.quality_score }}%;"></div>
                            </div>
                            
                            {% if column.min_value is not none %}
                            <div class="stat-row">
                                <span class="stat-label">Min / Max</span>
                                <span class="stat-value">{{ column.min_value }} / {{ column.max_value }}</span>
                            </div>
                            {% if column.average is not none %}
                            <div class="stat-row">
                                <span class="stat-label">Average</span>
                                <span class="stat-value">{{ "%.2f"|format(column.average) }}</span>
                            </div>
                            {% endif %}
                            {% endif %}
                            
                            {% if column.avg_length is not none %}
                            <div class="stat-row">
                                <span class="stat-label">Avg Length</span>
                                <span class="stat-value">{{ "%.1f"|format(column.avg_length) }} chars</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Length Range</span>
                                <span class="stat-value">{{ column.min_length }} - {{ column.max_length }}</span>
                            </div>
                            {% endif %}
                            
                            {% if column.patterns %}
                            <div class="patterns-section">
                                <div class="section-title">Top Patterns</div>
                                {% for pattern in column.patterns[:3] %}
                                <div class="pattern-item">
                                    <strong>{{ pattern.pattern }}</strong> 
                                    <span class="pattern-count">({{ pattern.count }} occurrences)</span>
                                </div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            {% if column.common_values %}
                            <div class="common-values-section">
                                <div class="section-title">Most Common Values</div>
                                {% for value in column.common_values[:3] %}
                                <div class="value-item">
                                    <strong>{{ value.value }}</strong> 
                                    <span class="value-count">({{ value.count }}x)</span>
                                </div>
                                {% endfor %}
                            </div>
                            {% endif %}
                            
                            {% if column.potential_issues %}
                            <div class="issues-list">
                                {% for issue in column.potential_issues %}
                                <div class="issue-item">⚠️ {{ issue }}</div>
                                {% endfor %}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    <script>
        function toggleTable(tableId) {
            const content = document.getElementById(tableId);
            const icon = document.getElementById('icon-' + tableId);
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                icon.classList.remove('rotated');
            } else {
                content.classList.add('active');
                icon.classList.add('rotated');
            }
        }
        
        // Show first table by default
        if (document.querySelector('.table-content')) {
            document.querySelector('.table-content').classList.add('active');
            document.querySelector('.toggle-icon').classList.add('rotated');
        }
    </script>
</body>
</html>
        '''