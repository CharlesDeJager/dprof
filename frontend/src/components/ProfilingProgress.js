import React, { useState, useEffect, useRef } from 'react';
import { Progress, Card, Alert, Button, Space } from 'antd';
import { CheckCircle, XCircle, RotateCw, Play } from 'lucide-react';
import ApiService from '../services/api';

const ProfilingProgress = ({ sessionId, taskId, onComplete, onRestart }) => {
  const [status, setStatus] = useState('running');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [resultsAvailable, setResultsAvailable] = useState(false);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(null);
  const intervalRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  useEffect(() => {
    if (sessionId && taskId) {
      startTimeRef.current = Date.now();
      checkStatus();
      intervalRef.current = setInterval(checkStatus, 2000); // Check every 2 seconds
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [sessionId, taskId]);

  const checkStatus = async () => {
    try {
      const result = await ApiService.getProfilingStatus(sessionId);

      setStatus(result.status);
      setProgress(result.progress);
      setError(result.error);
      setResultsAvailable(result.results_available);

      // Calculate estimated time remaining
      if (result.status === 'running' && result.progress > 0) {
        const elapsed = Date.now() - startTimeRef.current;
        const estimatedTotal = (elapsed / result.progress) * 100;
        const remaining = Math.max(0, estimatedTotal - elapsed);
        setEstimatedTimeRemaining(remaining);
      }

      // Stop polling when completed or failed
      if (result.status === 'completed' || result.status === 'error') {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }

        if (result.status === 'completed' && result.results_available) {
          setTimeout(() => onComplete(), 1000); // Small delay to show completion
        }
      }
    } catch (error) {
      console.error('Error checking profiling status:', error);
      setError('Failed to check profiling status');
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'running':
        return <RotateCw className='spinning' size={24} color='#1890ff' />;
      case 'completed':
        return <CheckCircle size={24} color='#52c41a' />;
      case 'error':
        return <XCircle size={24} color='#ff4d4f' />;
      default:
        return <Play size={24} color='#8c8c8c' />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'running':
        return '#1890ff';
      case 'completed':
        return '#52c41a';
      case 'error':
        return '#ff4d4f';
      default:
        return '#d9d9d9';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'running':
        return 'Processing data...';
      case 'completed':
        return 'Profiling completed successfully!';
      case 'error':
        return 'Profiling failed';
      default:
        return 'Preparing to start...';
    }
  };

  const formatTimeRemaining = (milliseconds) => {
    if (!milliseconds || milliseconds <= 0) return null;

    const seconds = Math.ceil(milliseconds / 1000);

    if (seconds < 60) {
      return `${seconds} second${seconds !== 1 ? 's' : ''}`;
    } else if (seconds < 3600) {
      const minutes = Math.ceil(seconds / 60);
      return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
    } else {
      const hours = Math.ceil(seconds / 3600);
      return `${hours} hour${hours !== 1 ? 's' : ''}`;
    }
  };

  return (
    <div className='profiling-progress'>
      <Card
        title={
          <Space>
            {getStatusIcon()}
            <span>Data Profiling Progress</span>
          </Space>
        }
        className='progress-card'
        extra={
          status === 'error' && (
            <Button
              type='primary'
              icon={<RotateCw size={16} />}
              onClick={onRestart}
            >
              Restart
            </Button>
          )
        }
      >
        <div className='progress-content'>
          <div className='status-section'>
            <h3>{getStatusText()}</h3>
            <Progress
              percent={progress}
              status={
                status === 'error'
                  ? 'exception'
                  : status === 'completed'
                  ? 'success'
                  : 'active'
              }
              strokeColor={getStatusColor()}
              size='large'
            />

            <div className='progress-details'>
              <Space direction='vertical' style={{ width: '100%' }}>
                <div className='detail-row'>
                  <span>Progress:</span>
                  <strong>{progress}%</strong>
                </div>

                {status === 'running' && estimatedTimeRemaining && (
                  <div className='detail-row'>
                    <span>Estimated time remaining:</span>
                    <strong>
                      {formatTimeRemaining(estimatedTimeRemaining)}
                    </strong>
                  </div>
                )}

                {status === 'completed' && (
                  <div className='detail-row'>
                    <span>Status:</span>
                    <strong style={{ color: '#52c41a' }}>
                      Ready to view results
                    </strong>
                  </div>
                )}
              </Space>
            </div>
          </div>

          {error && (
            <Alert
              message='Profiling Error'
              description={error}
              type='error'
              showIcon
              style={{ marginTop: 20 }}
            />
          )}

          {status === 'running' && (
            <div className='processing-info'>
              <Alert
                message='Processing Information'
                description='The profiling engine is analyzing your data using parallel processing. This includes calculating statistics, detecting patterns, and generating quality scores for each column.'
                type='info'
                showIcon
              />
            </div>
          )}

          {status === 'completed' && resultsAvailable && (
            <div className='completion-info'>
              <Alert
                message='Profiling Complete'
                description='Data profiling has completed successfully. You can now view detailed analysis results, export reports, or start a new profiling session.'
                type='success'
                showIcon
                action={
                  <Button size='small' type='primary' onClick={onComplete}>
                    View Results
                  </Button>
                }
              />
            </div>
          )}
        </div>
      </Card>

      <style jsx>{`
        .profiling-progress {
          max-width: 800px;
          margin: 20px auto;
          padding: 0 20px;
        }

        .progress-card {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          border-radius: 12px;
          border: none;
        }

        .progress-content {
          padding: 20px 0;
        }

        .status-section h3 {
          text-align: center;
          margin-bottom: 20px;
          color: #262626;
          font-size: 18px;
        }

        .progress-details {
          margin-top: 20px;
          background: #fafafa;
          padding: 16px;
          border-radius: 8px;
        }

        .detail-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin: 8px 0;
        }

        .detail-row span {
          color: #8c8c8c;
        }

        .processing-info,
        .completion-info {
          margin-top: 20px;
        }

        .spinning {
          animation: spin 2s linear infinite;
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default ProfilingProgress;
