// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IIdentityRegistry} from "@T-REX/contracts/registry/interface/IIdentityRegistry.sol";
import "./IParameters.sol";
import "./IAsset.sol";

contract REDEMPTION is Ownable {
    ///////////////////
    // Errors /////////
    ///////////////////
    error Token__TokenIsNotOfExchangeableType();
    error Token__TokenIsNotOfExtendibleType();
    error Token__TokenIsNotOfRedeemableType();
    error Equity__InputParameterIsZero();
    error Token__ExchangeTokenIsNotAllowed();
    error Equity__ExchangeFailed();
    error Token__InsufficientTokenBalance();
    error Token__InsufficientTokenAllowance();
    error Token__InvestorNotVerified();

    ///////////////////
    // Enums //////////
    ///////////////////
    enum Redemption {
        NONE,
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
    // Used to specify remdemption state of the token
    Redemption public redemptionState;
    // Used to specify buyback date of the token
    uint256 public buybackDate;
    // Used to specify the maturity date of the token
    uint256 public maturity;
    // Used to specify the call price of redeemable tokens
    uint256 public callPrice;
    // Used to maintain an array of authorized tokens that can exchanged or redeemed for this token
    address[] public authorizedExchangeableTokens;
    // Set to the address of the parameters contract
    address public param;

    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(address => uint256) public conversionRate;

    ///////////////////
    // Modifiers //////
    ///////////////////
    modifier isExchangeable() {
        if (
            (redemptionState != Redemption.EXCHANGEABLE &&
                redemptionState != Redemption.REDEEMABLE_EXCHANGEABLE &&
                redemptionState !=
                Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE)
        ) {
            revert Token__TokenIsNotOfExchangeableType();
        }
        _;
    }

    modifier isExtendible() {
        if (
            (redemptionState != Redemption.EXTENDIBLE &&
                redemptionState != Redemption.REDEEMABLE_EXTENDIBLE &&
                redemptionState !=
                Redemption.REDEEMABLE_EXCHANGEABLE_EXTENDIBLE)
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

    modifier risNonZero(uint256 _input) {
        if (_input == 0) {
            revert Equity__InputParameterIsZero();
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
        IAsset asset = IAsset(IParameters(param).getAssetAddress());
        if (_amount > asset.balanceOf(_sender)) {
            revert Token__InsufficientTokenBalance();
        }
        _;
    }

    modifier hasSufficientAllowance(uint256 _amount, address _sender) {
        IAsset asset = IAsset(IParameters(param).getAssetAddress());
        if (_amount > asset.allowance(msg.sender, address(this))) {
            revert Token__InsufficientTokenAllowance();
        }
        _;
    }

    modifier isVerified() {
        IIdentityRegistry identityRegistry = IIdentityRegistry(
            IParameters(param).getIdentityRegistryAddress()
        );
        if (!IIdentityRegistry(identityRegistry).isVerified(msg.sender)) {
            revert Token__InvestorNotVerified();
        }
        _;
    }

    ///////////////////
    // Functions //////
    ///////////////////
    constructor(
        Redemption _redemptionState,
        uint256 _buybackDate,
        uint256 _maturityDate,
        uint256 _callPrice,
        address _parameters
    ) {
        redemptionState = _redemptionState;
        param = _parameters;
        if ((_redemptionState != Redemption.PERPETUAL)) {
            require(
                _maturityDate > block.timestamp,
                "Maturity date should be greater than current time"
            );
            maturity = _maturityDate;
        }
        if (
            _redemptionState != Redemption.EXTENDIBLE &&
            _redemptionState != Redemption.EXCHANGEABLE &&
            _redemptionState != Redemption.PERPETUAL
        ) {
            require(
                _buybackDate > block.timestamp,
                "Buyback date should be greater than current time"
            );
            buybackDate = _buybackDate;
            callPrice = _callPrice;
        }
    }

    function addExchangeableToken(
        address _token,
        uint256 _conversionRate
    ) external onlyOwner isExchangeable {
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

    function exchangeToken(
        address _exchangeToken,
        uint256 _amount
    )
        external
        isVerified
        isExchangeable
        isAllowedExchangeToken(_exchangeToken)
        hasSufficientBalance(_amount, msg.sender)
        hasSufficientAllowance(_amount, msg.sender)
    {
        uint256 totalAmount = _amount * conversionRate[_exchangeToken];
        IAsset asset = IAsset(IParameters(param).getAssetAddress());
        asset.transferFrom(msg.sender, address(this), _amount);
        bool success = IERC20(_exchangeToken).transfer(msg.sender, totalAmount);
        if (!success) {
            revert Equity__ExchangeFailed();
        }
    }

    function extendMaturityDate(
        uint256 _maturityDate
    ) external onlyOwner isExtendible risNonZero(_maturityDate) {
        require(
            _maturityDate > block.timestamp,
            "Maturity date should be greater than current time"
        );
        maturity = _maturityDate;
    }

    function redeemToken(
        uint256 _amount
    )
        external
        isVerified
        isRedeemable
        risNonZero(_amount)
        hasSufficientBalance(_amount, msg.sender)
        hasSufficientAllowance(_amount, msg.sender)
    {
        require(
            block.timestamp >= buybackDate,
            "The token cannot be redeemed before the buyback date has passed!"
        );
        address paymentToken = IParameters(param).getPaymentTokenAddress();
        uint256 price = callPrice;
        require(
            price * _amount <= IERC20(paymentToken).balanceOf(address(this)),
            "The smart contract does not have sufficient funds"
        );
        IAsset asset = IAsset(IParameters(param).getAssetAddress());
        asset.transferFrom(msg.sender, address(this), _amount);
        bool success = IERC20(paymentToken).transfer(
            msg.sender,
            price * _amount
        );
        if (!success) {
            revert Equity__ExchangeFailed();
        }
    }

    function getMaturityDate() external view returns (uint256) {
        return maturity;
    }
}
