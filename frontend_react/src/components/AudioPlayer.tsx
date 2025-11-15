import React, { useState, useEffect, useRef } from 'react';
import { getPlaybackUrl } from '../services/api';
import { AudioPlayerProps } from '../types';
import './AudioPlayer.css';

/**
 * Professional custom audio player component
 * Features: Play/Pause, Seek, Volume Control, Time Display
 */
const AudioPlayer: React.FC<AudioPlayerProps> = ({ fileId, fileName }) => {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [volume, setVolume] = useState<number>(1);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isVolumeDragging, setIsVolumeDragging] = useState<boolean>(false);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressBarRef = useRef<HTMLDivElement | null>(null);
  const volumeBarRef = useRef<HTMLDivElement | null>(null);

  // Fetch playback URL
  useEffect(() => {
    const fetchPlaybackUrl = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);
        const response = await getPlaybackUrl(fileId);
        setAudioUrl(response.signed_url);
      } catch (err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setError(axiosError.response?.data?.detail || 'Failed to load audio');
        console.error('Error fetching playback URL:', err);
      } finally {
        setLoading(false);
      }
    };

    if (fileId) {
      fetchPlaybackUrl();
    }
  }, [fileId]);

  // Initialize audio element
  useEffect(() => {
    if (!audioUrl) return;

    const audio = new Audio(audioUrl);
    audioRef.current = audio;

    // Event listeners
    const updateTime = () => {
      if (!isDragging && audioRef.current) {
        setCurrentTime(audioRef.current.currentTime);
      }
    };

    const updateDuration = () => {
      if (audioRef.current) {
        setDuration(audioRef.current.duration);
      }
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);

    audio.volume = volume;
    audio.muted = isMuted;

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.pause();
      audio.src = '';
      audioRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioUrl, isDragging]);

  // Update volume and mute
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
      audioRef.current.muted = isMuted;
    }
  }, [volume, isMuted]);

  // Play/Pause handler
  const togglePlayPause = (): void => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch((err) => {
        console.error('Error playing audio:', err);
        setError('Failed to play audio');
      });
    }
  };

  // Format time helper
  const formatTime = (seconds: number): string => {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Progress bar click handler
  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>): void => {
    if (!audioRef.current || !progressBarRef.current) return;

    const rect = progressBarRef.current.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;

    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  // Progress bar drag handler
  const handleProgressMouseDown = (e: React.MouseEvent<HTMLDivElement>): void => {
    setIsDragging(true);
    handleProgressClick(e);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent): void => {
      if (isDragging && progressBarRef.current && audioRef.current) {
        const rect = progressBarRef.current.getBoundingClientRect();
        const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const newTime = percent * duration;
        audioRef.current.currentTime = newTime;
        setCurrentTime(newTime);
      }
    };

    const handleMouseUp = (): void => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, duration]);

  // Volume control handlers
  const handleVolumeClick = (e: React.MouseEvent<HTMLDivElement>): void => {
    if (!volumeBarRef.current) return;

    const rect = volumeBarRef.current.getBoundingClientRect();
    const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    
    setVolume(percent);
    setIsMuted(percent === 0);
    if (audioRef.current) {
      audioRef.current.volume = percent;
      audioRef.current.muted = percent === 0;
    }
  };

  const handleVolumeMouseDown = (e: React.MouseEvent<HTMLDivElement>): void => {
    setIsVolumeDragging(true);
    handleVolumeClick(e);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent): void => {
      if (isVolumeDragging && volumeBarRef.current && audioRef.current) {
        const rect = volumeBarRef.current.getBoundingClientRect();
        const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        setVolume(percent);
        setIsMuted(percent === 0);
        audioRef.current.volume = percent;
        audioRef.current.muted = percent === 0;
      }
    };

    const handleMouseUp = (): void => {
      setIsVolumeDragging(false);
    };

    if (isVolumeDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isVolumeDragging]);

  // Toggle mute
  const toggleMute = (): void => {
    if (!audioRef.current) return;
    
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    audioRef.current.muted = newMuted;
  };

  // Calculate progress percentage
  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;
  const volumePercent = volume * 100;

  if (loading) {
    return (
      <div className="audio-player-loading">
        <div className="audio-player-spinner"></div>
        <span>Loading audio...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="audio-player-error">
        <svg className="audio-player-error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" strokeWidth="2"/>
          <line x1="12" y1="8" x2="12" y2="12" strokeWidth="2"/>
          <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth="2"/>
        </svg>
        <span>{error}</span>
      </div>
    );
  }

  if (!audioUrl) {
    return null;
  }

  return (
    <div className="custom-audio-player">
      <div className="audio-player-main">
        {/* Play/Pause Button */}
        <button
          className="audio-player-play-btn"
          onClick={togglePlayPause}
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <svg viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="4" width="4" height="16" rx="1"/>
              <rect x="14" y="4" width="4" height="16" rx="1"/>
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
          )}
        </button>

        {/* Time Display */}
        <div className="audio-player-time">
          <span className="audio-player-time-current">{formatTime(currentTime)}</span>
          <span className="audio-player-time-separator">/</span>
          <span className="audio-player-time-total">{formatTime(duration)}</span>
        </div>

        {/* Progress Bar */}
        <div
          className="audio-player-progress-container"
          ref={progressBarRef}
          onClick={handleProgressClick}
          onMouseDown={handleProgressMouseDown}
        >
          <div className="audio-player-progress-track">
            <div
              className="audio-player-progress-fill"
              style={{ width: `${progressPercent}%` }}
            >
              <div className="audio-player-progress-handle"></div>
            </div>
          </div>
        </div>

        {/* Volume Control */}
        <div className="audio-player-volume">
          <button
            className="audio-player-volume-btn"
            onClick={toggleMute}
            aria-label={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted || volume === 0 ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 5L6 9H2v6h4l5 4V5z"/>
                <line x1="23" y1="9" x2="17" y2="15"/>
                <line x1="17" y1="9" x2="23" y2="15"/>
              </svg>
            ) : volume < 0.5 ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 5L6 9H2v6h4l5 4V5z"/>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 5L6 9H2v6h4l5 4V5z"/>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
                <path d="M12 2a10 10 0 0 1 0 20"/>
              </svg>
            )}
          </button>
          
          <div
            className="audio-player-volume-container"
            ref={volumeBarRef}
            onClick={handleVolumeClick}
            onMouseDown={handleVolumeMouseDown}
          >
            <div className="audio-player-volume-track">
              <div
                className="audio-player-volume-fill"
                style={{ width: `${volumePercent}%` }}
              >
                <div className="audio-player-volume-handle"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioPlayer;
