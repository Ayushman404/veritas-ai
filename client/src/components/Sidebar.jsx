import React, { useRef } from 'react';

const Sidebar = ({ url, setUrl, handleUrlIngest, handlePdfIngest, handleReset, isTraining, statusMsg }) => {
  const fileInputRef = useRef(null);

  const onFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handlePdfIngest(e.target.files);
    }
  };

  return (
    <aside className="glass-panel" style={{ padding: '24px', maxWidth: '300px' }}>
      <div style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.5px', margin: 0 }}>
          VERITAS <span style={{ color: 'var(--accent-primary)' }}>.AI</span>
        </h1>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '5px' }}>
          Modular Research Engine
        </p>
      </div>

      {/* URL SECTION */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '30px' }}>
        <label style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
          Web Source
        </label>
        
        <input 
          placeholder="https://wikipedia.org/..." 
          value={url} 
          onChange={(e) => setUrl(e.target.value)}
          style={{ padding: '12px', width: '100%', boxSizing: 'border-box' }}
        />
        
        <button className="glow-btn" onClick={handleUrlIngest} disabled={isTraining}>
          {isTraining ? 'Scanning Web...' : 'Ingest URL'}
        </button>
      </div>

      {/* PDF SECTION (NEW) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <label style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
          Document Source
        </label>
        
        {/* Hidden Input for aesthetics */}
        <input 
          type="file" 
          multiple 
          accept=".pdf" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={onFileChange}
        />
        
        <button 
          className="glow-btn" 
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', boxShadow: 'none' }}
          onClick={() => fileInputRef.current.click()} 
          disabled={isTraining}
        >
          {isTraining ? 'Uploading...' : '📁 Upload PDFs'}
        </button>
      </div>

      {/* STATUS MESSAGE */}
      {statusMsg && (
        <div style={{ 
          marginTop: '20px', 
          padding: '12px', 
          background: 'rgba(255,255,255,0.05)', 
          borderRadius: '8px',
          fontSize: '0.8rem',
          borderLeft: '3px solid var(--accent-primary)',
          animation: 'fadeIn 0.3s ease'
        }}>
          {statusMsg}
        </div>
      )}


      <hr style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: '20px 0' }} />

      {/* RESET BUTTON */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <button 
          className="glow-btn" 
          style={{ 
            background: 'transparent', 
            border: '1px solid #ef4444', 
            color: '#ef4444', 
            boxShadow: 'none' 
          }}
          onClick={handleReset}
        >
          🗑️ Clear Brain
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;