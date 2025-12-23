import { useState } from 'react';
import axios from 'axios';
import './styles/global.css';

// Components
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import Inspector from './components/Inspector';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [url, setUrl] = useState('');
  const [query, setQuery] = useState('');
  const [isTraining, setIsTraining] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [statusMsg, setStatusMsg] = useState('');

  // --- HANDLER 1: URL INGESTION (Refactored for Form Data) ---
  const handleUrlIngest = async () => {
    if (!url) return;
    setIsTraining(true);
    setStatusMsg("Crawling & Vectorizing...");

    try {
      // Backend expects Form Data now, not JSON!
      const formData = new FormData();
      formData.append('url', url);

      const res = await axios.post(`${API_URL}/ingest/url`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' } // Optional but good practice
      });
      
      setStatusMsg(`Success: Read ${res.data.chunks_stored} chunks from URL.`);
      setUrl('');
    } catch (err) {
      console.error(err);
      setStatusMsg("Error: Failed to process URL.");
    } finally {
      setIsTraining(false);
    }
  };

  // --- HANDLER 2: PDF INGESTION (NEW) ---
  const handlePdfIngest = async (files) => {
    if (!files || files.length === 0) return;
    setIsTraining(true);
    setStatusMsg(`Uploading ${files.length} document(s)...`);

    try {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }

      // FIX: Do NOT set Content-Type header manually. 
      // Axios detects FormData and sets it + the boundary automatically.
      const res = await axios.post(`${API_URL}/ingest/pdf`, formData);

      setStatusMsg(` Success: Extracted ${res.data.chunks_stored} chunks from PDF(s).`);
    } catch (err) {
      console.error(err);
      setStatusMsg(" Error: Failed to process PDF.");
    } finally {
      setIsTraining(false);
    }
  };

  const handleAsk = async () => {
    if (!query) return;
    const currentQ = query;
    setQuery('');
    setIsSearching(true);
    setChatHistory(prev => [...prev, { role: 'user', content: currentQ }]);

    // Format history for backend
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
      setChatHistory(prev => [...prev, { role: 'ai', content: "⚠️ Error: The Agent is unresponsive." }]);
    } finally {
      setIsSearching(false);
    }
  };

  // --- HANDLER 3: RESET BRAIN ---
  const handleReset = async () => {
    if (!window.confirm("Are you sure? This will delete all ingested knowledge.")) return;
    
    setIsTraining(true);
    setStatusMsg("Purging memory...");
    
    try {
      await axios.delete(`${API_URL}/reset`);
      setStatusMsg("✅ System Reset. Brain is empty.");
      setChatHistory([]); // Also clear the chat UI
      setEvidence([]);
    } catch (err) {
      console.error(err);
      setStatusMsg("❌ Error: Failed to reset.");
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar 
        url={url} 
        setUrl={setUrl} 
        handleUrlIngest={handleUrlIngest} 
        handlePdfIngest={handlePdfIngest}
        handleReset={handleReset}
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
      
      <Inspector evidence={evidence} />
    </div>
  );
}

export default App;