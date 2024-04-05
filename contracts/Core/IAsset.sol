// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IAsset is IERC20 {
    function tokenHolderExists(
        address _tokenHolder
    ) external view returns (bool, uint256);

    function burn(address _account, uint256 _amount) external;

    function getTokenHolders() external view returns (address[] memory);
}
