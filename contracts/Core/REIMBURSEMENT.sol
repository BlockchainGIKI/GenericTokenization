// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./IParameters.sol";
import "./IAsset.sol";

contract REIMBURSEMENT is Ownable {
    ///////////////////
    // Errors /////////
    ///////////////////
    error Token__TokenIsNotOfPayableType();
    error Token__TokenIsNotOfExtendibleType();
    error Token__InputParameterIsZero();
    error Token__ExchangeFailed();
    error Token__InvestorDoesNotExist();
    error Token__ReimbursementIsNotofMaturityType();
    error Token__ReimbursementIsNOtOfAmortizableType();
    error Token__ReimbursementIsOfAmortizableType();
    error Token__TokenIsNotOfCallableType();
    error Token__TokenIsNotOfPutType();

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

    enum Reimbursement {
        NONE,
        FIXED_MATURITY,
        FIXED_MATURITY_WITH_CALL,
        FIXED_MATURITY_WITH_PUT,
        FIXED_MATURITY_WITH_PUT_AND_CALL,
        AMORTIZATION,
        AMORTIZATION_WITH_CALL,
        AMORTIZATION_WITH_PUT,
        AMORTIZATION_WITH_PUT_AND_CALL,
        PERPETUAL,
        PERPETUAL_WITH_CALL,
        PERPETUAL_WITH_PUT,
        EXTENDIBLE
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify payment frequency of the token
    PaymentFrequency public paymentFrequency;
    // Used to specify redemption/reimbursement (payout at maturity) state of the token
    Reimbursement public reimbursementState;
    // Used to specify maturity date of the token
    uint256 public maturityDate;
    // Set to the current block timestamp when the contract is deployed
    uint256 public contractDeploymentTime;
    // Set to the address of the parameters contract
    address public parameters;
    // The face value of the asset
    uint256 public faceValue;
    // Refers to the interest rate of the token set during contract deployment. Can optionally be modified if interest rate type is variable
    uint256 public interestRate;
    // Refers to the periodic interest rate obtained by dividing the token duration with the payment frequency
    uint256 public periodicInterestRate;
    // Refers to the duration of the token
    uint256 public loanTerm;
    // Refers to the periodic payment amounts that the issuer has to pay to the token holders
    uint256 public periodicPayment;
    // Indicates if the reimbursement is of perpetual type
    bool public perpetualStatus;
    // Refers to the starting date of the put period
    uint256 public startDate;
    // Refers to the ending date of the put period
    uint256 public endDate;
    ////////////////////
    // Constants ///////
    ///////////////////
    uint256 private constant AVERAGE_SECONDS_IN_A_DAY = 86400;
    uint256 private constant AVERAGE_SECONDS_IN_A_WEEK = 604800;
    uint256 private constant AVERAGE_SECONDS_IN_SEMI_MONTH = 1209600;
    uint256 private constant AVERAGE_SECONDS_IN_A_MONTH = 2629800; //2628288;
    uint256 private constant AVERAGE_SECONDS_IN_A_YEAR = 31556952;
    uint256 private constant DAYS_IN_A_YEAR = 365;
    uint256 private constant WEEKS_IN_A_YEAR = 52;
    uint256 private constant SEMI_MONTHS_IN_A_YEAR = 24;
    uint256 private constant MONTHS_IN_A_YEAR = 12;
    uint256 private constant YEAR_IN_A_YEAR = 1;
    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(PaymentFrequency => uint256) private paymentFrequencyToSeconds;
    mapping(PaymentFrequency => uint256) private paymentFrequencyToLoanTerm;
    mapping(address => mapping(uint256 => bool))
        public investorToPaymentPeriodToStatus;
    mapping(address => bool) public investorToMaturityPaymentStatus;

    ///////////////////
    // Modifiers //////
    ///////////////////
    modifier isExtendible() {
        if ((reimbursementState != Reimbursement.EXTENDIBLE)) {
            revert Token__TokenIsNotOfExtendibleType();
        }
        _;
    }

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

    modifier hasMaturityPayment() {
        if (
            reimbursementState != Reimbursement.FIXED_MATURITY &&
            reimbursementState != Reimbursement.FIXED_MATURITY_WITH_CALL &&
            reimbursementState != Reimbursement.FIXED_MATURITY_WITH_PUT &&
            reimbursementState !=
            Reimbursement.FIXED_MATURITY_WITH_PUT_AND_CALL &&
            reimbursementState != Reimbursement.EXTENDIBLE
        ) {
            revert Token__ReimbursementIsNotofMaturityType();
        }
        _;
    }

    modifier isAmortizable() {
        if (
            reimbursementState != Reimbursement.AMORTIZATION &&
            reimbursementState != Reimbursement.AMORTIZATION_WITH_CALL &&
            reimbursementState != Reimbursement.AMORTIZATION_WITH_PUT &&
            reimbursementState != Reimbursement.AMORTIZATION_WITH_PUT_AND_CALL
        ) {
            revert Token__ReimbursementIsNOtOfAmortizableType();
        }
        _;
    }

    modifier isNotAmortizable() {
        if (
            reimbursementState == Reimbursement.AMORTIZATION ||
            reimbursementState == Reimbursement.AMORTIZATION_WITH_CALL ||
            reimbursementState == Reimbursement.AMORTIZATION_WITH_PUT ||
            reimbursementState == Reimbursement.AMORTIZATION_WITH_PUT_AND_CALL
        ) {
            revert Token__ReimbursementIsOfAmortizableType();
        }
        _;
    }

    modifier isCallable() {
        if (
            reimbursementState != Reimbursement.FIXED_MATURITY_WITH_CALL &&
            reimbursementState !=
            Reimbursement.FIXED_MATURITY_WITH_PUT_AND_CALL &&
            reimbursementState != Reimbursement.AMORTIZATION_WITH_CALL &&
            reimbursementState !=
            Reimbursement.AMORTIZATION_WITH_PUT_AND_CALL &&
            reimbursementState != Reimbursement.PERPETUAL_WITH_CALL
        ) {
            revert Token__TokenIsNotOfCallableType();
        }
        _;
    }

    modifier isPutable() {
        if (
            reimbursementState != Reimbursement.FIXED_MATURITY_WITH_PUT &&
            reimbursementState !=
            Reimbursement.FIXED_MATURITY_WITH_PUT_AND_CALL &&
            reimbursementState != Reimbursement.AMORTIZATION_WITH_PUT &&
            reimbursementState !=
            Reimbursement.AMORTIZATION_WITH_PUT_AND_CALL &&
            reimbursementState != Reimbursement.PERPETUAL_WITH_PUT
        ) {
            revert Token__TokenIsNotOfPutType();
        }
        _;
    }

    ///////////////////
    // Functions //////
    ///////////////////
    constructor(
        Reimbursement _reimbursementState,
        PaymentFrequency _paymentFrequency,
        address _parameters,
        uint256 _maturityDate,
        uint256 _faceValue,
        uint256 _interestRate
    ) {
        reimbursementState = _reimbursementState;
        paymentFrequency = _paymentFrequency;
        faceValue = _faceValue;
        interestRate = _interestRate;
        parameters = _parameters;

        if (
            (_paymentFrequency != PaymentFrequency.NONE) &&
            (_reimbursementState != Reimbursement.PERPETUAL &&
                _reimbursementState != Reimbursement.PERPETUAL_WITH_CALL &&
                _reimbursementState != Reimbursement.PERPETUAL_WITH_PUT)
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
        paymentFrequencyToLoanTerm[PaymentFrequency.DAILY] = DAYS_IN_A_YEAR;
        paymentFrequencyToLoanTerm[PaymentFrequency.WEEKLY] = WEEKS_IN_A_YEAR;
        paymentFrequencyToLoanTerm[
            PaymentFrequency.SEMIMONTHLY
        ] = SEMI_MONTHS_IN_A_YEAR;
        paymentFrequencyToLoanTerm[PaymentFrequency.MONTHLY] = MONTHS_IN_A_YEAR;
        paymentFrequencyToLoanTerm[PaymentFrequency.ANNUALY] = YEAR_IN_A_YEAR;
        contractDeploymentTime = block.timestamp;
        if (
            reimbursementState == Reimbursement.AMORTIZATION ||
            reimbursementState == Reimbursement.AMORTIZATION_WITH_CALL ||
            reimbursementState == Reimbursement.AMORTIZATION_WITH_PUT ||
            reimbursementState == Reimbursement.AMORTIZATION_WITH_PUT_AND_CALL
        ) {
            uint256 PRECISION = IParameters(parameters).getPrecision();
            periodicInterestRate =
                (interestRate * 10 ** PRECISION) /
                (paymentFrequencyToLoanTerm[paymentFrequency] * 100);
            loanTerm =
                (maturityDate *
                    10 ** PRECISION -
                    contractDeploymentTime *
                    10 ** PRECISION) /
                paymentFrequencyToSeconds[paymentFrequency];
        }
        perpetualStatus =
            reimbursementState == Reimbursement.PERPETUAL ||
            reimbursementState == Reimbursement.PERPETUAL_WITH_CALL ||
            reimbursementState == Reimbursement.PERPETUAL_WITH_PUT;
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

    function payAtMaturity(
        address _investor
    ) public onlyOwner hasMaturityPayment investorExists(_investor) {
        require(
            maturityDate <= block.timestamp,
            "The token has not matured yet!"
        );
        require(
            !investorToMaturityPaymentStatus[_investor],
            "The token holder has already been paid"
        );
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        require(
            IERC20(paymentToken).balanceOf(address(this)) >=
                faceValue * asset.balanceOf(_investor),
            "You do not have sufficient balance to pay this token holder"
        );
        bool success = IERC20(paymentToken).transfer(
            _investor,
            faceValue * asset.balanceOf(_investor)
        );
        if (!success) {
            revert Token__ExchangeFailed();
        }
        investorToMaturityPaymentStatus[_investor] = true;
    }

    function payAtMaturityToAll() public onlyOwner hasMaturityPayment {
        require(
            maturityDate <= block.timestamp,
            "The token has not matured yet!"
        );
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        address[] memory tokenHolders = asset.getTokenHolders();
        require(
            IERC20(paymentToken).balanceOf(address(this)) >=
                faceValue * asset.totalSupply(),
            "You do not have sufficient balance to pay this token holder"
        );
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (!investorToMaturityPaymentStatus[tokenHolders[i]]) {
                IERC20(paymentToken).transfer(
                    tokenHolders[i],
                    faceValue * asset.balanceOf(tokenHolders[i])
                );
                investorToMaturityPaymentStatus[tokenHolders[i]] = true;
            }
        }
    }

    function setAmortizationSchedule(
        uint256 numerator,
        uint256 denominator
    ) public isAmortizable isNonZero(denominator) isNonZero(numerator) {
        require(
            msg.sender == owner() || msg.sender == address(this),
            "This function is only callable by the owner or the smart contract itself"
        );
        uint256 PRECISION = IParameters(parameters).getPrecision();
        periodicPayment =
            (faceValue * 10 ** PRECISION * numerator) /
            denominator;
    }

    function payAmortizedPayments(
        address _tokenHolder
    )
        public
        onlyOwner
        isAmortizable
        investorExists(_tokenHolder)
        isNonZero(periodicPayment)
    {
        require(
            !investorToMaturityPaymentStatus[_tokenHolder],
            "Token has matured!"
        );
        uint256 PRECISION = IParameters(parameters).getPrecision();
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        uint256 payment = (asset.balanceOf(_tokenHolder) * periodicPayment) /
            10 ** PRECISION;
        require(
            IERC20(paymentToken).balanceOf(address(this)) >= payment,
            "You do not have sufficient balance to pay this investor!"
        );
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        require(
            !investorToPaymentPeriodToStatus[_tokenHolder][duration],
            "The token holder has already been paid for this payment period"
        );
        bool success = IERC20(paymentToken).transfer(_tokenHolder, payment);
        if (!success) {
            revert Token__ExchangeFailed();
        }
        investorToPaymentPeriodToStatus[_tokenHolder][duration] = true;
        uint256 maxPeriod = (maturityDate - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        if (duration >= maxPeriod) {
            investorToMaturityPaymentStatus[_tokenHolder] = true;
        }
    }

    function payAmortizedPaymentsToAll()
        public
        onlyOwner
        isAmortizable
        isNonZero(periodicPayment)
    {
        uint256 PRECISION = IParameters(parameters).getPrecision();
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        address[] memory tokenHolders = asset.getTokenHolders();
        require(
            IERC20(paymentToken).balanceOf(address(this)) >=
                (asset.totalSupply() * periodicPayment) / 10 ** PRECISION,
            "You do not have sufficient balance to pay all token holders!"
        );
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        uint256 maxPeriod = (maturityDate - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (
                !investorToPaymentPeriodToStatus[tokenHolders[i]][duration] &&
                !investorToMaturityPaymentStatus[tokenHolders[i]]
            ) {
                IERC20(paymentToken).transfer(
                    tokenHolders[i],
                    ((periodicPayment * asset.balanceOf(tokenHolders[i])) /
                        10 ** PRECISION)
                );
                investorToPaymentPeriodToStatus[tokenHolders[i]][
                    duration
                ] = true;
                if (duration >= maxPeriod) {
                    investorToMaturityPaymentStatus[tokenHolders[i]] = true;
                }
            }
        }
    }

    function modifyInterestRate(
        uint256 _rate,
        uint256 numerator,
        uint256 denominator
    )
        public
        onlyOwner
        isNonZero(_rate)
        isNonZero(numerator)
        isNonZero(denominator)
        isAmortizable
    {
        interestRate = _rate;
        periodicInterestRate = calculatePeriodicInterestRate(_rate);
        setAmortizationSchedule(numerator, denominator);
    }

    function calculatePeriodicInterestRate(
        uint256 _rate
    ) public view isNonZero(_rate) returns (uint256) {
        uint256 PRECISION = IParameters(parameters).getPrecision();
        return
            (_rate * 10 ** PRECISION) /
            (paymentFrequencyToLoanTerm[paymentFrequency] * 100);
    }

    function issueToken(
        uint256 _amount,
        address _to
    ) public onlyOwner isNonZero(_amount) {
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        asset.transfer(_to, _amount);
    }

    function callToken(
        address _tokenHolder,
        uint256 _amount
    ) public onlyOwner isCallable investorExists(_tokenHolder) {
        require(block.timestamp < maturityDate, "The token has matured");
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        uint256 balance = asset.balanceOf(_tokenHolder);
        require(
            IERC20(paymentToken).balanceOf(address(this)) >= balance + _amount,
            "You do not have sufficient funds to reimburse this token holder!"
        );
        bool success = IERC20(paymentToken).transfer(
            _tokenHolder,
            balance * faceValue + _amount
        );
        if (!success) {
            revert Token__ExchangeFailed();
        }
        asset.burn(_tokenHolder, balance);
    }

    function callTokenFromAll(uint256 _amount) public onlyOwner isCallable {
        require(block.timestamp < maturityDate, "The token has matured");
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        address[] memory tokenHolders = asset.getTokenHolders();
        uint256 balance = asset.totalSupply();
        require(
            IERC20(paymentToken).balanceOf(address(this)) >=
                balance * faceValue + _amount * tokenHolders.length,
            "You do not have sufficient funds to reimburse all token holders!"
        );
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            IERC20(paymentToken).transfer(
                tokenHolders[i],
                asset.balanceOf(tokenHolders[i]) * faceValue + _amount
            );
            asset.burn(tokenHolders[i], asset.balanceOf(tokenHolders[i]));
        }
    }

    function setPutPeriod(
        uint256 _startDate,
        uint256 _endDate
    ) public onlyOwner isPutable isNonZero(_startDate) isNonZero(_endDate) {
        require(
            (_endDate > _startDate) && (_endDate <= maturityDate),
            "The end date should be greater than start date and less than maturity"
        );
        require(
            (contractDeploymentTime <= _startDate) &&
                (block.timestamp <= _startDate),
            "The start date should be set between the contract deployment time and maturity"
        );
        startDate = _startDate;
        endDate = _endDate;
    }

    function putToken(
        uint256 _amount
    )
        public
        isPutable
        isNonZero(startDate)
        investorExists(msg.sender)
        isNonZero(_amount)
    {
        require(
            startDate <= block.timestamp && block.timestamp <= endDate,
            "You cannot put the token outside of the put period"
        );
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        require(
            asset.balanceOf(msg.sender) >= _amount &&
                IERC20(paymentToken).balanceOf(address(this)) >=
                _amount * faceValue,
            "The token redemption exceeds the current balance"
        );
        bool success = IERC20(paymentToken).transfer(
            msg.sender,
            _amount * faceValue
        );
        if (!success) {
            revert Token__ExchangeFailed();
        }
        asset.burn(msg.sender, _amount);
    }

    function getTimestamp() public view returns (uint256) {
        return block.timestamp;
    }

    function getMaturity() public view returns (uint256) {
        return maturityDate;
    }

    function getPeriodicPayment() public view returns (uint256) {
        return periodicPayment;
    }
}
