import React, { useState, FormEvent, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadAudioFile } from '../services/api';
import Button from '../components/Button';

const Upload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError('');
      setSuccess(false);
    }
  };

  const handleUpload = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess(false);

    try {
      await uploadAudioFile(selectedFile);
      setSuccess(true);
      // Redirect to audio list after 1 second
      setTimeout(() => {
        navigate('/audio');
      }, 1000);
    } catch (err) {
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosError.response?.status === 401) {
        // Handled by interceptor
      } else {
        setError(
          axiosError.response?.data?.detail ||
            'Upload failed. Please check the file format and size.'
        );
      }
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="page-container">
      <div className="upload-container">
        <div className="upload-header">
          <h1>Upload Audio File</h1>
        </div>

        <div className="upload-card">
          <form onSubmit={handleUpload} className="upload-form">
            <div className="form-group">
              <label htmlFor="file">Select Audio File</label>
              <div className="file-input">
                <input
                  type="file"
                  id="file"
                  accept="audio/*"
                  onChange={handleFileChange}
                  disabled={uploading}
                />
                <label
                  htmlFor="file"
                  className={`file-input-label ${selectedFile ? 'has-file' : ''}`}
                >
                  {selectedFile ? (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                      </svg>
                      <span>{selectedFile.name}</span>
                    </>
                  ) : (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                      </svg>
                      <span>Choose file or drag and drop</span>
                    </>
                  )}
                </label>
              </div>
              {selectedFile && (
                <div className="file-info">
                  <div className="file-info-row">
                    <span className="file-info-label">File Name:</span>
                    <span className="file-info-value">{selectedFile.name}</span>
                  </div>
                  <div className="file-info-row">
                    <span className="file-info-label">Size:</span>
                    <span className="file-info-value">{formatFileSize(selectedFile.size)}</span>
                  </div>
                  <div className="file-info-row">
                    <span className="file-info-label">Type:</span>
                    <span className="file-info-value">{selectedFile.type || 'Unknown'}</span>
                  </div>
                </div>
              )}
            </div>

            {error && <div className="error-message">{error}</div>}

            {success && (
              <div className="success-message">
                File uploaded successfully! Redirecting...
              </div>
            )}

            <div className="form-actions">
              <Button
                type="submit"
                variant="primary"
                isLoading={uploading}
                disabled={!selectedFile || uploading}
              >
                {uploading ? 'Uploading...' : 'Upload File'}
              </Button>
            </div>
          </form>

          <div className="upload-info">
            <h3>Supported Formats:</h3>
            <ul>
              <li>MP3 (.mp3)</li>
              <li>WAV (.wav)</li>
              <li>AAC/M4A (.m4a, .aac)</li>
              <li>OGG (.ogg, .oga)</li>
              <li>OPUS (.opus)</li>
            </ul>
            <p className="file-size-limit">Maximum file size: 100MB</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;

