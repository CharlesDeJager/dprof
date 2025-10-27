import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Database, Settings } from 'lucide-react';
import {
  Button,
  Card,
  message,
  Tabs,
  Form,
  Input,
  InputNumber,
  Select,
} from 'antd';
import ApiService from '../services/api';

const { TabPane } = Tabs;

const DataSourceSelector = ({ onDataSourceSelected, onSettingsUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [connectionForm] = Form.useForm();
  const [settingsForm] = Form.useForm();
  const [activeTab, setActiveTab] = useState('file');

  // File upload handler
  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setLoading(true);

        try {
          const result = await ApiService.uploadFile(file);
          message.success(`File uploaded successfully: ${result.filename}`);
          onDataSourceSelected({
            type: 'file',
            sessionId: result.session_id,
            filename: result.filename,
            structure: result.structure,
          });
        } catch (error) {
          message.error(
            `Upload failed: ${error.response?.data?.detail || error.message}`,
          );
        } finally {
          setLoading(false);
        }
      }
    },
    [onDataSourceSelected],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [
        '.xlsx',
      ],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
  });

  // Database connection handler
  const handleDatabaseConnect = async (values) => {
    setLoading(true);

    try {
      const result = await ApiService.connectDatabase(values);
      message.success('Database connected successfully');
      onDataSourceSelected({
        type: 'database',
        sessionId: result.session_id,
        tables: result.tables,
        connection: values,
      });
    } catch (error) {
      message.error(
        `Connection failed: ${error.response?.data?.detail || error.message}`,
      );
    } finally {
      setLoading(false);
    }
  };

  // Settings update handler
  const handleSettingsUpdate = async (values) => {
    try {
      await ApiService.updateSettings(values);
      message.success('Settings updated successfully');
      onSettingsUpdate(values);
    } catch (error) {
      message.error(
        `Settings update failed: ${
          error.response?.data?.detail || error.message
        }`,
      );
    }
  };

  return (
    <div className='data-source-selector'>
      <Card title='🎯 Select Data Source' className='main-card'>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane
            tab={
              <span>
                <FileText size={16} /> Files
              </span>
            }
            key='file'
          >
            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'active' : ''} ${
                loading ? 'loading' : ''
              }`}
            >
              <input {...getInputProps()} />
              <Upload size={48} className='upload-icon' />
              <div className='upload-text'>
                <h3>Drop files here or click to browse</h3>
                <p>Supports CSV, JSON, XLSX, and XLS files</p>
                {loading && <p className='loading-text'>Uploading...</p>}
              </div>
            </div>
          </TabPane>

          <TabPane
            tab={
              <span>
                <Database size={16} /> Database
              </span>
            }
            key='database'
          >
            <Form
              form={connectionForm}
              layout='vertical'
              onFinish={handleDatabaseConnect}
              className='database-form'
            >
              <Form.Item
                name='connection_type'
                label='Database Type'
                rules={[
                  { required: true, message: 'Please select database type' },
                ]}
              >
                <Select placeholder='Select database type'>
                  <Select.Option value='oracle'>Oracle</Select.Option>
                  <Select.Option value='sqlserver'>SQL Server</Select.Option>
                </Select>
              </Form.Item>

              <div className='form-row'>
                <Form.Item
                  name='host'
                  label='Host'
                  rules={[{ required: true, message: 'Please enter host' }]}
                >
                  <Input placeholder='localhost' />
                </Form.Item>

                <Form.Item
                  name='port'
                  label='Port'
                  rules={[{ required: true, message: 'Please enter port' }]}
                >
                  <InputNumber placeholder='1521' style={{ width: '100%' }} />
                </Form.Item>
              </div>

              <Form.Item
                name='database'
                label='Database/Service Name'
                rules={[
                  { required: true, message: 'Please enter database name' },
                ]}
              >
                <Input placeholder='ORCL' />
              </Form.Item>

              <div className='form-row'>
                <Form.Item
                  name='username'
                  label='Username'
                  rules={[{ required: true, message: 'Please enter username' }]}
                >
                  <Input placeholder='username' />
                </Form.Item>

                <Form.Item
                  name='password'
                  label='Password'
                  rules={[{ required: true, message: 'Please enter password' }]}
                >
                  <Input.Password placeholder='password' />
                </Form.Item>
              </div>

              <Form.Item>
                <Button
                  type='primary'
                  htmlType='submit'
                  loading={loading}
                  block
                >
                  Connect to Database
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          <TabPane
            tab={
              <span>
                <Settings size={16} /> Settings
              </span>
            }
            key='settings'
          >
            <Form
              form={settingsForm}
              layout='vertical'
              onFinish={handleSettingsUpdate}
              initialValues={{
                max_threads: 4,
                default_max_records: 10000,
                chunk_size: 1000,
              }}
            >
              <Form.Item
                name='max_threads'
                label='Maximum Threads'
                help='Number of parallel threads for processing'
              >
                <InputNumber min={1} max={16} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name='default_max_records'
                label='Default Max Records'
                help='Default number of records to process per table'
              >
                <InputNumber
                  min={100}
                  max={1000000}
                  style={{ width: '100%' }}
                />
              </Form.Item>

              <Form.Item
                name='chunk_size'
                label='Chunk Size'
                help='Number of records to process in each chunk'
              >
                <InputNumber min={100} max={10000} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item>
                <Button type='primary' htmlType='submit' block>
                  Update Settings
                </Button>
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Card>

      <style jsx>{`
        .data-source-selector {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }

        .main-card {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          border-radius: 12px;
          border: none;
        }

        .dropzone {
          border: 2px dashed #d9d9d9;
          border-radius: 8px;
          padding: 40px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          background: #fafafa;
        }

        .dropzone:hover {
          border-color: #1890ff;
          background: #f0f8ff;
        }

        .dropzone.active {
          border-color: #1890ff;
          background: #e6f7ff;
        }

        .dropzone.loading {
          border-color: #52c41a;
          background: #f6ffed;
        }

        .upload-icon {
          color: #8c8c8c;
          margin-bottom: 16px;
        }

        .upload-text h3 {
          margin: 0 0 8px 0;
          color: #262626;
        }

        .upload-text p {
          margin: 0;
          color: #8c8c8c;
        }

        .loading-text {
          color: #52c41a !important;
          font-weight: 500;
        }

        .database-form {
          max-width: 500px;
        }

        .form-row {
          display: flex;
          gap: 16px;
        }

        .form-row .ant-form-item {
          flex: 1;
        }
      `}</style>
    </div>
  );
};

export default DataSourceSelector;
