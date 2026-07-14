// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract RestorationCertificate is ERC721URIStorage {
    uint256 private _nextId = 1;

    constructor() ERC721("Restoration Certificate", "RCERT") {}

    function mintCertificate(address to, string memory metadataURI) public returns (uint256) {
        uint256 tokenId = _nextId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI);
        return tokenId;
    }
}
