// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";

contract Parameters is Ownable {
    uint256 private PRICE;
    uint256 private PRECISION;
    address private ASSET_ADDRESS;
    address private PAYMENT_TOKEN_ADDRESS;
    address private IDENTITY_REGISTRY_ADDRESS;

    constructor(
        uint256 _price,
        uint256 _precision,
        address _asset,
        address _payment_token,
        address _identity_registry
    ) {
        PRICE = _price;
        PRECISION = _precision;
        ASSET_ADDRESS = _asset;
        PAYMENT_TOKEN_ADDRESS = _payment_token;
        IDENTITY_REGISTRY_ADDRESS = _identity_registry;
    }

    function getPrice() external view returns (uint256) {
        return PRICE;
    }

    function getPrecision() external view returns (uint256) {
        return PRECISION;
    }

    function getAssetAddress() external view returns (address) {
        return ASSET_ADDRESS;
    }

    function getPaymentTokenAddress() external view returns (address) {
        return PAYMENT_TOKEN_ADDRESS;
    }

    function getIdentityRegistryAddress() external view returns (address) {
        return IDENTITY_REGISTRY_ADDRESS;
    }
}
