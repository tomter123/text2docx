import React, { useState } from 'react';
import axios from 'axios';

const FileConverter = () => {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState('');
  const [status, setStatus] = useState('');
  const [downloadUrl, setDownloadUrl] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleConvert = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/convert/file`,
        formData,
        {
          headers: {'Content-Type': 'multipart/form-data'}
        }
      );
      
      setJobId(response.data.job_id);
      setStatus('PROCESSING');
      setError('');
      pollStatus(response.data.job_id);
    } catch (err) {
      setError('Failed to start conversion');
    }
  };

  const pollStatus = (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/convert/${jobId}/status`
        );
        
        setStatus(response.data.status);
        
        if (response.data.status === 'SUCCESS') {
          clearInterval(interval);
          setDownloadUrl(
            `${import.meta.env.VITE_API_URL}/download?job_id=${jobId}`
          );
        } else if (response.data.status === 'FAILURE') {
          clearInterval(interval);
          setError('Conversion failed');
        }
      } catch (err) {
        clearInterval(interval);
        setError('Status check failed');
      }
    }, 2000);
  };

  return (
    <div className="converter-container">
      <h1>Text to DOCX Converter</h1>
      
      <div className="upload-section">
        <input type="file" onChange={handleFileChange} accept=".txt,.md,.html" />
        <button onClick={handleConvert} disabled={!file}>
          Convert to DOCX
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {jobId && (
        <div className="status-section">
          <h2>Conversion Status</h2>
          <p>Job ID: {jobId}</p>
          <p>Status: {status}</p>
          
          {downloadUrl && (
            <a href={downloadUrl} download="converted.docx">
              Download DOCX File
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default FileConverter;