// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IIdentityRegistry} from "@T-REX/contracts/registry/interface/IIdentityRegistry.sol";
import {Asset} from "./Asset.sol";

contract Token is Ownable {
    ///////////////////
    // Errors /////////
    ///////////////////
    error Token__TokenIsNotOfExchangeableType();
    error Token__TokenIsNotOfExtendibleType();
    error Token__TokenIsNotOfRedeemableType();
    error Token__InputParameterIsZero();
    error Token__ExchangeTokenIsNotAllowed();
    error Token__ExchangeFailed();
    error Token__InsufficientTokenBalance();
    error Token__InsufficientTokenAllowance();
    error Token__InvestorNotVerified();

    ///////////////////
    // Enums //////////
    ///////////////////
    enum Redemption {
        REDEEMABLE,
        EXTENDIBLE,
        EXCHANGEABLE,
        PERPETUAL,
        REDEEMABLE_EXTENDIBLE,
        REDEEMABLE_EXCHANGEABLE,
        REDEEMABLE_EXCHANGEABLE_EXTENDIBLE
    }

    ////////////////////
    // State Variables /
    ///////////////////
    Redemption public redemptionState;
    uint256 public buybackDate;
    address[] public authorizedExchangeableTokens;
    address public paymentToken;
    address public identityRegistry;
    uint256 public price;
    Asset private asset;

    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(address => uint256) public conversionRate;

    ///////////////////
    // Modifiers //////
    ///////////////////
    modifier isExchangeable() {
        if (
            redemptionState != Redemption.EXCHANGEABLE &&
            redemptionState != Redemption.REDEEMABLE_EXCHANGEABLE &&
            redemptionState != Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE
        ) {
            revert Token__TokenIsNotOfExchangeableType();
        }
        _;
    }

    modifier isExtendible() {
        if (
            redemptionState != Redemption.EXTENDIBLE &&
            redemptionState != Redemption.REDEEMABLE_EXTENDIBLE &&
            redemptionState != Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE
        ) {
            revert Token__TokenIsNotOfExtendibleType();
        }
        _;
    }

    modifier isRedeemable() {
        if (
            redemptionState != Redemption.REDEEMABLE &&
            redemptionState != Redemption.REDEEMABLE_EXTENDIBLE &&
            redemptionState != Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE
        ) {
            revert Token__TokenIsNotOfRedeemableType();
        }
        _;
    }

    modifier isNonZero(uint256 _input) {
        if (_input == 0) {
            revert Token__InputParameterIsZero();
        }
        _;
    }

    modifier isAllowedExchangeToken(address _exchangeToken) {
        if (conversionRate[_exchangeToken] == 0) {
            revert Token__ExchangeTokenIsNotAllowed();
        }
        _;
    }

    modifier hasSufficientBalance(uint256 _amount, address _sender) {
        if (_amount > asset.balanceOf(_sender)) {
            revert Token__InsufficientTokenBalance();
        }
        _;
    }

    modifier hasSufficientAllowance(uint256 _amount, address _sender) {
        if (_amount > asset.allowance(msg.sender, address(this))) {
            revert Token__InsufficientTokenAllowance();
        }
        _;
    }

    event Sender(address Sender);
    modifier isVerified() {
        if (!IIdentityRegistry(identityRegistry).isVerified(msg.sender)) {
            emit Sender(msg.sender);
            revert Token__InvestorNotVerified();
        }
        _;
    }

    ///////////////////
    // Functions //////
    ///////////////////
    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _initialSupply,
        Redemption _redemptionState,
        uint256 _buybackDate,
        address _paymentToken,
        address _identityRegistry,
        uint256 _price
    ) {
        // _mint(address(this), _initialSupply);
        asset = new Asset(_initialSupply, _name, _symbol);
        redemptionState = _redemptionState;
        paymentToken = _paymentToken;
        identityRegistry = _identityRegistry;
        price = _price;
        if (
            _redemptionState != Redemption.EXCHANGEABLE &&
            _redemptionState != Redemption.PERPETUAL
        ) {
            require(
                _buybackDate > block.timestamp,
                "Buyback date should be greater than current time"
            );
            buybackDate = _buybackDate;
        }
    }

    function addExchangeableToken(
        address _token,
        uint256 _conversionRate
    ) public onlyOwner isExchangeable {
        // require(redemptionState == Redemption.EXCHANGEABLE || redemptionState == Redemption.REDEEMABLE_EXCHANGEABLE || redemptionState == Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE, 'This token is not authorized for exchangeable operation');
        require(
            conversionRate[_token] == 0,
            "This token has already been added"
        );
        require(_token != address(0), "Token address cannot be null");
        require(
            _conversionRate > 0,
            "Conversion rate cannot be zero or less than zero"
        );
        authorizedExchangeableTokens.push(_token);
        conversionRate[_token] = _conversionRate;
    }

    function issueToken(
        uint256 _amount,
        address _to
    ) public onlyOwner isNonZero(_amount) {
        asset.transfer(_to, _amount);
    }

    function exchangeToken(
        address _exchangeToken,
        uint256 _amount
    )
        public
        isVerified
        isExchangeable
        isAllowedExchangeToken(_exchangeToken)
        hasSufficientBalance(_amount, msg.sender)
        hasSufficientAllowance(_amount, msg.sender)
    {
        uint256 totalAmount = _amount * conversionRate[_exchangeToken];
        asset.transferFrom(msg.sender, address(this), _amount);
        bool success = IERC20(_exchangeToken).transfer(msg.sender, totalAmount);
        if (!success) {
            revert Token__ExchangeFailed();
        }
    }

    function extendBuybackDate(
        uint256 _buybackDate
    ) public onlyOwner isExtendible isNonZero(_buybackDate) {
        require(
            _buybackDate > block.timestamp,
            "Buyback date should be greater than current time"
        );
        buybackDate = _buybackDate;
    }

    function redeemToken(
        uint256 _amount
    )
        public
        isVerified
        isRedeemable
        isNonZero(_amount)
        hasSufficientBalance(_amount, msg.sender)
        hasSufficientAllowance(_amount, msg.sender)
    {
        require(
            buybackDate < block.timestamp,
            "Buyback date should be less than current time"
        );
        require(
            price * _amount <= IERC20(paymentToken).balanceOf(address(this)),
            "The smart contract does not have sufficient funds"
        );
        asset.transferFrom(msg.sender, address(this), _amount);
        bool success = IERC20(paymentToken).transfer(
            msg.sender,
            price * _amount
        );
        if (!success) {
            revert Token__ExchangeFailed();
        }
    }

    function getBalance(address _user) public view returns (uint256) {
        return asset.balanceOf(_user);
    }

    function getAddress() public view returns (address) {
        return address(asset);
    }
}
