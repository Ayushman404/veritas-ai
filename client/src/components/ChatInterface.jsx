import React, { useRef, useEffect } from 'react';

const ChatInterface = ({ chatHistory, query, setQuery, handleAsk, isSearching }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isSearching]);

  return (
    <section style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'var(--bg-dark)' }}>
      
      {/* Messages Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '30px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {chatHistory.length === 0 && (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#333' }}>
            <h2>Ready to research.</h2>
          </div>
        )}

        {chatHistory.map((msg, idx) => (
          <div key={idx} style={{ 
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '75%' 
          }}>
            <div style={{ 
              padding: '15px 20px', 
              borderRadius: '12px',
              background: msg.role === 'user' ? 'var(--accent-primary)' : 'var(--bg-card)',
              border: msg.role === 'ai' ? '1px solid var(--border-color)' : 'none',
              lineHeight: '1.6',
              fontSize: '0.95rem'
            }}>
              {msg.role === 'ai' && <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '5px' }}>VERITAS</div>}
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
            </div>
          </div>
        ))}

        {isSearching && (
          <div style={{ alignSelf: 'flex-start', padding: '15px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            Thinking...
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Bar */}
      <div style={{ padding: '20px', borderTop: '1px solid var(--border-color)', background: 'var(--bg-panel)' }}>
        <div style={{ display: 'flex', gap: '10px', maxWidth: '900px', margin: '0 auto' }}>
          <input 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
            placeholder="Ask a complex question..."
            style={{ flex: 1, padding: '15px', background: 'var(--bg-dark)' }}
            disabled={isSearching}
          />
          <button className="glow-btn" onClick={handleAsk} disabled={isSearching} style={{ width: '100px' }}>
            Send
          </button>
        </div>
      </div>

    </section>
  );
};

export default ChatInterface;