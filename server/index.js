const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// The internal Docker URL for Python
const AI_URL = process.env.AI_SERVICE_URL || 'http://ai-engine:8000';

app.get('/', (req, res) => {
    res.send('Veritas Gateway is Online');
});

// --- PROXY ROUTE 1: INGEST ---
// Frontend sends URL -> Gateway -> Python scrapes & vectorizes
app.post('/api/ingest', async (req, res) => {
    try {
        console.log(`Gateway: Forwarding ingestion request for ${req.body.url}`);
        const response = await axios.post(`${AI_URL}/ingest`, req.body);
        res.json(response.data);
    } catch (error) {
        console.error("Ingest Error:", error.message);
        res.status(500).json({ error: "Failed to ingest data" });
    }
});

// --- PROXY ROUTE 2: ASK ---
// Frontend sends Question -> Gateway -> Python searches Vector DB
app.post('/api/ask', async (req, res) => {
    try {
        console.log(`Gateway: Forwarding query: ${req.body.query}`);
        const response = await axios.post(`${AI_URL}/ask`, req.body);
        res.json(response.data);
    } catch (error) {
        console.error("Ask Error:", error.message);
        res.status(500).json({ error: "Failed to get answer" });
    }
});

const PORT = 5000;
app.listen(PORT, () => console.log(`Gateway running on port ${PORT}`));