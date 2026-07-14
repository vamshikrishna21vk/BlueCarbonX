// db.js using sqlite3
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

// Database file path
const dbPath = path.join(__dirname, "bluecarbon.db");

// Create and open database
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT,
    before_path TEXT,
    after_path TEXT,
    lat REAL,
    lng REAL,
    carbon REAL,
    wallet TEXT,
    status TEXT,
    cid TEXT,
    nft_id TEXT,
    tokens INTEGER,
    tokens_retired INTEGER DEFAULT 0,
    created_at INTEGER
  )`);
});

module.exports = db;

