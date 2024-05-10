// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./IParameters.sol";
import "./IAsset.sol";
import "./IREDEMPTION.sol";

contract INCOME is Ownable {
    ///////////////////
    // Errors /////////
    ///////////////////
    error Token__InputParameterIsZero();
    error Token__TokenIsNotOfPayableType();
    error Token__InvestorDoesNotExist();
    error Token__IncomeIsNotOfParticipatingType();
    error Token__IncomeRateIsNotOfVariableType();
    error Token__IncomeIsNotOfCumulativeType();
    error Token__ExchangeFailed();

    ///////////////////
    // Enums //////////
    ///////////////////
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

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify payment frequency of the token
    PaymentFrequency public paymentFrequency;
    // Used to specify the income type of the token
    Income public incomeState;
    // Set to the current block timestamp when the contract is deployed
    uint256 public contractDeploymentTime;
    // Set to the address of the parameters contract
    address public parameters;
    // Set to the maturity date defined in the Redemption contract
    uint256 public maturityDate;
    // Refers to the income rate of the token set during contract deployment. Can optionally be modified if income rate type is variable
    uint256 public incomeRate;

    uint256 private constant AVERAGE_SECONDS_IN_A_DAY = 86400;
    uint256 private constant AVERAGE_SECONDS_IN_A_WEEK = 604800;
    uint256 private constant AVERAGE_SECONDS_IN_SEMI_MONTH = 1209600;
    uint256 private constant AVERAGE_SECONDS_IN_A_MONTH = 2629800; //2628288;
    uint256 private constant AVERAGE_SECONDS_IN_A_YEAR = 31556952;

    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(address => mapping(uint256 => bool))
        public investorToPaymentPeriodToStatus;
    mapping(PaymentFrequency => uint256) private paymentFrequencyToSeconds;
    ///////////////////
    // Modifiers //////
    ///////////////////

    modifier isNonZero(uint256 _input) {
        if (_input == 0) {
            revert Token__InputParameterIsZero();
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
        address assetAddress = IParameters(parameters).getAssetAddress();
        (bool status, ) = IAsset(assetAddress).tokenHolderExists(_investor);
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
        Income _incomeState,
        PaymentFrequency _paymentFrequency,
        uint256 _incomeRate,
        uint256 _maturityDate,
        address _parameters
    ) // address _redemption
    {
        incomeState = _incomeState;
        paymentFrequency = _paymentFrequency;
        incomeRate = _incomeRate;
        parameters = _parameters;

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

        // if (_redemption != address(0)) {
        //     maturityDate = IREDEMPTION(_redemption).getMaturityDate();
        // }
        maturityDate = _maturityDate;
        contractDeploymentTime = block.timestamp;
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
            block.timestamp < maturityDate || maturityDate == 0,
            "Token has reached maturity"
        );
        if (
            incomeState != Income.PARTICIPATING &&
            incomeState != Income.CUMULATIVE_PARTICIPATING
        ) {
            _dividend = 0;
        }
        uint256 precision = IParameters(parameters).getPrecision();
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        uint256 payment = ((incomeRate *
            precision *
            asset.balanceOf(_investor)) / precision) + _dividend;
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
        if (
            incomeState != Income.PARTICIPATING &&
            incomeState != Income.CUMULATIVE_PARTICIPATING
        ) {
            _dividend = 0;
        }
        uint256 precision = IParameters(parameters).getPrecision();
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        uint256 payment = ((incomeRate *
            precision *
            asset.balanceOf(_investor)) / precision) + _dividend;
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
            block.timestamp < maturityDate || maturityDate == 0,
            "Token has reached maturity"
        );
        if (
            incomeState != Income.PARTICIPATING &&
            incomeState != Income.CUMULATIVE_PARTICIPATING
        ) {
            _dividend = 0;
        }
        uint256 precision = IParameters(parameters).getPrecision();
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
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
                ((asset.totalSupply() * incomeRate * precision) / precision) +
                    (_dividend * asset.totalSupply()),
            "You do not have sufficient balance to pay all token holders!"
        );
        uint256 payment;
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (!investorToPaymentPeriodToStatus[tokenHolders[i]][duration]) {
                payment =
                    ((incomeRate *
                        precision *
                        asset.balanceOf(tokenHolders[i])) / precision) +
                    _dividend;
                IERC20(paymentToken).transfer(tokenHolders[i], payment);
                investorToPaymentPeriodToStatus[tokenHolders[i]][
                    duration
                ] = true;
            }
        }
    }
}
