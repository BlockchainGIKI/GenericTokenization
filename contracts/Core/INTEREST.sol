// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./IParameters.sol";
import "./IAsset.sol";

contract INTEREST is Ownable {
    ///////////////////
    // Errors /////////
    ///////////////////
    error Token__InputParameterIsZero();
    error Token__ExchangeFailed();
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

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify payment frequency of the token
    PaymentFrequency public paymentFrequency;
    // Used to specify type of interest rate of the token
    InterestType public interestType;
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

    ////////////////////
    // Constants ///////
    ///////////////////
    uint256 private constant AVERAGE_SECONDS_IN_A_DAY = 86400;
    uint256 private constant AVERAGE_SECONDS_IN_A_WEEK = 604800;
    uint256 private constant AVERAGE_SECONDS_IN_SEMI_MONTH = 1209600;
    uint256 private constant AVERAGE_SECONDS_IN_A_MONTH = 2629800; //2628288;
    uint256 private constant AVERAGE_SECONDS_IN_A_YEAR = 31556952;

    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(PaymentFrequency => uint256) private paymentFrequencyToSeconds;
    mapping(address => mapping(uint256 => bool))
        public investorToPaymentPeriodToStatus;
    mapping(address => mapping(uint256 => CashReceipt))
        public investorToPaymentPeriodToReceipt;

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
        address assetAddress = IParameters(parameters).getAssetAddress();
        (bool status, ) = IAsset(assetAddress).tokenHolderExists(_investor);
        if (!status) {
            revert Token__InvestorDoesNotExist();
        }
        _;
    }

    ///////////////////
    // Functions //////
    ///////////////////
    constructor(
        PaymentFrequency _paymentFrequency,
        InterestType _interestType,
        address _parameters,
        uint256 _maturityDate,
        uint256 _faceValue,
        uint256 _interestRate
    ) {
        paymentFrequency = _paymentFrequency;
        interestType = _interestType;
        faceValue = _faceValue;
        interestRate = _interestRate;
        parameters = _parameters;

        if ((_paymentFrequency != PaymentFrequency.NONE)) {
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
        contractDeploymentTime = block.timestamp;
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
        uint256 precision = IParameters(parameters).getPrecision();
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        uint256 payment = (interestRate *
            precision *
            faceValue *
            asset.balanceOf(_investor)) / precision;
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
        uint256 precision = IParameters(parameters).getPrecision();
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        address[] memory tokenHolders = asset.getTokenHolders();
        uint256 payment = (interestRate *
            precision *
            faceValue *
            asset.totalSupply()) / precision;
        require(
            IERC20(paymentToken).balanceOf(address(this)) >= payment,
            "You do not have sufficient balance to pay all token holders!"
        );
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (!investorToPaymentPeriodToStatus[tokenHolders[i]][duration]) {
                payment =
                    (interestRate *
                        precision *
                        faceValue *
                        asset.balanceOf(tokenHolders[i])) /
                    precision;
                IERC20(paymentToken).transfer(tokenHolders[i], payment);
                investorToPaymentPeriodToStatus[tokenHolders[i]][
                    duration
                ] = true;
            }
        }
    }

    function payInterestInPaymentInKind(
        address _investor,
        address _tokenAddress,
        uint256 _tokenAmount
    ) public onlyOwner isPaymentInKind isPayable investorExists(_investor) {
        require(block.timestamp < maturityDate, "Token has reached maturity");
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        require(
            !investorToPaymentPeriodToStatus[_investor][duration],
            "The investor has already been paid for this payment period"
        );
        require(
            IERC20(_tokenAddress).balanceOf(address(this)) >= _tokenAmount,
            "You do not have sufficient balance to the investor!"
        );
        bool success = IERC20(_tokenAddress).transfer(_investor, _tokenAmount);
        if (!success) {
            revert Token__ExchangeFailed();
        }
        investorToPaymentPeriodToStatus[_investor][duration] = true;
    }

    function payInterestInPaymentInKindToAll(
        address _tokenAddress,
        uint256 _tokenAmount
    ) public onlyOwner isPaymentInKind isPayable {
        require(block.timestamp < maturityDate, "Token has reached maturity");
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address[] memory tokenHolders = asset.getTokenHolders();
        require(
            IERC20(_tokenAddress).balanceOf(address(this)) >= _tokenAmount,
            "You do not have sufficient balance to pay all token holders!"
        );
        for (uint256 i = 0; i < tokenHolders.length; i++) {
            if (!investorToPaymentPeriodToStatus[tokenHolders[i]][duration]) {
                IERC20(_tokenAddress).transfer(tokenHolders[i], _tokenAmount);
                investorToPaymentPeriodToStatus[tokenHolders[i]][
                    duration
                ] = true;
            }
        }
    }

    function getRecoveredAddress(
        bytes memory sig,
        bytes32 dataHash
    ) internal pure returns (address addr) {
        bytes32 ra;
        bytes32 sa;
        uint8 va;

        // Check the signature length
        if (sig.length != 65) {
            return address(0);
        }

        // Divide the signature in r, s and v variables
        // solhint-disable-next-line no-inline-assembly
        assembly {
            ra := mload(add(sig, 32))
            sa := mload(add(sig, 64))
            va := byte(0, mload(add(sig, 96)))
        }

        if (va < 27) {
            va += 27;
        }

        address recoveredAddress = ecrecover(dataHash, va, ra, sa);

        return (recoveredAddress);
    }

    function payInterestInCash(
        uint256 _receiptNumber,
        uint256 _date,
        address _tokenHolder,
        uint256 _amount,
        bytes memory _signature
    ) public onlyOwner isCashPayment isPayable investorExists(_tokenHolder) {
        require(block.timestamp < maturityDate, "Token has reached maturity");
        bytes32 dataHash = keccak256(
            abi.encode(_receiptNumber, _date, _tokenHolder, _amount)
        );
        bytes32 prefixedHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", dataHash)
        );
        address recovered = getRecoveredAddress(_signature, prefixedHash);
        require(recovered == owner(), "The signer is not the owner");
        uint256 duration = (block.timestamp - contractDeploymentTime) /
            paymentFrequencyToSeconds[paymentFrequency];
        require(
            !investorToPaymentPeriodToStatus[_tokenHolder][duration],
            "Investor already paid for this payment period"
        );
        investorToPaymentPeriodToReceipt[_tokenHolder][duration] = CashReceipt(
            _receiptNumber,
            _date,
            _tokenHolder,
            _amount,
            _signature
        );
        investorToPaymentPeriodToStatus[_tokenHolder][duration] = true;
    }

    function modifyInterestRate(
        uint256 _rate
    ) public onlyOwner isVariable isNonZero(_rate) {
        interestRate = _rate;
    }
}
