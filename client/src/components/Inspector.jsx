import React from 'react';

const Inspector = ({ evidence }) => {
  return (
    <aside className="glass-panel" style={{ borderRight: 'none', borderLeft: '1px solid var(--border-color)' }}>
      <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)' }}>
        <h3 style={{ margin: 0, fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
          Evidence
        </h3>
      </div>
      
      <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
        {evidence.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center', marginTop: '50px' }}>
            No active context.<br/>Ask a question to retrieve data.
          </p>
        ) : (
          evidence.map((text, index) => (
            <div key={index} style={{ 
              background: 'var(--bg-card)', 
              padding: '15px', 
              borderRadius: '8px', 
              marginBottom: '15px', 
              border: '1px solid var(--border-color)',
              fontSize: '0.85rem',
              lineHeight: '1.5',
              color: '#ccc'
            }}>
              <div style={{ 
                color: 'var(--accent-primary)', 
                fontSize: '0.7rem', 
                fontWeight: 700, 
                marginBottom: '8px',
                textTransform: 'uppercase' 
              }}>
                Source Chunk {index + 1}
              </div>
              {text}
            </div>
          ))
        )}
      </div>
    </aside>
  );
};

export default Inspector;