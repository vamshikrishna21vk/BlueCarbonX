# BlueCarbonX

BlueCarbonX is a combined climate-tech repository that brings together a backend API, blockchain minting logic, a Streamlit marketplace frontend, a React demo application, and a local demo implementation all in one place.

## Project Purpose

BlueCarbonX is designed to demonstrate how restoration projects can be uploaded, tokenized, and traded using a combination of web apps, blockchain contracts, and marketplace logic. It includes:

- A backend API for project creation, minting, marketplace actions, and dashboard data.
- A Streamlit frontend for interactive project upload, analysis, marketplace trading, and wallet lookup.
- A React demo app showcasing a web-based UI for project interaction.
- A local Streamlit demo for fast experimentation without blockchain integration.
- Smart-contract minting logic that connects to ERC20 and ERC721 contracts.

## Repository Structure

```
bluecarbon-backend/         # Root repository and backend API server
  app.js / index.js         # Node.js/Express backend server
  mint.js                   # Blockchain minting router and contract interaction
  package.json              # Backend dependencies and scripts
  .gitignore                # Recommended files to ignore
  uploads/                  # Local file uploads for demo
  bluecarbon.db             # Demo database file
  frontend/                 # Streamlit frontend app for the marketplace
  demo/                     # React demo application built with Create React App
  streamlit/                # Local offline Streamlit demo app
```

## What Each Folder Contains

### `bluecarbon-backend`

This is the main API and minting backend.

- `index.js` runs an Express server on `http://localhost:3001`
- `mint.js` performs blockchain token and certificate minting via ethers.js
- API routes include project creation, project listing, minting, stats, map, and marketplace actions
- It uses a demo in-memory project store for project lifecycle management

### `bluecarbon-backend/frontend`

This folder contains the primary Streamlit app for BlueCarbonX.

- A user-facing dashboard with pages for Upload, Dashboard, Projects, Marketplace, Map, Analyze, and Wallet
- Connects to the backend API at `http://localhost:3001/api`
- Generates restoration certificate images and simulates wallets and marketplace operations
- Uses `requests`, `pandas`, `plotly`, `pydeck`, and Streamlit for UI and analytics

### `bluecarbon-backend/demo`

This is a React demo app built with Create React App.

- Provides a browser-based interface for demonstrating the product concept
- Includes standard CRA scripts: `npm start`, `npm build`, `npm test`

### `bluecarbon-backend/streamlit`

A lightweight local Streamlit demo app.

- Simulates project upload, analysis, minting, marketplace buy/retire, and dashboard flows entirely in-memory
- Uses local session state rather than an external API
- Useful for quick demoing and prototypes without blockchain setup

## Key Features

- Climate restoration project onboarding
- Token issuance and token balance tracking
- NFT certificate creation and certificate lookups
- Marketplace buy, sell, and retire operations
- Visual dashboards and geographic mapping of projects
- Multiple frontends for different demonstration scenarios

## How To Run the Project

### 1. Start the Backend API

```bash
cd bluecarbon-backend
npm install
node index.js
```

The API server should start at `http://localhost:3001`.

### 2. Run the Streamlit Frontend App

```bash
cd bluecarbon-backend/frontend
pip install -r requirements.txt   # if requirements file exists or install dependencies manually
streamlit run app.py
```

Open the browser URL shown by Streamlit and use the app to upload projects, mint tokens, and explore the marketplace.

### 3. Run the React Demo App

```bash
cd bluecarbon-backend/demo
npm install
npm start
```

This opens the React demo in a browser on `http://localhost:3000` by default.

### 4. Run the Local Streamlit Demo App

```bash
cd bluecarbon-backend/streamlit
pip install -r requirements.txt   # or install Streamlit, Pillow, pandas
streamlit run app.py
```

This demo lets you explore a full project lifecycle without external blockchain services.

## Environment Variables

The minting backend (`bluecarbon-backend/mint.js`) requires a `.env` file with the following values:

```ini
RPC_URL=https://your-ethereum-rpc-provider
PRIVATE_KEY=your-wallet-private-key
TOKEN_ADDRESS=deployed-token-contract-address
CERT_ADDRESS=deployed-certificate-contract-address
```

> Keep these values private. Do not commit `.env` or local private keys into the repository.

## Recommended Workflow

1. Start the backend server.
2. Launch the primary Streamlit frontend in `frontend/`.
3. Use the app to upload a restoration project and mint tokens.
4. Use the `Marketplace` and `Wallet` pages to interact with tokens and certificates.
5. Optionally run the React demo app to explore the UI concept.

## Notes and Best Practices

- `node_modules/`, `.venv/`, `.env`, `uploads/`, and generated artifact folders should be ignored by Git.
- The backend demo currently uses an in-memory project list, so server restarts will clear project state unless you migrate to persistent storage.
- The `bluecarbon-backend/frontend` app assumes the backend API is running at `http://localhost:3001`.
- The `mint.js` router is the bridge between the API and blockchain minting contracts.

## Project Vision

BlueCarbonX is a climate restoration tokenization platform concept. It combines project data, token economics, NFT certificates, and marketplace interactions into one unified demo repository. This repo shows how restoration projects can be represented as digital assets and how stakeholders can track, trade, and retire those assets in a web-enabled workflow.

---

If you want, I can also add a shorter `README` for the `frontend/`, `demo/`, and `streamlit/` subfolders to make each component easier to use independently.
