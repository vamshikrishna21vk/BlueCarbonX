const { ethers } = require("hardhat");

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with:", deployer.address);

    // ERC20 Token
    const BCT = await ethers.getContractFactory("BlueCarbonToken");
    const bct = await BCT.deploy(1000000);
    await bct.deployed();
    console.log("✅ BlueCarbonToken deployed at:", bct.address);

    // ERC721 Certificate
    const RCERT = await ethers.getContractFactory("RestorationCertificate");
    const rcert = await RCERT.deploy();
    await rcert.deployed();
    console.log("✅ RestorationCertificate deployed at:", rcert.address);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
