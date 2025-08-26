import React, { useCallback, useState } from 'react';
import { Upload, FileText, Image, AlertCircle } from 'lucide-react';
import { apiClient } from '../api';
import { JobStatus } from '../types';

interface FileUploaderProps {
  onFileUploaded: (job: JobStatus) => void;
  disabled?: boolean;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileUploaded, disabled = false }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const supportedTypes = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff'];
  const maxFileSize = 200 * 1024 * 1024; // 200MB

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [disabled]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, []);

  const validateFile = (file: File): string | null => {
    // Check file extension
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!supportedTypes.includes(extension)) {
      return `Unsupported file type. Supported formats: ${supportedTypes.join(', ')}`;
    }

    // Check file size
    if (file.size > maxFileSize) {
      return `File too large. Maximum size: ${maxFileSize / (1024 * 1024)}MB`;
    }

    return null;
  };

  const handleFile = async (file: File) => {
    setError(null);
    
    // Validate file
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsUploading(true);
    
    try {
      const response = await apiClient.uploadFile(file);
      
      // Get initial job status
      const jobStatus = await apiClient.getJobStatus(response.job_id);
      onFileUploaded(jobStatus);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    return ext === 'pdf' ? FileText : Image;
  };

  return (
    <div className="space-y-4">
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Document</h3>
        
        {/* Upload Area */}
        <div
          className={`upload-area relative border-2 border-dashed rounded-xl p-8 text-center transition-all ${
            isDragging
              ? 'border-primary-500 bg-primary-100 dragging'
              : 'border-gray-300 hover:border-primary-400'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !disabled && document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            className="hidden"
            accept={supportedTypes.join(',')}
            onChange={handleFileSelect}
            disabled={disabled || isUploading}
          />
          
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
              <Upload className={`h-8 w-8 text-primary-600 ${isUploading ? 'animate-pulse' : ''}`} />
            </div>
            
            <div>
              <p className="text-lg font-medium text-gray-900">
                {isUploading ? 'Uploading...' : 'Drop files here or click to browse'}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Supports PDF, JPG, PNG, TIFF up to 200MB
              </p>
            </div>
            
            <div className="flex justify-center space-x-4">
              <div className="flex items-center text-xs text-gray-500">
                <FileText className="h-4 w-4 mr-1" />
                PDF
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <Image className="h-4 w-4 mr-1" />
                Images
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-error-50 border border-error-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-error-600 flex-shrink-0" />
              <p className="text-sm text-error-700">{error}</p>
            </div>
          </div>
        )}

        {/* File Info */}
        <div className="mt-4 text-xs text-gray-500 space-y-1">
          <p>• All processing happens locally on your device</p>
          <p>• No data is sent to external servers</p>
          <p>• Files are not stored after processing</p>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;