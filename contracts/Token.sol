// SPDX-License-Identifier: MIT

pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract Token is ERC20, Ownable {
    ///////////////////
    // Errors /////////
    ///////////////////
    error Token__TokenIsNotOfExchangeableType();
    error Token__TokenIsNotOfExtendibleType();
    error Token__InputParameterIsZero();

    enum Redemption {
        REDEEMABLE,
        EXTENDIBLE,
        EXCHANGEABLE,
        PERPETUAL,
        REDEEMABLE_EXTENDIBLE,
        REDEEMABLE_EXCHANGEABLE,
        REDEEMABLE_EXCHANGEABLE_EXTENDIBLE
    }

    Redemption public redemptionState;
    uint256 public buybackDate;
    address[] public authorizedExchangeableTokens;
    mapping(address => uint256) public conversionRate;

    ///////////////////
    // Modifiers //////
    ///////////////////
    modifier isExchangeable() {
        if (redemptionState != Redemption.EXCHANGEABLE && redemptionState != Redemption.REDEEMABLE_EXCHANGEABLE && redemptionState != Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE) {
            revert Token__TokenIsNotOfExchangeableType();
        }
        _;
    }

    modifier isExtendible(){
        if (redemptionState != Redemption.EXTENDIBLE && redemptionState != Redemption.REDEEMABLE_EXTENDIBLE && redemptionState != Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE){
            revert Token__TokenIsNotOfExtendibleType();
        }
        _;
    }

    modifier isNonZero(uint256 _input){
        if(_input == 0){
            revert Token__InputParameterIsZero();
        }
        _;
    }

    constructor(string memory _name, string memory _symbol, uint256 _initialSupply, Redemption _redemptionState, uint256 _buybackDate) ERC20 (_name, _symbol) {
        _mint(address(this), _initialSupply);
        redemptionState = _redemptionState;
        if (_redemptionState != Redemption.EXCHANGEABLE && _redemptionState != Redemption.PERPETUAL)
        {
            require(_buybackDate > block.timestamp, 'Buyback date should be greater than current time');
            buybackDate = _buybackDate;
        }
    }

    function addExchangeableToken (address _token, uint256 _conversionRate) public onlyOwner isExchangeable {
        // require(redemptionState == Redemption.EXCHANGEABLE || redemptionState == Redemption.REDEEMABLE_EXCHANGEABLE || redemptionState == Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE, 'This token is not authorized for exchangeable operation');
        require(conversionRate[_token] == 0, 'This token has already been added');
        require(_token != address(0), 'Token address cannot be null');
        require(_conversionRate > 0, 'Conversion rate cannot be zero or less than zero');
        authorizedExchangeableTokens.push(_token);
        conversionRate[_token] = _conversionRate;
    }

    function extendBuybackDate(uint256 _buybackDate) public onlyOwner isExtendible isNonZero(_buybackDate) {
        require(_buybackDate > block.timestamp, 'Buyback date should be greater than current time');
        buybackDate = _buybackDate;
    }

}