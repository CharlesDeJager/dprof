# Changelog

All notable changes to the DProf project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-27

### Added

- Initial release of DProf Data Profiling Application
- Support for CSV, JSON, XLSX, and XLS file formats
- Oracle and SQL Server database connectivity
- Parallel data processing with configurable threading
- Comprehensive column-level profiling including:
  - Data type detection and classification
  - Null and blank value analysis
  - Statistical analysis for numeric fields
  - String pattern detection and analysis
  - Data quality scoring (0-100 scale)
  - Most common values identification
- Modern React-based web interface with:
  - Drag-and-drop file upload
  - Database connection wizard
  - Real-time progress tracking
  - Interactive results dashboard
  - Responsive design for all devices
- Export capabilities:
  - Excel (XLSX) with detailed worksheets
  - JSON for programmatic access
  - HTML reports with interactive navigation
- Configuration management:
  - Web-based settings interface
  - Environment variable support
  - Configurable processing limits
- Automated setup scripts for easy installation
- Comprehensive documentation and README

### Technical Features

- FastAPI backend with async processing
- SQLAlchemy for database abstraction
- Pandas for data manipulation and analysis
- Ant Design for modern UI components
- Recharts for data visualization
- Concurrent processing with ThreadPoolExecutor
- Real-time WebSocket-style progress updates
- Error handling and recovery mechanisms

### Security

- Input validation and sanitization
- Secure file upload handling
- Database credential protection
- CORS configuration for cross-origin requests

### Performance

- Parallel processing of multiple tables
- Configurable chunk-based data processing
- Memory-efficient streaming for large datasets
- Optimized database queries with proper indexing recommendations

## [Unreleased]

### Planned Features

- PostgreSQL and MySQL database support
- Advanced data visualization charts
- Data lineage tracking
- Automated data quality rules
- API authentication and user management
- Docker containerization
- Cloud deployment support
- Advanced pattern recognition with machine learning
- Data comparison and drift detection
- Scheduled profiling jobs
- Email report delivery
- Integration with popular data catalogs

---

For more details about each release, see the [GitHub releases page](https://github.com/yourusername/dprof/releases).
