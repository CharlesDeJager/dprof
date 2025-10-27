import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  InputNumber,
  Card,
  message,
  Space,
  Tag,
  Checkbox,
} from 'antd';
import { Play, Database, FileText } from 'lucide-react';
import ApiService from '../services/api';

const TableSelector = ({ dataSource, onProfilingStart }) => {
  const [tables, setTables] = useState([]);
  const [selectedTables, setSelectedTables] = useState([]);
  const [recordCounts, setRecordCounts] = useState({});
  const [maxRecords, setMaxRecords] = useState({});
  const [loading, setLoading] = useState(false);
  const [loadingCounts, setLoadingCounts] = useState(false);

  useEffect(() => {
    if (dataSource) {
      initializeTables();
    }
  }, [dataSource]);

  const initializeTables = async () => {
    let tableList = [];

    if (dataSource.type === 'file') {
      tableList = dataSource.structure.sheets.map((sheet) => ({
        key: sheet.name,
        name: sheet.name,
        columns: sheet.columns,
        columnCount: sheet.column_count,
      }));
    } else if (dataSource.type === 'database') {
      tableList = dataSource.tables.map((table) => ({
        key: table.name,
        name: table.name,
        columns: table.columns,
        columnCount: table.column_count,
      }));
    }

    setTables(tableList);

    // Load record counts for all tables
    await loadRecordCounts(tableList);
  };

  const loadRecordCounts = async (tableList) => {
    setLoadingCounts(true);
    const counts = {};
    const maxRecs = {};

    try {
      for (const table of tableList) {
        try {
          const result = await ApiService.getRecordCount(
            dataSource.sessionId,
            table.name,
          );
          counts[table.name] = result.record_count;
          maxRecs[table.name] = Math.min(result.record_count, 10000); // Default to 10k or total
        } catch (error) {
          console.error(`Error getting count for ${table.name}:`, error);
          counts[table.name] = 'Error';
          maxRecs[table.name] = 1000;
        }
      }
    } catch (error) {
      message.error('Error loading table information');
    }

    setRecordCounts(counts);
    setMaxRecords(maxRecs);
    setLoadingCounts(false);
  };

  const handleTableSelection = (selectedRowKeys) => {
    setSelectedTables(selectedRowKeys);
  };

  const handleMaxRecordsChange = (tableName, value) => {
    setMaxRecords((prev) => ({
      ...prev,
      [tableName]: value,
    }));
  };

  const handleStartProfiling = async () => {
    if (selectedTables.length === 0) {
      message.warning('Please select at least one table to profile');
      return;
    }

    setLoading(true);

    try {
      const profilingRequest = {
        session_id: dataSource.sessionId,
        tables: selectedTables,
        max_records: selectedTables.reduce((acc, tableName) => {
          acc[tableName] = maxRecords[tableName];
          return acc;
        }, {}),
      };

      const result = await ApiService.startProfiling(profilingRequest);
      message.success('Profiling started successfully');
      onProfilingStart(result.task_id);
    } catch (error) {
      message.error(
        `Failed to start profiling: ${
          error.response?.data?.detail || error.message
        }`,
      );
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Table Name',
      dataIndex: 'name',
      key: 'name',
      render: (text) => (
        <Space>
          {dataSource.type === 'file' ? (
            <FileText size={16} />
          ) : (
            <Database size={16} />
          )}
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: 'Columns',
      dataIndex: 'columnCount',
      key: 'columnCount',
      width: 100,
      render: (count) => <Tag color='blue'>{count} cols</Tag>,
    },
    {
      title: 'Total Records',
      key: 'recordCount',
      width: 150,
      render: (_, record) => {
        const count = recordCounts[record.name];
        if (count === 'Error') {
          return <Tag color='red'>Error</Tag>;
        }
        if (loadingCounts && count === undefined) {
          return <Tag color='orange'>Loading...</Tag>;
        }
        return <Tag color='green'>{count?.toLocaleString() || 0}</Tag>;
      },
    },
    {
      title: 'Records to Profile',
      key: 'maxRecords',
      width: 200,
      render: (_, record) => {
        const totalRecords = recordCounts[record.name];
        return (
          <InputNumber
            size='small'
            value={maxRecords[record.name]}
            onChange={(value) => handleMaxRecordsChange(record.name, value)}
            min={1}
            max={totalRecords !== 'Error' ? totalRecords : 1000000}
            formatter={(value) =>
              `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
            }
            parser={(value) => value.replace(/\$\s?|(,*)/g, '')}
            style={{ width: '100%' }}
            disabled={!selectedTables.includes(record.name)}
          />
        );
      },
    },
    {
      title: 'Sample Columns',
      key: 'columns',
      render: (_, record) => (
        <div className='column-list'>
          {record.columns.slice(0, 3).map((col) => (
            <Tag key={col} size='small'>
              {col}
            </Tag>
          ))}
          {record.columns.length > 3 && (
            <Tag size='small' color='default'>
              +{record.columns.length - 3} more
            </Tag>
          )}
        </div>
      ),
    },
  ];

  const rowSelection = {
    selectedRowKeys: selectedTables,
    onChange: handleTableSelection,
    onSelect: (record, selected, selectedRows) => {
      // Auto-adjust max records when selecting/deselecting
      if (selected && !maxRecords[record.name]) {
        const totalRecords = recordCounts[record.name];
        setMaxRecords((prev) => ({
          ...prev,
          [record.name]: Math.min(totalRecords || 10000, 10000),
        }));
      }
    },
    onSelectAll: (selected, selectedRows, changeRows) => {
      // Handle select all
      changeRows.forEach((record) => {
        if (selected && !maxRecords[record.name]) {
          const totalRecords = recordCounts[record.name];
          setMaxRecords((prev) => ({
            ...prev,
            [record.name]: Math.min(totalRecords || 10000, 10000),
          }));
        }
      });
    },
  };

  const totalRecordsToProcess = selectedTables.reduce((sum, tableName) => {
    return sum + (maxRecords[tableName] || 0);
  }, 0);

  return (
    <div className='table-selector'>
      <Card
        title={
          <Space>
            <span>📊 Select Tables to Profile</span>
            <Tag color='processing'>
              {dataSource.type === 'file'
                ? dataSource.filename
                : 'Database Connection'}
            </Tag>
          </Space>
        }
        extra={
          <Space>
            <span>
              Total Records to Process:{' '}
              <strong>{totalRecordsToProcess.toLocaleString()}</strong>
            </span>
            <Button
              type='primary'
              icon={<Play size={16} />}
              onClick={handleStartProfiling}
              loading={loading}
              disabled={selectedTables.length === 0}
            >
              Start Profiling
            </Button>
          </Space>
        }
        className='main-card'
      >
        <Table
          columns={columns}
          dataSource={tables}
          rowSelection={rowSelection}
          pagination={false}
          loading={loadingCounts}
          scroll={{ x: 800 }}
          size='small'
        />

        {selectedTables.length > 0 && (
          <div className='selection-summary'>
            <h4>Selection Summary:</h4>
            <Space wrap>
              {selectedTables.map((tableName) => {
                const recordCount = maxRecords[tableName];
                const totalCount = recordCounts[tableName];
                const percentage =
                  totalCount !== 'Error' && totalCount > 0
                    ? Math.round((recordCount / totalCount) * 100)
                    : 100;

                return (
                  <Tag key={tableName} color='blue' className='selection-tag'>
                    {tableName}: {recordCount?.toLocaleString()} records (
                    {percentage}%)
                  </Tag>
                );
              })}
            </Space>
          </div>
        )}
      </Card>

      <style jsx>{`
        .table-selector {
          max-width: 1200px;
          margin: 20px auto;
          padding: 0 20px;
        }

        .main-card {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          border-radius: 12px;
          border: none;
        }

        .column-list {
          max-width: 200px;
        }

        .selection-summary {
          margin-top: 20px;
          padding: 16px;
          background: #f0f8ff;
          border-radius: 8px;
          border-left: 4px solid #1890ff;
        }

        .selection-summary h4 {
          margin: 0 0 8px 0;
          color: #1890ff;
        }

        .selection-tag {
          margin: 2px;
          font-size: 12px;
        }
      `}</style>
    </div>
  );
};

export default TableSelector;
