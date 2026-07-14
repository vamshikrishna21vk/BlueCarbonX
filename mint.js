const express = require("express");
const { ethers } = require("ethers");
const path = require("path");
require("dotenv").config({ path: __dirname + "/.env" });

const router = express.Router();

// --- Load Environment ---
const RPC_URL = process.env.RPC_URL;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const TOKEN_ADDRESS = process.env.TOKEN_ADDRESS;
const CERT_ADDRESS = process.env.CERT_ADDRESS;

console.log("RPC_URL:", RPC_URL);
console.log("TOKEN_ADDRESS:", TOKEN_ADDRESS);
console.log("CERT_ADDRESS:", CERT_ADDRESS);

// --- Load ABIs from Hardhat Artifacts ---
const tokenABI = require(path.join(
    __dirname,
    "../bluecarbon-frontend/blockchain/artifacts/contracts/BlueCarbonToken.sol/BlueCarbonToken.json"
)).abi;

const certABI = require(path.join(
    __dirname,
    "../bluecarbon-frontend/blockchain/artifacts/contracts/RestorationCertificate.sol/RestorationCertificate.json"
)).abi;

// --- Setup Provider, Wallet, and Contracts ---
const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

const erc20 = new ethers.Contract(TOKEN_ADDRESS, tokenABI, wallet);
const erc721 = new ethers.Contract(CERT_ADDRESS, certABI, wallet);

// -------------------------------
// Helper Functions
// -------------------------------
async function mintTokens(to, amount) {
    const tx = await erc20.mint(to, amount);
    await tx.wait();
    console.log(`✅ Minted ${amount} BCT to ${to}`);
    return { ok: true, msg: `Minted ${amount} BCT to ${to}` };
}

async function mintCertificate(to, uri) {
    const tx = await erc721.safeMint(to, uri);
    const receipt = await tx.wait();

    // Try to extract tokenId from Transfer event
    const event = receipt.events?.find((e) => e.event === "Transfer");
    const tokenId = event?.args?.tokenId?.toString() || "0";

    console.log(`✅ NFT Certificate minted: ${tokenId}`);
    return { ok: true, certificateId: tokenId, to, uri };
}

async function getBalances(address) {
    const tokens = await erc20.balanceOf(address);
    const certCount = await erc721.balanceOf(address);

    const certificates = [];
    const count = certCount.toNumber();

    for (let i = 0; i < count; i++) {
        try {
            const tokenId = await erc721.tokenOfOwnerByIndex(address, i);
            const uri = await erc721.tokenURI(tokenId);
            certificates.push({
                tokenId: tokenId.toString(),
                uri,
                projectId: uri,
                title: "Restoration Project",
            });
        } catch (err) {
            console.error("Error fetching NFT:", err);
        }
    }

    return { tokens: tokens.toString(), certificates };
}

// -------------------------------
// API Routes
// -------------------------------

// Mint ERC20 Tokens
router.post("/tokens", async (req, res) => {
    try {
        const { to, amount } = req.body;
        const result = await mintTokens(to, amount);
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Mint ERC721 Certificate
router.post("/certificate", async (req, res) => {
    try {
        const { to, uri } = req.body;
        const result = await mintCertificate(to, uri);
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Get balances for a wallet
router.get("/balance/:addr", async (req, res) => {
    try {
        const result = await getBalances(req.params.addr);
        res.json({ ok: true, ...result });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
