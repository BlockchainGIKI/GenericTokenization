// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IIdentityRegistry} from "@T-REX/contracts/registry/interface/IIdentityRegistry.sol";
import {Asset} from "./Asset.sol";

contract Equities is Ownable {
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
    error Token__InvestorDoesNotExist();
    error Token__IncomeIsNotOfParticipatingType();
    error Token__IncomeRateIsNotOfVariableType();
    error Token__IncomeIsNotOfCumulativeType();

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

    enum PaymentFrequency {
        NONE,
        DAILY,
        WEEKLY,
        SEMIMONTHLY,
        MONTHLY,
        ANNUALY
    }

    enum Income {
        NONE,
        FIXED_RATE,
        CUMULATIVE_FIXED_RATE,
        PARTICIPATING,
        CUMULATIVE_PARTICIPATING,
        ADJUSTABLE_VARIABLE_RATE,
        NORMAL_RATE,
        AUCTION_RATE,
        DIVIDENDS
    }

    ///////////////////
    // Struct /////////
    ///////////////////

    ////////////////////
    // State Variables /
    ///////////////////

    // Used to specify remdemption state of the token
    Redemption public redemptionState;
    // Used to specify payment frequency of the token
    PaymentFrequency public paymentFrequency;
    // Used to specify the income type of the token
    Income public incomeState;
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
    // Refers to the underlying token created during contract deployment
    Asset private asset;
    // Refers to the income rate of the token set during contract deployment. Can optionally be modified if income rate type is variable
    uint256 public incomeRate;

    ////////////////////
    // Constants ///////
    ///////////////////
    uint256 private constant AVERAGE_SECONDS_IN_A_DAY = 86400;
    uint256 private constant AVERAGE_SECONDS_IN_A_WEEK = 604800;
    uint256 private constant AVERAGE_SECONDS_IN_SEMI_MONTH = 1209600;
    uint256 private constant AVERAGE_SECONDS_IN_A_MONTH = 2629800; //2628288;
    uint256 private constant AVERAGE_SECONDS_IN_A_YEAR = 31556952;
    uint256 private constant INTEREST_RATE_PRECISION = 1000;
    uint256 private constant DAYS_IN_A_YEAR = 365;
    uint256 private constant WEEKS_IN_A_YEAR = 52;
    uint256 private constant SEMI_MONTHS_IN_A_YEAR = 24;
    uint256 private constant MONTHS_IN_A_YEAR = 12;
    uint256 private constant YEAR_IN_A_YEAR = 1;
    uint256 private constant PRECISION = 8;
    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(address => uint256) public conversionRate;
    mapping(PaymentFrequency => uint256) private paymentFrequencyToSeconds;
    mapping(address => mapping(uint256 => bool))
        public investorToPaymentPeriodToStatus;
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

    modifier investorExists(address _investor) {
        (bool status, ) = asset.tokenHolderExists(_investor);
        if (!status) {
            revert Token__InvestorDoesNotExist();
        }
        _;
    }

    modifier isParticipating(uint256 _dividend) {
        if (
            incomeState == Income.PARTICIPATING ||
            incomeState == Income.CUMULATIVE_PARTICIPATING
        ) {
            if (_dividend == 0) {
                revert Token__InputParameterIsZero();
            }
        }
        _;
    }

    modifier isVariable() {
        if (incomeState != Income.ADJUSTABLE_VARIABLE_RATE) {
            revert Token__IncomeRateIsNotOfVariableType();
        }
        _;
    }

    modifier isCumulative() {
        if (
            incomeState != Income.CUMULATIVE_FIXED_RATE &&
            incomeState != Income.CUMULATIVE_PARTICIPATING
        ) {
            revert Token__IncomeIsNotOfCumulativeType();
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
        Income _incomeState,
        PaymentFrequency _paymentFrequency,
        uint256 _maturityDate,
        address _paymentToken,
        address _identityRegistry,
        uint256 _price,
        uint256 _incomeRate
    ) {
        asset = new Asset(_initialSupply, _name, _symbol, _identityRegistry);
        redemptionState = _redemptionState;
        incomeState = _incomeState;
        paymentFrequency = _paymentFrequency;
        paymentToken = _paymentToken;
        identityRegistry = _identityRegistry;
        price = _price;
        incomeRate = _incomeRate;
        if (
            (_redemptionState != Redemption.EXCHANGEABLE &&
                _redemptionState != Redemption.PERPETUAL) &&
            (_paymentFrequency != PaymentFrequency.NONE)
        ) {
            require(
                _maturityDate > block.timestamp,
                "Maturity/Buyback date should be greater than current time"
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
    }

    function addExchangeableToken(
        address _token,
        uint256 _conversionRate
    ) public onlyOwner isExchangeable {
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

    function extendMaturityDate(
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

    function payIncome(
        address _investor,
        uint256 _dividend
    )
        public
        onlyOwner
        isPayable
        investorExists(_investor)
        isParticipating(_dividend)
    {
        require(
            block.timestamp < maturityDate ||
                redemptionState == Redemption.PERPETUAL,
            "Token has reached maturity"
        );
        if (
            incomeState != Income.PARTICIPATING &&
            incomeState != Income.CUMULATIVE_PARTICIPATING
        ) {
            _dividend = 0;
        }
        uint256 payment = ((incomeRate *
            INTEREST_RATE_PRECISION *
            asset.balanceOf(_investor)) / INTEREST_RATE_PRECISION) + _dividend;
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

    function payCumulativeIncome(
        address _investor,
        uint256 _paymentPeriod,
        uint256 _dividend
    )
        public
        onlyOwner
        isCumulative
        isPayable
        investorExists(_investor)
        isParticipating(_dividend)
    {
        require(
            block.timestamp < maturityDate ||
                redemptionState == Redemption.PERPETUAL,
            "Token has reached maturity"
        );
        if (
            incomeState != Income.PARTICIPATING &&
            incomeState != Income.CUMULATIVE_PARTICIPATING
        ) {
            _dividend = 0;
        }
        uint256 payment = ((incomeRate *
            INTEREST_RATE_PRECISION *
            asset.balanceOf(_investor)) / INTEREST_RATE_PRECISION) + _dividend;
        require(
            IERC20(paymentToken).balanceOf(address(this)) >= payment,
            "You do not have sufficient balance to pay this investor!"
        );
        require(
            !investorToPaymentPeriodToStatus[_investor][_paymentPeriod],
            "The investor has already been paid for this payment period"
        );
        bool success = IERC20(paymentToken).transfer(_investor, payment);
        if (!success) {
            revert Token__ExchangeFailed();
        }
        investorToPaymentPeriodToStatus[_investor][_paymentPeriod] = true;
    }

    function payIncomeToAll(
        uint256 _dividend
    ) public onlyOwner isPayable isParticipating(_dividend) {
        require(
            block.timestamp < maturityDate ||
                redemptionState == Redemption.PERPETUAL,
            "Token has reached maturity"
        );
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        address[] memory tokenHolders = asset.getTokenHolders();
        if (
            incomeState != Income.PARTICIPATING &&
            incomeState != Income.CUMULATIVE_PARTICIPATING
        ) {
            _dividend = 0;
        }
        require(
            IERC20(paymentToken).balanceOf(address(this)) >=
                ((asset.totalSupply() * incomeRate * INTEREST_RATE_PRECISION) /
                    INTEREST_RATE_PRECISION) +
                    (_dividend * asset.totalSupply()),
            "You do not have sufficient balance to pay all token holders!"
        );
        uint256 payment;
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (!investorToPaymentPeriodToStatus[tokenHolders[i]][duration]) {
                payment =
                    ((incomeRate *
                        INTEREST_RATE_PRECISION *
                        asset.balanceOf(tokenHolders[i])) /
                        INTEREST_RATE_PRECISION) +
                    _dividend;
                IERC20(paymentToken).transfer(tokenHolders[i], payment);
                investorToPaymentPeriodToStatus[tokenHolders[i]][
                    duration
                ] = true;
            }
        }
    }

    function updatePrice(uint256 _price) public onlyOwner isNonZero(_price) {
        price = _price;
    }

    function modifyInterestRate(
        uint256 _rate
    ) public onlyOwner isVariable isNonZero(_rate) {
        incomeRate = _rate;
    }

    function getBalance(address _user) public view returns (uint256) {
        return asset.balanceOf(_user);
    }

    function getTotalSupply() public view returns (uint256) {
        return asset.totalSupply();
    }

    function getTokenHolders() public view returns (address[] memory) {
        return asset.getTokenHolders();
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
}
