import React, { useState, useRef } from 'react';
import { api } from '../api';
export default function Analyze() {
  const [dragging, setDragging]   = useState(false);
  const [image, setImage]         = useState(null);
  const [preview, setPreview]     = useState(null);
  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState(null);
  const [cameraId, setCameraId]   = useState('CAM-001');
  const [location, setLocation]   = useState('MG Road, Bengaluru');
  const [stopLine, setStopLine]   = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const fileRef = useRef();
  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please upload a valid image file.');
      return;
    }
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };
  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };
  const handleAnalyze = async () => {
    if (!image) return;
    setLoading(true);
    setError(null);
    setStatusMsg('Submitting image to server...');
    try {
      const formData = new FormData();
      formData.append('file', image);
      formData.append('camera_id', cameraId);
      formData.append('location', location);
      formData.append('has_stop_line', stopLine);
      setStatusMsg('Running YOLOv8 inference... this may take 30-60s on first request');
      const data = await api.analyzeImage(formData);
      if (data.detail) {
        setError(`Server error: ${data.detail}`);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
      setStatusMsg('');
    }
  };
  const severityColor = {
    CRITICAL: '#ef4444', HIGH: '#f97316',
    MEDIUM: '#eab308', LOW: '#22c55e'
  };
  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">Analyze Image</div>
          <div className="page-subtitle">Upload a traffic image to detect violations</div>
        </div>
      </div>
      <div style={{ background: '#1a1d27', border: '1px solid #f97316', borderRadius: 8, padding: '12px 16px', marginBottom: 24, fontSize: 13, color: '#f97316' }}>
        ⚡ Note: First analysis request may take 30-60 seconds as the AI model loads on the server.
      </div>
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title">Camera Settings</div>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <div>
            <label style={{ fontSize: 12, color: '#64748b', display: 'block', marginBottom: 6 }}>Camera ID</label>
            <select
              value={cameraId}
              onChange={e => setCameraId(e.target.value)}
              style={{ background: '#151720', border: '1px solid #2d3148', borderRadius: 8, padding: '8px 12px', color: '#e2e8f0', fontSize: 14 }}
            >
              {['CAM-001','CAM-002','CAM-003','CAM-004','CAM-005'].map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#64748b', display: 'block', marginBottom: 6 }}>Location</label>
            <select
              value={location}
              onChange={e => setLocation(e.target.value)}
              style={{ background: '#151720', border: '1px solid #2d3148', borderRadius: 8, padding: '8px 12px', color: '#e2e8f0', fontSize: 14 }}
            >
              {[
                'MG Road, Bengaluru',
                'Silk Board Junction, Bengaluru',
                'Hebbal Flyover, Bengaluru',
                'Whitefield Main Road, Bengaluru',
                'Koramangala 5th Block, Bengaluru',
              ].map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8 }}>
            <input
              type="checkbox"
              id="stopline"
              checked={stopLine}
              onChange={e => setStopLine(e.target.checked)}
              style={{ width: 16, height: 16 }}
            />
            <label htmlFor="stopline" style={{ fontSize: 14, color: '#94a3b8' }}>Has Stop Line</label>
          </div>
        </div>
      </div>
      <div
        className={`upload-area ${dragging ? 'dragging' : ''}`}
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileRef.current.click()}
      >
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={e => handleFile(e.target.files[0])}
        />
        {preview ? (
          <img src={preview} alt="preview" style={{ maxHeight: 200, borderRadius: 8, marginBottom: 12 }} />
        ) : (
          <div className="upload-icon">📷</div>
        )}
        <div className="upload-text">
          {preview ? image.name : 'Drop a traffic image here or click to upload'}
        </div>
        <div className="upload-sub">Supports JPG, PNG, WEBP</div>
      </div>
      {error && (
        <div style={{ background: '#450a0a', border: '1px solid #ef4444', borderRadius: 8, padding: '12px 16px', marginTop: 16, color: '#ef4444', fontSize: 14 }}>
          {error}
        </div>
      )}
      {image && (
        <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading}>
            {loading ? 'Analyzing...' : 'Run Analysis'}
          </button>
          <button className="btn btn-secondary" onClick={() => { setImage(null); setPreview(null); setResult(null); setError(null); }}>
            Clear
          </button>
        </div>
      )}
      {loading && (
        <div className="loading" style={{ marginTop: 24 }}>
          <div className="spinner" />
          {statusMsg || 'Running AI analysis — YOLOv8 detecting violations...'}
        </div>
      )}
      {result && (
        <div className="result-panel" style={{ marginTop: 24 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #2d3148', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 600, color: '#f1f5f9' }}>
              Analysis Result — Incident: {result.incident_id}
            </span>
            <span className={`badge ${result.violation_count > 0 ? 'badge-HIGH' : 'badge-LOW'}`}>
              {result.violation_count} Violation{result.violation_count !== 1 ? 's' : ''} Found
            </span>
          </div>
          {result.annotated_image_b64 && (
            <img
              src={`data:image/jpeg;base64,${result.annotated_image_b64}`}
              alt="annotated"
              className="result-image"
            />
          )}
          <div className="violation-list">
            {result.violation_count === 0 ? (
              <div className="empty">
                <div className="empty-icon">✅</div>
                <div>No violations detected in this image</div>
              </div>
            ) : (
              result.metadata.violations.map((v, i) => (
                <div key={i} className="violation-item" style={{ borderLeftColor: severityColor[v.severity] }}>
                  <div>
                    <div style={{ fontWeight: 600, color: '#f1f5f9', marginBottom: 4 }}>{v.violation_label}</div>
                    <div style={{ fontSize: 12, color: '#64748b' }}>
                      Confidence: {(v.confidence * 100).toFixed(1)}%
                      {v.license_plate && ` • Plate: ${v.license_plate}`}
                      {v.notes && ` • ${v.notes}`}
                    </div>
                  </div>
                  <span className={`badge badge-${v.severity}`}>{v.severity}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
