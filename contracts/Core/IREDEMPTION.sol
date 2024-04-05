// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

interface IREDEMPTION {
    function getMaturityDate() external view returns (uint256);
    function redeemToken(uint256 _amount) external;
    function extendMaturityDate(uint256 _maturityDate) external;
    function exchangeToken(address _exchangeToken, uint256 _amount) external;
    function addExchangeableToken(
        address _token,
        uint256 _conversionRate
    ) external;
}
