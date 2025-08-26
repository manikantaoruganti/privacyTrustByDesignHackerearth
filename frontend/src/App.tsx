import React, { useState } from 'react';
import { Shield, FileText, Image, Settings, Download, AlertCircle } from 'lucide-react';
import FileUploader from './components/FileUploader';
import ProcessingStatus from './components/ProcessingStatus';
import ResultsViewer from './components/ResultsViewer';
import SettingsPanel from './components/SettingsPanel';
import { JobStatus, ProcessResult } from './types';

function App() {
  const [activeTab, setActiveTab] = useState<'upload' | 'settings'>('upload');
  const [currentJob, setCurrentJob] = useState<JobStatus | null>(null);
  const [results, setResults] = useState<ProcessResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileUploaded = (job: JobStatus) => {
    setCurrentJob(job);
    setIsProcessing(true);
    setResults(null);
  };

  const handleProcessingComplete = (result: ProcessResult) => {
    setResults(result);
    setIsProcessing(false);
  };

  const handleProcessingError = (error: string) => {
    setIsProcessing(false);
    setCurrentJob(null);
    // Could add error state here
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Shield className="h-8 w-8 text-primary-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">DocuShield AI</h1>
                <p className="text-sm text-gray-600">Privacy-Preserving Document Deidentification</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setActiveTab('upload')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'upload'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <FileText className="h-4 w-4 inline mr-2" />
                Upload
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === 'settings'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Settings className="h-4 w-4 inline mr-2" />
                Settings
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'upload' && (
          <div className="space-y-8">
            {/* Upload Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <FileUploader onFileUploaded={handleFileUploaded} disabled={isProcessing} />
              </div>
              
              <div className="space-y-6">
                {/* Info Card */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Supported Features</h3>
                  <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <FileText className="h-5 w-5 text-primary-600 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">PDF Documents</p>
                        <p className="text-xs text-gray-600">Text and scanned documents</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <Image className="h-5 w-5 text-primary-600 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Images</p>
                        <p className="text-xs text-gray-600">JPG, PNG, TIFF formats</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <Shield className="h-5 w-5 text-success-600 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Privacy-First</p>
                        <p className="text-xs text-gray-600">All processing happens locally</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Privacy Notice */}
                <div className="card bg-primary-50 border-primary-200">
                  <div className="flex items-start space-x-3">
                    <Shield className="h-5 w-5 text-primary-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="text-sm font-semibold text-primary-900">Privacy Guaranteed</h4>
                      <p className="text-xs text-primary-700 mt-1">
                        Your documents are processed locally and never leave your system. 
                        No data is sent to external servers or stored permanently.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Processing Status */}
            {(isProcessing || currentJob) && (
              <ProcessingStatus
                job={currentJob}
                onComplete={handleProcessingComplete}
                onError={handleProcessingError}
              />
            )}

            {/* Results */}
            {results && !isProcessing && (
              <ResultsViewer results={results} />
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <SettingsPanel />
        )}
      </main>
    </div>
  );
}

export default App;