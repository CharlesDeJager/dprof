import React, { useState, useEffect } from 'react';
import {
  Card,
  Tabs,
  Table,
  Statistic,
  Progress,
  Tag,
  Alert,
  Button,
  Space,
  Tooltip,
  Modal,
  List,
  Row,
  Col,
  message,
} from 'antd';
import {
  Download,
  FileText,
  Database,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  BarChart3,
  Eye,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts';
import ApiService from '../services/api';

const { TabPane } = Tabs;

const ResultsDisplay = ({
  sessionId,
  profileResults,
  onExport,
  onNewProfiling,
}) => {
  const [selectedTable, setSelectedTable] = useState(null);
  const [patternModalVisible, setPatternModalVisible] = useState(false);
  const [selectedPatterns, setSelectedPatterns] = useState([]);
  const [selectedColumn, setSelectedColumn] = useState(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (profileResults && Object.keys(profileResults).length > 0) {
      setSelectedTable(Object.keys(profileResults)[0]);
    }
  }, [profileResults]);

  const handleExport = async (format) => {
    if (!profileResults || Object.keys(profileResults).length === 0) {
      message.error('No data to export');
      return;
    }

    setExporting(true);
    try {
      const exportRequest = {
        session_id: sessionId,
        export_format: format,
        tables: Object.keys(profileResults),
      };

      const blob = await ApiService.exportResults(exportRequest);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `data_profile_${
        new Date().toISOString().split('T')[0]
      }.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.success(
        `Export completed: ${format.toUpperCase()} file downloaded`,
      );
    } catch (error) {
      message.error(`Export failed: ${error.message}`);
    } finally {
      setExporting(false);
    }
  };

  const showPatterns = (patterns, columnName) => {
    setSelectedPatterns(patterns);
    setSelectedColumn(columnName);
    setPatternModalVisible(true);
  };

  const getQualityColor = (score) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  };

  const getDataTypeIcon = (dataType) => {
    if (['int64', 'float64', 'numeric'].includes(dataType)) {
      return <BarChart3 size={16} color='#1890ff' />;
    }
    if (['object', 'string'].includes(dataType)) {
      return <FileText size={16} color='#722ed1' />;
    }
    return <Database size={16} color='#8c8c8c' />;
  };

  if (!profileResults || Object.keys(profileResults).length === 0) {
    return (
      <div className='results-display'>
        <Alert
          message='No Results Available'
          description='No profiling results to display. Please start a new profiling session.'
          type='info'
          showIcon
          action={
            <Button type='primary' onClick={onNewProfiling}>
              New Profiling
            </Button>
          }
        />
      </div>
    );
  }

  const tableNames = Object.keys(profileResults);
  const currentTableData = selectedTable ? profileResults[selectedTable] : null;

  // Generate summary statistics
  const totalTables = tableNames.length;
  const totalRecords = Object.values(profileResults).reduce(
    (sum, table) => sum + (table.total_records || 0),
    0,
  );
  const totalColumns = Object.values(profileResults).reduce(
    (sum, table) => sum + (table.total_columns || 0),
    0,
  );
  const avgQuality =
    Object.values(profileResults).reduce((sum, table) => {
      if (!table.columns) return sum;
      const tableAvg =
        Object.values(table.columns).reduce(
          (colSum, col) => colSum + (col.data_quality_score || 0),
          0,
        ) / Object.keys(table.columns).length;
      return sum + (tableAvg || 0);
    }, 0) / totalTables;

  // Prepare column data for table display
  const columnData = currentTableData?.columns
    ? Object.entries(currentTableData.columns).map(([name, data]) => ({
        key: name,
        name,
        ...data,
      }))
    : [];

  const columnColumns = [
    {
      title: 'Column',
      dataIndex: 'name',
      key: 'name',
      fixed: 'left',
      width: 150,
      render: (text, record) => (
        <Space direction='vertical' size={0}>
          <Space>
            {getDataTypeIcon(record.data_type)}
            <strong>{text}</strong>
          </Space>
          <Tag size='small' color='blue'>
            {record.data_type}
          </Tag>
        </Space>
      ),
    },
    {
      title: 'Quality',
      dataIndex: 'data_quality_score',
      key: 'quality',
      width: 120,
      sorter: (a, b) =>
        (a.data_quality_score || 0) - (b.data_quality_score || 0),
      render: (score) => (
        <div>
          <Progress
            percent={score || 0}
            size='small'
            strokeColor={getQualityColor(score)}
            format={() => `${Math.round(score || 0)}`}
          />
        </div>
      ),
    },
    {
      title: 'Completeness',
      dataIndex: 'completeness',
      key: 'completeness',
      width: 100,
      sorter: (a, b) => (a.completeness || 0) - (b.completeness || 0),
      render: (completeness) => (
        <Tag
          color={
            completeness >= 95 ? 'green' : completeness >= 80 ? 'orange' : 'red'
          }
        >
          {Math.round(completeness || 0)}%
        </Tag>
      ),
    },
    {
      title: 'Uniqueness',
      dataIndex: 'uniqueness',
      key: 'uniqueness',
      width: 100,
      sorter: (a, b) => (a.uniqueness || 0) - (b.uniqueness || 0),
      render: (uniqueness) => `${Math.round(uniqueness || 0)}%`,
    },
    {
      title: 'Nulls',
      key: 'nulls',
      width: 80,
      render: (_, record) => (
        <Tooltip title={`${record.null_count || 0} null values`}>
          <Tag
            color={
              record.null_percentage <= 5
                ? 'green'
                : record.null_percentage <= 20
                ? 'orange'
                : 'red'
            }
          >
            {Math.round(record.null_percentage || 0)}%
          </Tag>
        </Tooltip>
      ),
    },
    {
      title: 'Distinct',
      dataIndex: 'distinct_count',
      key: 'distinct',
      width: 100,
      render: (distinct, record) => (
        <Space direction='vertical' size={0}>
          <span>{(distinct || 0).toLocaleString()}</span>
          <small style={{ color: '#8c8c8c' }}>
            {Math.round(record.distinct_percentage || 0)}%
          </small>
        </Space>
      ),
    },
    {
      title: 'Statistics',
      key: 'stats',
      width: 150,
      render: (_, record) => {
        if (['int64', 'float64', 'numeric'].includes(record.data_type)) {
          return (
            <Space direction='vertical' size={0}>
              <small>Min: {record.min_value?.toLocaleString() || 'N/A'}</small>
              <small>Max: {record.max_value?.toLocaleString() || 'N/A'}</small>
              <small>Avg: {record.average?.toFixed(2) || 'N/A'}</small>
            </Space>
          );
        }
        if (['object', 'string'].includes(record.data_type)) {
          return (
            <Space direction='vertical' size={0}>
              <small>
                Avg Length: {record.avg_length?.toFixed(1) || 'N/A'}
              </small>
              <small>
                Range: {record.min_length || 0}-{record.max_length || 0}
              </small>
            </Space>
          );
        }
        return <span style={{ color: '#8c8c8c' }}>N/A</span>;
      },
    },
    {
      title: 'Issues',
      key: 'issues',
      width: 120,
      render: (_, record) => (
        <Space direction='vertical' size={0}>
          {(record.potential_issues || []).slice(0, 2).map((issue) => (
            <Tag
              key={issue}
              size='small'
              color='red'
              icon={<AlertTriangle size={10} />}
            >
              {issue}
            </Tag>
          ))}
          {(record.potential_issues || []).length > 2 && (
            <small style={{ color: '#8c8c8c' }}>
              +{(record.potential_issues || []).length - 2} more
            </small>
          )}
        </Space>
      ),
    },
    {
      title: 'Patterns',
      key: 'patterns',
      width: 100,
      render: (_, record) => {
        const patterns = record.patterns || [];
        return patterns.length > 0 ? (
          <Button
            size='small'
            type='link'
            icon={<Eye size={12} />}
            onClick={() => showPatterns(patterns, record.name)}
          >
            View ({patterns.length})
          </Button>
        ) : (
          <span style={{ color: '#8c8c8c' }}>None</span>
        );
      },
    },
  ];

  // Prepare chart data for quality distribution
  const qualityDistribution = columnData.reduce((acc, col) => {
    const score = col.data_quality_score || 0;
    let bucket;
    if (score >= 90) bucket = '90-100';
    else if (score >= 80) bucket = '80-89';
    else if (score >= 70) bucket = '70-79';
    else if (score >= 60) bucket = '60-69';
    else bucket = '0-59';

    acc[bucket] = (acc[bucket] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(qualityDistribution).map(
    ([range, count]) => ({
      range,
      count,
      color:
        range === '90-100'
          ? '#52c41a'
          : range === '80-89'
          ? '#1890ff'
          : range === '70-79'
          ? '#faad14'
          : '#ff4d4f',
    }),
  );

  return (
    <div className='results-display'>
      {/* Header with Export Options */}
      <Card
        title='📊 Data Profiling Results'
        extra={
          <Space>
            <Button
              icon={<Download size={16} />}
              onClick={() => handleExport('xlsx')}
              loading={exporting}
            >
              Excel
            </Button>
            <Button
              icon={<Download size={16} />}
              onClick={() => handleExport('json')}
              loading={exporting}
            >
              JSON
            </Button>
            <Button
              type='primary'
              icon={<Download size={16} />}
              onClick={() => handleExport('html')}
              loading={exporting}
            >
              HTML Report
            </Button>
          </Space>
        }
        className='header-card'
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={6}>
            <Statistic
              title='Total Tables'
              value={totalTables}
              prefix={<Database size={16} />}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Statistic
              title='Total Records'
              value={totalRecords}
              formatter={(value) => value.toLocaleString()}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Statistic title='Total Columns' value={totalColumns} />
          </Col>
          <Col xs={24} sm={6}>
            <Statistic
              title='Avg Quality Score'
              value={avgQuality}
              precision={1}
              valueStyle={{ color: getQualityColor(avgQuality) }}
            />
          </Col>
        </Row>
      </Card>

      {/* Main Results */}
      <Tabs
        activeKey={selectedTable}
        onChange={setSelectedTable}
        items={tableNames.map((tableName) => ({
          key: tableName,
          label: (
            <Space>
              <Database size={16} />
              {tableName}
              <Tag size='small'>
                {profileResults[tableName]?.total_records?.toLocaleString() ||
                  0}{' '}
                records
              </Tag>
            </Space>
          ),
          children: (
            <div className='table-results'>
              {profileResults[tableName]?.error ? (
                <Alert
                  message='Profiling Error'
                  description={profileResults[tableName].error}
                  type='error'
                  showIcon
                />
              ) : (
                <>
                  {/* Table Summary */}
                  <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                    <Col xs={24} lg={16}>
                      <Card title='Column Quality Distribution' size='small'>
                        <ResponsiveContainer width='100%' height={200}>
                          <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray='3 3' />
                            <XAxis dataKey='range' />
                            <YAxis />
                            <RechartsTooltip />
                            <Bar dataKey='count' fill='#1890ff' />
                          </BarChart>
                        </ResponsiveContainer>
                      </Card>
                    </Col>
                    <Col xs={24} lg={8}>
                      <Card title='Table Summary' size='small'>
                        <Space direction='vertical' style={{ width: '100%' }}>
                          <Statistic
                            title='Records'
                            value={currentTableData?.total_records || 0}
                            formatter={(value) => value.toLocaleString()}
                          />
                          <Statistic
                            title='Columns'
                            value={currentTableData?.total_columns || 0}
                          />
                          <div>
                            <small style={{ color: '#8c8c8c' }}>
                              Profiled at:
                            </small>
                            <br />
                            <small>
                              {new Date(
                                currentTableData?.profiled_at,
                              ).toLocaleString()}
                            </small>
                          </div>
                        </Space>
                      </Card>
                    </Col>
                  </Row>

                  {/* Column Details Table */}
                  <Card title='Column Analysis' size='small'>
                    <Table
                      columns={columnColumns}
                      dataSource={columnData}
                      pagination={{ pageSize: 20 }}
                      scroll={{ x: 1200 }}
                      size='small'
                    />
                  </Card>
                </>
              )}
            </div>
          ),
        }))}
      />

      {/* Pattern Modal */}
      <Modal
        title={`String Patterns - ${selectedColumn}`}
        visible={patternModalVisible}
        onCancel={() => setPatternModalVisible(false)}
        footer={null}
        width={700}
      >
        <List
          dataSource={selectedPatterns}
          renderItem={(pattern) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <Space>
                    <Tag color='blue'>{pattern.pattern}</Tag>
                    <small style={{ color: '#8c8c8c' }}>
                      {pattern.count} occurrences ({pattern.percentage}%)
                    </small>
                  </Space>
                }
                description={
                  <Space wrap>
                    <span>Examples:</span>
                    {pattern.examples.map((example, idx) => (
                      <Tag key={idx} size='small'>
                        {example}
                      </Tag>
                    ))}
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Modal>

      <style jsx>{`
        .results-display {
          max-width: 1400px;
          margin: 20px auto;
          padding: 0 20px;
        }

        .header-card {
          margin-bottom: 20px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          border-radius: 12px;
          border: none;
        }

        .table-results {
          min-height: 400px;
        }
      `}</style>
    </div>
  );
};

export default ResultsDisplay;
