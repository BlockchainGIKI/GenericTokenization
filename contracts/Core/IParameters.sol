// SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.17;

interface IParameters {
    function getPrice() external view returns (uint256);

    function getPrecision() external view returns (uint256);

    function getAssetAddress() external view returns (address);

    function getPaymentTokenAddress() external view returns (address);

    function getIdentityRegistryAddress() external view returns (address);
}
