import React, { useState, useEffect } from 'react';
import { Layout, Steps, Button, message } from 'antd';
import { ArrowLeft } from 'lucide-react';
import DataSourceSelector from './components/DataSourceSelector';
import TableSelector from './components/TableSelector';
import ProfilingProgress from './components/ProfilingProgress';
import ResultsDisplay from './components/ResultsDisplay';
import ApiService from './services/api';
import 'antd/dist/reset.css';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Step } = Steps;

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [dataSource, setDataSource] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [profileResults, setProfileResults] = useState(null);
  const [settings, setSettings] = useState(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const settingsData = await ApiService.getSettings();
      setSettings(settingsData);
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleDataSourceSelected = (sourceData) => {
    setDataSource(sourceData);
    setSessionId(sourceData.sessionId);
    setCurrentStep(1);
  };

  const handleSettingsUpdate = (newSettings) => {
    setSettings(newSettings);
    message.success('Settings updated successfully');
  };

  const handleProfilingStart = (profilingTaskId) => {
    setTaskId(profilingTaskId);
    setCurrentStep(2);
  };

  const handleProfilingComplete = async () => {
    try {
      const results = await ApiService.getProfilingResults(sessionId);
      setProfileResults(results);
      setCurrentStep(3);
    } catch (error) {
      message.error('Failed to load profiling results');
      console.error('Error loading results:', error);
    }
  };

  const handleNewProfiling = () => {
    setCurrentStep(0);
    setDataSource(null);
    setSessionId(null);
    setTaskId(null);
    setProfileResults(null);
  };

  const handleRestartProfiling = () => {
    setCurrentStep(1);
    setTaskId(null);
    setProfileResults(null);
  };

  const handleGoBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const steps = [
    {
      title: 'Data Source',
      description: 'Select your data source',
    },
    {
      title: 'Tables',
      description: 'Choose tables to profile',
    },
    {
      title: 'Processing',
      description: 'Profiling in progress',
    },
    {
      title: 'Results',
      description: 'View analysis results',
    },
  ];

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <DataSourceSelector
            onDataSourceSelected={handleDataSourceSelected}
            onSettingsUpdate={handleSettingsUpdate}
          />
        );
      case 1:
        return (
          <TableSelector
            dataSource={dataSource}
            onProfilingStart={handleProfilingStart}
          />
        );
      case 2:
        return (
          <ProfilingProgress
            sessionId={sessionId}
            taskId={taskId}
            onComplete={handleProfilingComplete}
            onRestart={handleRestartProfiling}
          />
        );
      case 3:
        return (
          <ResultsDisplay
            sessionId={sessionId}
            profileResults={profileResults}
            onNewProfiling={handleNewProfiling}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Layout className='app-layout'>
      <Header className='app-header'>
        <div className='header-content'>
          <div className='logo'>
            <h1>📊 DProf</h1>
            <span>Data Profiling Application</span>
          </div>
          {currentStep > 0 && (
            <Button
              icon={<ArrowLeft size={16} />}
              onClick={handleGoBack}
              type='text'
              className='back-button'
            >
              Back
            </Button>
          )}
        </div>
      </Header>

      <Content className='app-content'>
        <div className='content-wrapper'>
          <div className='steps-container'>
            <Steps current={currentStep} className='progress-steps'>
              {steps.map((step) => (
                <Step
                  key={step.title}
                  title={step.title}
                  description={step.description}
                />
              ))}
            </Steps>
          </div>

          <div className='step-content'>{renderCurrentStep()}</div>
        </div>
      </Content>

      <Footer className='app-footer'>
        <div className='footer-content'>
          <p>
            © 2024 DProf Data Profiling Application. Built with React, FastAPI,
            and modern data analysis tools.
          </p>
          {settings && (
            <div className='settings-info'>
              <small>
                Max Threads: {settings.max_threads} | Default Records:{' '}
                {settings.default_max_records?.toLocaleString()} | Chunk Size:{' '}
                {settings.chunk_size?.toLocaleString()}
              </small>
            </div>
          )}
        </div>
      </Footer>
    </Layout>
  );
}

export default App;
