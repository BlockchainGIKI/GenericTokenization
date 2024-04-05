// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import {IIdentityRegistry} from "@T-REX/contracts/registry/interface/IIdentityRegistry.sol";

contract Asset is ERC20, Ownable {
    IIdentityRegistry internal _tokenIdentityRegistry;
    // mapping(address => mapping(address => uint256)) internal _allowances;
    address[] private tokenHolders;

    constructor(
        uint256 _initialSupply,
        string memory _name,
        string memory _symbol,
        address _identityRegistry
    ) ERC20(_name, _symbol) {
        _tokenIdentityRegistry = IIdentityRegistry(_identityRegistry);
        _mint(msg.sender, _initialSupply);
    }

    function tokenHolderExists(
        address _tokenHolder
    ) public view returns (bool, uint256) {
        require(_tokenHolder != address(0), "Null address");
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (tokenHolders[i] == _tokenHolder) {
                return (true, i);
            }
        }
        return (false, 0);
    }

    function deleteTokenHolder(address _tokenHolder) internal {
        (bool exists, uint256 index) = tokenHolderExists(_tokenHolder);
        if (exists) {
            tokenHolders[index] = tokenHolders[tokenHolders.length - 1];
            tokenHolders.pop();
        }
    }

    function burn(address _account, uint256 _amount) external onlyOwner {
        _burn(_account, _amount);
        if (balanceOf(_account) == 0 && owner() != _account) {
            deleteTokenHolder(_account);
        }
    }

    function transfer(
        address _to,
        uint256 _amount
    ) public override returns (bool) {
        require(_amount <= balanceOf(msg.sender), "Insufficient Balance");
        if (_tokenIdentityRegistry.isVerified(_to)) {
            _transfer(msg.sender, _to, _amount);
            if (balanceOf(msg.sender) == 0 && owner() != msg.sender) {
                deleteTokenHolder(msg.sender);
            }
            (bool exists, ) = tokenHolderExists(_to);
            if (!exists) {
                tokenHolders.push(_to);
            }
            return true;
        }
        revert("Transfer not possible");
    }

    function transferFrom(
        address _from,
        address _to,
        uint256 _amount
    ) public override returns (bool) {
        require(_amount <= balanceOf(_from), "Insufficient Balance");
        if (_tokenIdentityRegistry.isVerified(_to)) {
            _spendAllowance(_from, msg.sender, _amount);
            _transfer(_from, _to, _amount);
            if (balanceOf(_from) == 0 && owner() != _from) {
                deleteTokenHolder(_from);
            }
            (bool exists, ) = tokenHolderExists(_to);
            if (!exists) {
                tokenHolders.push(_to);
            }
            return true;
        }
        revert("Transfer not possible");
    }

    function getTokenHolders()
        external
        view
        onlyOwner
        returns (address[] memory)
    {
        return tokenHolders;
    }
}
