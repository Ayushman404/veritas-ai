import { useState } from 'react';
import axios from 'axios';
import './styles/global.css';

// Components
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import Inspector from './components/Inspector';

const API_URL = 'http://localhost:5000/api';

function App() {
  // --- STATE ---
  const [url, setUrl] = useState('');
  const [query, setQuery] = useState('');
  const [isTraining, setIsTraining] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [statusMsg, setStatusMsg] = useState('');

  // --- HANDLERS ---
  const handleIngest = async () => {
    if (!url) return;
    setIsTraining(true);
    setStatusMsg("Vectorizing content...");
    try {
      const res = await axios.post(`${API_URL}/ingest`, { url });
      setStatusMsg(`Success: Ingested ${res.data.chunks_stored} chunks.`);
      setUrl('');
    } catch (err) {
      setStatusMsg("Error: Failed to ingest.");
    } finally {
      setIsTraining(false);
    }
  };

  const handleAsk = async () => {
    if (!query) return;
    const currentQ = query;
    setQuery('');
    setIsSearching(true);

    // Optimistic Update
    setChatHistory(prev => [...prev, { role: 'user', content: currentQ }]);

    // Prepare History format for Backend
    const historyPairs = [];
    for (let i = 0; i < chatHistory.length; i += 2) {
      if (chatHistory[i+1]) {
        historyPairs.push([chatHistory[i].content, chatHistory[i+1].content]);
      }
    }

    try {
      const res = await axios.post(`${API_URL}/ask`, { 
        query: currentQ, 
        chat_history: historyPairs 
      });

      setChatHistory(prev => [...prev, { role: 'ai', content: res.data.answer }]);
      setEvidence(res.data.evidence);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'ai', content: "Error: Could not retrieve answer." }]);
    } finally {
      setIsSearching(false);
    }
  };

  // --- RENDER ---
  return (
    <div className="app-layout">
      
      <Sidebar 
        url={url} 
        setUrl={setUrl} 
        handleIngest={handleIngest} 
        isTraining={isTraining} 
        statusMsg={statusMsg} 
      />
      
      <ChatInterface 
        chatHistory={chatHistory} 
        query={query} 
        setQuery={setQuery} 
        handleAsk={handleAsk} 
        isSearching={isSearching} 
      />
      
      <Inspector 
        evidence={evidence} 
      />

    </div>
  );
}

export default App;