# DProf - Data Profiling Application

![DProf Logo](https://img.shields.io/badge/DProf-Data%20Profiling-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.2+-61dafb.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive data profiling application that analyzes data in files (CSV, JSON, XLSX) and database tables (Oracle, SQL Server) with parallel processing capabilities and rich visualizations.

## 🌟 Features

### Data Sources

- **📁 File Support**: CSV, JSON, XLSX, XLS files
- **🗃️ Database Support**: Oracle and SQL Server connections
- **🔄 Automatic Detection**: Smart detection of file structure and database schemas

### Profiling Capabilities

- **📊 Comprehensive Statistics**: For each column:
  - Data type detection and classification
  - Null and blank value counts and percentages
  - Distinct value counts and uniqueness percentage
  - Min, max, and average values for numeric fields
  - String length statistics and pattern analysis
  - Data quality scoring (0-100)

### Advanced Features

- **⚡ Parallel Processing**: Configurable multi-threading for fast processing
- **🎯 Smart Sampling**: Configurable record limits per table
- **🔍 Pattern Detection**: Automatic detection of string patterns
- **📈 Quality Scoring**: Automated data quality assessment
- **🚨 Issue Detection**: Identification of potential data problems

### Export Options

- **📄 Excel (XLSX)**: Detailed spreadsheets with formatted data
- **📝 JSON**: Machine-readable structured data
- **🌐 HTML**: Clean, interactive reports with navigation

### User Interface

- **🎨 Modern Web Interface**: React-based responsive design
- **📱 Mobile Friendly**: Works on desktop, tablet, and mobile
- **📊 Interactive Charts**: Visual representation of data quality
- **⏰ Real-time Progress**: Live progress tracking during analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/dprof.git
   cd dprof
   ```

2. **Set up the backend**

   ```bash
   cd backend
   python -m pip install -r requirements.txt
   cp .env.example .env  # Edit configuration if needed
   ```

3. **Set up the frontend**

   ```bash
   cd ../frontend
   npm install
   ```

4. **Start the application**

   Terminal 1 (Backend):

   ```bash
   cd backend
   python run_server.py
   ```

   Terminal 2 (Frontend):

   ```bash
   cd frontend
   npm start
   ```

5. **Access the application**
   - Open your browser to `http://localhost:3000`
   - API documentation available at `http://localhost:8000/docs`

## 📋 Usage Guide

### 1. Select Data Source

#### File Upload

1. Navigate to the **Files** tab
2. Drag and drop your file or click to browse
3. Supported formats: CSV, JSON, XLSX, XLS
4. The application will analyze the file structure automatically

#### Database Connection

1. Navigate to the **Database** tab
2. Select database type (Oracle or SQL Server)
3. Enter connection details:
   - Host and port
   - Database/service name
   - Username and password
4. Click "Connect to Database"

### 2. Configure Profiling

1. **Select Tables/Sheets**: Choose which data sources to profile
2. **Set Record Limits**: Specify how many records to analyze per table
3. **Review Selection**: Check the summary of records to be processed
4. Click "Start Profiling"

### 3. Monitor Progress

- **Real-time Updates**: Progress bar updates every 2 seconds
- **Time Estimation**: Estimated completion time based on current progress
- **Parallel Processing**: Multiple tables processed simultaneously

### 4. View Results

#### Summary Dashboard

- Overall statistics across all tables
- Quality score distribution charts
- Record and column counts

#### Detailed Analysis

- **Column-by-column breakdown** with:
  - Data types and quality scores
  - Completeness and uniqueness metrics
  - Statistical summaries (min, max, average)
  - String pattern analysis
  - Potential data issues

#### Interactive Features

- **Sortable columns**: Click headers to sort by different metrics
- **Pattern viewer**: Click "View Patterns" to see detailed string patterns
- **Quality visualization**: Progress bars and color coding for quick assessment

### 5. Export Results

Choose from three export formats:

- **📊 Excel**: Detailed spreadsheet with summary and data sheets
- **📋 JSON**: Structured data for programmatic use
- **🌐 HTML**: Interactive report for sharing and presentation

## ⚙️ Configuration

### Application Settings

Configure via the **Settings** tab or environment variables:

| Setting               | Default | Description                           |
| --------------------- | ------- | ------------------------------------- |
| `max_threads`         | 4       | Number of parallel processing threads |
| `default_max_records` | 10,000  | Default record limit per table        |
| `chunk_size`          | 1,000   | Records processed per chunk           |
| `max_file_size`       | 100MB   | Maximum upload file size              |

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Performance Settings
DPROF_MAX_THREADS=4
DPROF_DEFAULT_MAX_RECORDS=10000
DPROF_CHUNK_SIZE=1000

# File Settings
DPROF_MAX_FILE_SIZE=104857600
DPROF_TEMP_DIR=temp
DPROF_EXPORT_DIR=exports

# Database Settings (optional)
DPROF_ORACLE_CLIENT_PATH=/path/to/oracle/client
```

### Database Setup

#### Oracle Requirements

- Install Oracle Instant Client
- Set `ORACLE_HOME` environment variable (if needed)
- Ensure TNS configuration is accessible

#### SQL Server Requirements

- Install appropriate ODBC driver
- Common drivers: "ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server"

## 🏗️ Architecture

### Backend (Python/FastAPI)

```
backend/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── config.py          # Configuration management
│   ├── connectors/        # Data source connectors
│   │   ├── file_connector.py
│   │   └── database_connector.py
│   ├── profiler/          # Core profiling engine
│   │   └── data_profiler.py
│   └── exporters/         # Export functionality
│       └── profile_exporter.py
├── requirements.txt       # Python dependencies
└── run_server.py         # Server startup script
```

### Frontend (React)

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── DataSourceSelector.js
│   │   ├── TableSelector.js
│   │   ├── ProfilingProgress.js
│   │   └── ResultsDisplay.js
│   ├── services/          # API integration
│   │   └── api.js
│   ├── App.js            # Main application component
│   └── App.css           # Styling
└── package.json          # Node.js dependencies
```

## 📊 Profiling Details

### Column Analysis

For each column, DProf provides:

#### Basic Statistics

- **Total values**: Count of all values (including nulls)
- **Null count/percentage**: Missing or NULL values
- **Blank count/percentage**: Empty strings or whitespace-only values
- **Distinct count/percentage**: Unique values and diversity measure

#### Type-Specific Analysis

**Numeric Columns** (int, float):

- Min, max, average, median values
- Standard deviation
- Quartile distributions (25th, 75th percentiles)
- Zero, negative, and positive value counts

**String Columns**:

- Average, minimum, maximum string lengths
- Most common values with frequencies
- Pattern analysis with examples
- Character composition analysis

**Date/DateTime Columns**:

- Date range (min/max dates)
- Most common dates
- Time span calculations

**Boolean Columns**:

- True/false counts and percentages
- Distribution analysis

#### Data Quality Metrics

**Quality Score (0-100)**:

- Based on completeness, consistency, and validity
- Factors in null percentages, blank values, and data diversity
- Color-coded for quick assessment

**Completeness**:

- Percentage of non-null values
- Helps identify data gaps

**Uniqueness**:

- Percentage of distinct values
- Identifies potential key columns or redundant data

#### Issue Detection

Automatic identification of:

- High null percentages (>50%)
- High blank percentages (>20%)
- Low data diversity (<5% unique)
- Potential data type mismatches
- Suspicious patterns or outliers

### Pattern Analysis

For string columns, DProf automatically detects:

- **Format patterns**: Phone numbers, emails, IDs
- **Length patterns**: Fixed vs variable length fields
- **Character patterns**: Alphanumeric combinations
- **Common examples**: Representative values for each pattern

## 🔧 Development

### Running in Development Mode

Backend (with hot reload):

```bash
cd backend
python run_server.py
```

Frontend (with hot reload):

```bash
cd frontend
npm start
```

### API Documentation

FastAPI provides automatic API documentation:

- Interactive docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

### Building for Production

Frontend build:

```bash
cd frontend
npm run build
```

The built files will be in the `frontend/build` directory.

## 📈 Performance Tips

1. **Optimize Record Limits**: Start with smaller samples (1,000-10,000 records) for quick insights
2. **Adjust Thread Count**: Increase `max_threads` for faster processing on multi-core systems
3. **Use Chunking**: Smaller `chunk_size` for memory-constrained environments
4. **Database Indexing**: Ensure proper indexing on frequently analyzed tables
5. **Network Optimization**: Use database connections close to the data source

## 🐛 Troubleshooting

### Common Issues

**File Upload Fails**:

- Check file size limits (default 100MB)
- Ensure file format is supported
- Verify file permissions

**Database Connection Issues**:

- Verify network connectivity and credentials
- Check database server configuration
- Ensure required drivers are installed

**Memory Errors**:

- Reduce `max_records` setting
- Decrease `chunk_size` parameter
- Increase available system memory

**Slow Performance**:

- Reduce number of parallel threads
- Process fewer records per table
- Optimize database queries with proper indexing

### Error Codes

| Code | Description           | Solution                                    |
| ---- | --------------------- | ------------------------------------------- |
| 400  | Bad Request           | Check input parameters and file format      |
| 404  | Session Not Found     | Session may have expired, restart profiling |
| 500  | Internal Server Error | Check logs for detailed error information   |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Write descriptive commit messages
- Add tests for new features
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework for building APIs
- **React**: User interface library for building interactive UIs
- **Pandas**: Powerful data analysis and manipulation library
- **Ant Design**: Enterprise-class UI design language
- **Recharts**: Composable charting library for React

## 📞 Support

- **📧 Email**: support@dprof.com
- **🐛 Issues**: [GitHub Issues](https://github.com/yourusername/dprof/issues)
- **📖 Documentation**: [Full Documentation](https://docs.dprof.com)
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/dprof/discussions)

---

**Built with ❤️ for data professionals who need fast, reliable data profiling capabilities.**
