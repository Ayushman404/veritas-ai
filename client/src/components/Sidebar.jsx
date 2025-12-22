import React from 'react';

const Sidebar = ({ url, setUrl, handleIngest, isTraining, statusMsg }) => {
  return (
    <aside className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.5px' }}>
          VERITAS <span style={{ color: 'var(--accent-primary)' }}>.AI</span>
        </h1>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Research Agent v2.0</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <label style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
          Knowledge Base
        </label>
        
        <input 
          placeholder="https://example.com" 
          value={url} 
          onChange={(e) => setUrl(e.target.value)}
          style={{ padding: '12px', width: '100%', boxSizing: 'border-box' }}
        />
        
        <button className="glow-btn" onClick={handleIngest} disabled={isTraining}>
          {isTraining ? 'Ingesting...' : 'Add Source'}
        </button>

        {statusMsg && (
          <div style={{ 
            marginTop: '10px', 
            padding: '10px', 
            background: 'var(--glass)', 
            borderRadius: '6px',
            fontSize: '0.8rem',
            borderLeft: '2px solid var(--accent-primary)'
          }}>
            {statusMsg}
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;