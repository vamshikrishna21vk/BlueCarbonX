const express = require("express");
const mintRoutes = require("./mint"); // router from mint.js

const app = express();
app.use(express.json());

// Mount mint router at /api/mint
app.use("/api/mint", mintRoutes);

// --- Project storage (in-memory for demo) ---
let projects = [];

// Create project
app.post("/api/projects", (req, res) => {
    const { title, carbon, lat, lng } = req.body;
    const id = "p_" + Date.now();
    const project = {
        id,
        title,
        carbon,
        lat,
        lng,
        status: "uploaded",
        tokens: 0,
        tokens_retired: 0,
        wallet: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8" // demo wallet
    };
    projects.push(project);
    res.json({ ok: true, id });
});

// List projects
app.get("/api/projects", (req, res) => {
    res.json(projects);
});

// Mint tokens + NFT for project (call mint endpoints indirectly)
const axios = require("axios");

app.post("/api/mint/:id", async (req, res) => {
    const project = projects.find(p => p.id === req.params.id);
    if (!project) return res.status(404).json({ error: "not found" });

    try {
        // Call mint APIs
        await axios.post("http://localhost:3001/api/mint/tokens", {
            to: project.wallet,
            amount: project.carbon
        });

        await axios.post("http://localhost:3001/api/mint/certificate", {
            to: project.wallet,
            uri: "ipfs://QmDemo"
        });

        project.status = "minted";
        project.tokens = project.carbon;

        res.json({ ok: true, msg: `Minted ${project.carbon} tokens + certificate for ${project.title}` });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Stats for dashboard
app.get("/api/stats", (req, res) => {
    const totalProjects = projects.length;
    const totalCarbon = projects.reduce((a, b) => a + b.carbon, 0);
    const totalTokens = projects.reduce((a, b) => a + (b.tokens || 0), 0);
    const totalRetired = projects.reduce((a, b) => a + (b.tokens_retired || 0), 0);

    const byStatus = {
        uploaded: projects.filter(p => p.status === "uploaded").length,
        minted: projects.filter(p => p.status === "minted").length
    };

    res.json({
        totalProjects,
        totalCarbon,
        totalTokens,
        totalRetired,
        tokenDistribution: projects.map(p => ({
            title: p.title,
            tokens: p.tokens,
            retired: p.tokens_retired
        })),
        byStatus
    });
});

// Map API
app.get("/api/map", (req, res) => {
    const features = projects
        .filter(p => p.lat && p.lng)
        .map(p => ({
            type: "Feature",
            geometry: { type: "Point", coordinates: [p.lng, p.lat] },
            properties: { title: p.title, carbon: p.carbon }
        }));
    res.json({ type: "FeatureCollection", features });
});

// Marketplace actions
// --- Marketplace actions ---
// Buy tokens
app.post("/api/marketplace/buy/:id", (req, res) => {
    const project = projects.find(p => p.id === req.params.id);
    if (!project) return res.status(404).json({ error: "not found" });

    const { amount } = req.body;
    if (amount > project.tokens) {
        return res.status(400).json({ error: "Not enough tokens available" });
    }

    project.tokens -= amount;
    res.json({ ok: true, msg: `Bought ${amount} tokens from ${project.title}` });
});

// Sell tokens (NEW)
app.post("/api/marketplace/sell/:id", (req, res) => {
    const project = projects.find(p => p.id === req.params.id);
    if (!project) return res.status(404).json({ error: "not found" });

    const { amount } = req.body;
    if (amount <= 0) {
        return res.status(400).json({ error: "Amount must be greater than 0" });
    }

    // For demo: selling just adds tokens back to the project pool
    project.tokens += amount;
    res.json({ ok: true, msg: `Sold ${amount} tokens back into ${project.title}` });
});

// Retire tokens
app.post("/api/marketplace/retire/:id", (req, res) => {
    const project = projects.find(p => p.id === req.params.id);
    if (!project) return res.status(404).json({ error: "not found" });

    const { amount } = req.body;
    if (amount > project.tokens) {
        return res.status(400).json({ error: "Not enough tokens to retire" });
    }

    project.tokens -= amount;
    project.tokens_retired += amount;
    res.json({ ok: true, msg: `Retired ${amount} tokens from ${project.title}` });
});


app.listen(3001, () => console.log("✅ Backend running at http://localhost:3001"));






// Sell tokens back to marketplace
app.post("/api/marketplace/sell/:id", (req, res) => {
    const project = projects.find(p => p.id === req.params.id);
    if (!project) return res.status(404).json({ error: "not found" });

    const { amount } = req.body;
    project.tokens += amount; // Increase available tokens
    res.json({ ok: true, msg: `Sold ${amount} tokens back to ${project.title}` });
});
