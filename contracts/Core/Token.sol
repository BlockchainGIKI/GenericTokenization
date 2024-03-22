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
    error Token__TokenIsNotOfPayableType();
    error Token__InterestRateIsNotOfVariableType();
    error Token__InterestTypeIsNotPaymentInKind();
    error Token__InterestTypeIsNotFixedOrVariableRate();
    error Token__InterestTypeIsNotCashPayment();
    error Token__InvestorDoesNotExist();

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

    enum PaymentFrequency {
        NONE,
        DAILY,
        WEEKLY,
        SEMIMONTHLY,
        MONTHLY,
        ANNUALY
    }

    enum InterestType {
        NONE,
        FIXED,
        ZERO,
        VARIABLE,
        CASH,
        PAYMENT_IN_KIND
    }

    ///////////////////
    // Struct /////////
    ///////////////////
    struct CashReceipt {
        uint256 receiptNumber;
        uint256 date;
        address tokenHolder;
        uint256 amount;
        bytes signature;
    }

    struct TokenOptions {
        Redemption _redemptionState;
        PaymentFrequency _paymentFrequency;
        InterestType _interestType;
    }

    ////////////////////
    // State Variables /
    ///////////////////

    // Used to specify remdemption state of the token
    Redemption public redemptionState;
    // Used to specify payment frequency of the token
    PaymentFrequency public paymentFrequency;
    // Used to specify type of interest rate of the token
    InterestType public interestType;
    // Used to specify maturity date of the token
    uint256 public maturityDate;
    // Set to the current block timestamp when the contract is deployed
    uint256 public contractDeploymentTime;
    // Used to maintain an array of authorized tokens that can exchanged or redeemed for this token
    address[] public authorizedExchangeableTokens;
    // Set to the address of the underlying payment currency during contract deployment
    address public paymentToken;
    // Set to the address of the identity registry during contract deployment
    address public identityRegistry;
    // Set to the exchange rate of the token to the payment currency during contract deployment
    uint256 public price;
    // The face value of the asset
    uint256 public faceValue;
    // Refers to the underlying token created during contract deployment
    Asset private asset;
    // Keeps track of the current payment period if the token grants the investors the right to receive periodic payments
    uint256 private paymentPeriod;
    // Refers to the interest rate of the token set during contract deployment. Can optionally be modified if interest rate type is variable
    uint256 public interestRate;
    ////////////////////
    // Constants ///////
    ///////////////////
    uint256 private constant AVERAGE_SECONDS_IN_A_DAY = 86400;
    uint256 private constant AVERAGE_SECONDS_IN_A_WEEK = 604800;
    uint256 private constant AVERAGE_SECONDS_IN_SEMI_MONTH = 1209600;
    uint256 private constant AVERAGE_SECONDS_IN_A_MONTH = 2628288;
    uint256 private constant AVERAGE_SECONDS_IN_A_YEAR = 31556952;
    uint256 private constant INTEREST_RATE_PRECISION = 1000;
    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(address => uint256) public conversionRate;
    mapping(PaymentFrequency => uint256) private paymentFrequencyToSeconds;
    mapping(address => mapping(uint256 => bool))
        public investorToPaymentPeriodToStatus;
    mapping(address => mapping(uint256 => CashReceipt))
        public investorToPaymentPeriodToReceipt;
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

    modifier isVerified() {
        if (!IIdentityRegistry(identityRegistry).isVerified(msg.sender)) {
            revert Token__InvestorNotVerified();
        }
        _;
    }

    modifier isPayable() {
        if (paymentFrequency == PaymentFrequency.NONE) {
            revert Token__TokenIsNotOfPayableType();
        }
        _;
    }

    modifier isVariable() {
        if (interestType != InterestType.VARIABLE) {
            revert Token__InterestRateIsNotOfVariableType();
        }
        _;
    }

    modifier isPaymentInKind() {
        if (interestType != InterestType.PAYMENT_IN_KIND) {
            revert Token__InterestTypeIsNotPaymentInKind();
        }
        _;
    }

    modifier isFixedOrVariableRate() {
        if (
            interestType != InterestType.FIXED &&
            interestType != InterestType.VARIABLE
        ) {
            revert Token__InterestTypeIsNotFixedOrVariableRate();
        }
        _;
    }

    modifier isCashPayment() {
        if (interestType != InterestType.CASH) {
            revert Token__InterestTypeIsNotCashPayment();
        }
        _;
    }

    modifier investorExists(address _investor) {
        (bool status, ) = asset.tokenHolderExists(_investor);
        if (!status) {
            revert Token__InvestorDoesNotExist();
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
        // Redemption _redemptionState,
        // PaymentFrequency _paymentFrequency,
        // InterestType _interestType,
        TokenOptions memory options,
        uint256 _maturityDate,
        address _paymentToken,
        address _identityRegistry,
        uint256 _price,
        uint256 _faceValue,
        uint256 _interestRate
    ) {
        // _mint(address(this), _initialSupply);
        asset = new Asset(_initialSupply, _name, _symbol, _identityRegistry);
        redemptionState = options._redemptionState;
        paymentFrequency = options._paymentFrequency;
        interestType = options._interestType;
        paymentToken = _paymentToken;
        identityRegistry = _identityRegistry;
        price = _price;
        faceValue = _faceValue;
        interestRate = _interestRate;
        if (
            (options._redemptionState != Redemption.EXCHANGEABLE &&
                options._redemptionState != Redemption.PERPETUAL) ||
            options._paymentFrequency != PaymentFrequency.NONE
        ) {
            require(
                _maturityDate > block.timestamp,
                "Buyback date should be greater than current time"
            );
            maturityDate = _maturityDate;
        }
        paymentFrequencyToSeconds[
            PaymentFrequency.DAILY
        ] = AVERAGE_SECONDS_IN_A_DAY;
        paymentFrequencyToSeconds[
            PaymentFrequency.SEMIMONTHLY
        ] = AVERAGE_SECONDS_IN_SEMI_MONTH;
        paymentFrequencyToSeconds[
            PaymentFrequency.WEEKLY
        ] = AVERAGE_SECONDS_IN_A_WEEK;
        paymentFrequencyToSeconds[
            PaymentFrequency.MONTHLY
        ] = AVERAGE_SECONDS_IN_A_MONTH;
        paymentFrequencyToSeconds[
            PaymentFrequency.ANNUALY
        ] = AVERAGE_SECONDS_IN_A_YEAR;
        contractDeploymentTime = block.timestamp;
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
        maturityDate = _buybackDate;
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
            maturityDate < block.timestamp,
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

    function payInterest(
        address _investor
    )
        public
        onlyOwner
        isPayable
        isFixedOrVariableRate
        investorExists(_investor)
    {
        require(block.timestamp < maturityDate, "Token has reached maturity");
        uint256 payment = (interestRate * faceValue) / INTEREST_RATE_PRECISION;
        require(
            IERC20(paymentToken).balanceOf(address(this)) >= payment,
            "You do not have sufficient balance to pay this investor!"
        );
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        require(
            !investorToPaymentPeriodToStatus[_investor][duration],
            "The investor has already been paid for this payment period"
        );
        bool success = IERC20(paymentToken).transfer(_investor, payment);
        if (!success) {
            revert Token__ExchangeFailed();
        }
        investorToPaymentPeriodToStatus[_investor][duration] = true;
    }

    function payInterestToAll()
        public
        onlyOwner
        isPayable
        isFixedOrVariableRate
    {
        require(block.timestamp < maturityDate, "Token has reached maturity");
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        require(
            duration == paymentPeriod + 1,
            "You cannot pay interest during this payment period"
        );
        address[] memory tokenHolders = asset.getTokenHolders();
        uint256 payment = (interestRate * faceValue) / INTEREST_RATE_PRECISION;
        require(
            IERC20(paymentToken).balanceOf(address(this)) >=
                payment * tokenHolders.length,
            "You do not have sufficient balance to pay all token holders!"
        );
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (
                !investorToPaymentPeriodToStatus[tokenHolders[i]][
                    paymentPeriod + 1
                ]
            ) {
                IERC20(paymentToken).transfer(tokenHolders[i], payment);
                investorToPaymentPeriodToStatus[tokenHolders[i]][
                    paymentPeriod + 1
                ] = true;
            }
        }
        paymentPeriod += 1;
    }

    function payInterestInPaymentInKind(
        address _tokenAddress,
        uint256 _tokenAmount
    )
        public
        onlyOwner
        isPaymentInKind
        isPayable
        isAllowedExchangeToken(_tokenAddress)
    {
        require(block.timestamp < maturityDate, "Token has reached maturity");
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        require(
            duration == paymentPeriod + 1,
            "You cannot pay interest during this payment period"
        );
        address[] memory tokenHolders = asset.getTokenHolders();
        require(
            IERC20(_tokenAddress).balanceOf(address(this)) >= _tokenAmount,
            "You do not have sufficient balance to pay all token holders!"
        );
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (
                !investorToPaymentPeriodToStatus[tokenHolders[i]][
                    paymentPeriod + 1
                ]
            ) {
                IERC20(_tokenAddress).transfer(tokenHolders[i], _tokenAmount);
                investorToPaymentPeriodToStatus[tokenHolders[i]][
                    paymentPeriod + 1
                ] = true;
            }
        }
        paymentPeriod += 1;
    }

    function payInterestInCash(
        CashReceipt[] memory test
    ) public onlyOwner isCashPayment isPayable {
        require(block.timestamp < maturityDate, "Token has reached maturity");
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        require(
            duration == paymentPeriod + 1,
            "You cannot pay interest during this payment period"
        );
        address[] memory tokenHolders = asset.getTokenHolders();
    }

    function updatePrice(uint256 _price) public onlyOwner isNonZero(_price) {
        price = _price;
    }

    function modifyInterestRate(
        uint256 _rate
    ) public onlyOwner isVariable isNonZero(_rate) {
        interestRate = _rate;
    }

    function getBalance(address _user) public view returns (uint256) {
        return asset.balanceOf(_user);
    }

    function getAddress() public view returns (address) {
        return address(asset);
    }

    function getTimestamp() public view returns (uint256) {
        return block.timestamp;
    }

    function getMaturity() public view returns (uint256) {
        return maturityDate;
    }

    // function test(CashReceipt memory _cash) public pure returns (uint256) {
    //     return _cash.date;
    // }
}
