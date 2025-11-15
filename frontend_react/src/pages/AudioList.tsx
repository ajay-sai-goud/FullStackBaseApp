import React, { useState, useEffect } from 'react';
import { getAudioFiles, updateAudioFile, deleteAudioFile, getPlaybackUrl } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Permissions } from '../utils/permissions';
import AudioPlayer from '../components/AudioPlayer';
import UploadModal from '../components/UploadModal';
import ConfirmDialog from '../components/ConfirmDialog';
import ActionButton from '../components/ActionButton';
import Button from '../components/Button';
import { AudioFile } from '../types';

const AudioList: React.FC = () => {
  const [files, setFiles] = useState<AudioFile[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState<boolean>(false);
  const [editingFileId, setEditingFileId] = useState<string | null>(null);
  const [editingFileName, setEditingFileName] = useState<string>('');
  const [deletingFileId, setDeletingFileId] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<{ isOpen: boolean; fileId: string | null; fileName: string }>({
    isOpen: false,
    fileId: null,
    fileName: '',
  });
  const { hasAnyPermission } = useAuth();

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAudioFiles();
      setFiles(response.files || []);
    } catch (err) {
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosError.response?.status === 401) {
        // Handled by interceptor
      } else {
        setError(axiosError.response?.data?.detail || 'Failed to load audio files');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleUploadSuccess = (): void => {
    // Refresh the audio list after successful upload
    fetchFiles();
  };

  const handleEdit = (file: AudioFile): void => {
    setEditingFileId(file.id);
    setEditingFileName(file.file_name);
  };

  const handleEditCancel = (): void => {
    setEditingFileId(null);
    setEditingFileName('');
  };

  const handleEditSave = async (fileId: string): Promise<void> => {
    if (!editingFileName.trim()) {
      setError('File name cannot be empty');
      return;
    }

    try {
      setError(null);
      await updateAudioFile(fileId, { file_name: editingFileName.trim() });
      setEditingFileId(null);
      setEditingFileName('');
      // Refresh the list
      fetchFiles();
    } catch (err) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to update file');
    }
  };

  const handleDelete = (fileId: string, fileName: string): void => {
    setConfirmDelete({
      isOpen: true,
      fileId,
      fileName,
    });
  };

  const handleConfirmDelete = async (): Promise<void> => {
    if (!confirmDelete.fileId) return;

    try {
      setDeletingFileId(confirmDelete.fileId);
      setError(null);
      await deleteAudioFile(confirmDelete.fileId);
      // Remove from list
      setFiles(files.filter((file) => file.id !== confirmDelete.fileId));
      setConfirmDelete({ isOpen: false, fileId: null, fileName: '' });
    } catch (err) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to delete file');
    } finally {
      setDeletingFileId(null);
    }
  };

  const handleCancelDelete = (): void => {
    setConfirmDelete({ isOpen: false, fileId: null, fileName: '' });
  };

  const handleDownload = async (fileId: string, fileName: string): Promise<void> => {
    try {
      setError(null);
      // Get the playback URL (signed URL from backend)
      const response = await getPlaybackUrl(fileId);
      const signedUrl = response.signed_url;

      // Create a temporary anchor element and trigger download
      // Using anchor tag bypasses CORS restrictions that affect fetch() requests
      const link = document.createElement('a');
      link.href = signedUrl;
      link.download = fileName;
      link.target = '_blank'; // Open in new tab as fallback
      link.style.display = 'none'; // Hide the link
      document.body.appendChild(link);
      link.click();

      // Clean up
      document.body.removeChild(link);
    } catch (err) {
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to download file');
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner">Loading audio files...</div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="page-container">
        <div className="audio-list-header">
          <h1>My Audio Files</h1>
          {files.length > 0 && hasAnyPermission(Permissions.WRITE_AUDIO, Permissions.ADMIN) && (
            <div className="header-actions">
              <Button onClick={() => setIsUploadModalOpen(true)} variant="primary">
                Upload Audio
              </Button>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            <span>{error}</span>
            <button 
              onClick={() => setError(null)} 
              className="close-error-btn"
              aria-label="Close error message"
              type="button"
            >
              &times;
            </button>
          </div>
        )}

        {files.length === 0 ? (
          <div className="empty-state">
            <p>No audio files found. Upload your first audio file!</p>
            {hasAnyPermission(Permissions.WRITE_AUDIO, Permissions.ADMIN) && (
              <Button onClick={() => setIsUploadModalOpen(true)} variant="primary">
                Upload Audio
              </Button>
            )}
          </div>
        ) : (
          <div className="audio-files-list">
            {files.map((file) => (
              <div key={file.id} className="audio-file-card">
                <div className="audio-file-info">
                  {editingFileId === file.id ? (
                    <div className="edit-file-form">
                      <input
                        type="text"
                        value={editingFileName}
                        onChange={(e) => setEditingFileName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            handleEditSave(file.id);
                          } else if (e.key === 'Escape') {
                            handleEditCancel();
                          }
                        }}
                        className="edit-file-input"
                        placeholder="File name"
                        autoFocus
                      />
                      <div className="edit-file-actions">
                        <ActionButton
                          variant="save"
                          onClick={() => handleEditSave(file.id)}
                          title="Save"
                        />
                        <ActionButton
                          variant="cancel"
                          onClick={handleEditCancel}
                          title="Cancel"
                        />
                      </div>
                    </div>
                  ) : (
                    <>
                      <h3 className="audio-file-name">{file.file_name}</h3>
                      <p className="audio-file-date">
                        Uploaded: {formatDate(file.created_at)}
                      </p>
                      {file.file_type && (
                        <p className="audio-file-type">Type: {file.file_type}</p>
                      )}
                    </>
                  )}
                </div>
                <div className="audio-file-actions">
                  {editingFileId !== file.id && (
                    <>
                      <ActionButton
                        variant="download"
                        onClick={() => handleDownload(file.id, file.file_name)}
                        title="Download file"
                      />
                      {hasAnyPermission(Permissions.WRITE_AUDIO, Permissions.ADMIN) && (
                        <ActionButton
                          variant="edit"
                          onClick={() => handleEdit(file)}
                          title="Edit file name"
                        />
                      )}
                      {hasAnyPermission(Permissions.DELETE_AUDIO, Permissions.ADMIN) && (
                        <ActionButton
                          variant="delete"
                          onClick={() => handleDelete(file.id, file.file_name)}
                          disabled={deletingFileId === file.id}
                          title="Delete file"
                        />
                      )}
                    </>
                  )}
                </div>
                <div className="audio-file-player">
                  <AudioPlayer fileId={file.id} fileName={file.file_name} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {hasAnyPermission(Permissions.WRITE_AUDIO, Permissions.ADMIN) && (
        <UploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onUploadSuccess={handleUploadSuccess}
        />
      )}

      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        isOpen={confirmDelete.isOpen}
        title="Delete Audio File"
        message={`Are you sure you want to delete "${confirmDelete.fileName}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        variant="danger"
      />
    </>
  );
};

export default AudioList;

