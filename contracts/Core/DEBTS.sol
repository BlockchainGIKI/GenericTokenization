// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.17;

import {INTEREST} from "./INTEREST.sol";
import {GUARANTEE} from "./GUARANTEE.sol";
import {REIMBURSEMENT} from "./REIMBURSEMENT.sol";
import {FORM} from "./FORM.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract DEBTS is INTEREST, GUARANTEE, REIMBURSEMENT, FORM {
    ///////////////////
    // Enums //////////
    ///////////////////
    enum InstrumentType {
        BONDS,
        CONVERTIBLE_BONDS,
        BONDS_WITH_WARRANTS_ATTACHED,
        MEDIUM_TERM_NOTES,
        ASSET_BACKED_SECURITIES,
        MUNCIPAL_BONDS,
        MORTGAGE_BACKED_SECURITIES,
        MONEY_MARKET_INSTRUMENTS
    }

    ///////////////////
    // Struct /////////
    ///////////////////
    struct DebtConfig {
        PaymentFrequency _paymentFrequency;
        PaymentFreq _paymentFreq;
        InterestType _interestType;
        Guarantee _guaranteeState;
        Reimbursement _reimbursementState;
        Form _formState;
    }

    struct params {
        uint256 _maturityDate;
        uint256 _faceValue;
        uint256 _interestRate;
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify type of debt instrument
    InstrumentType public debtType;

    constructor(
        address _parameters,
        DebtConfig memory config,
        params memory param
    )
        INTEREST(
            config._paymentFrequency,
            config._interestType,
            _parameters,
            param._maturityDate,
            param._faceValue,
            param._interestRate
        )
        GUARANTEE(config._guaranteeState)
        REIMBURSEMENT(
            config._reimbursementState,
            config._paymentFreq,
            _parameters,
            param._maturityDate,
            param._faceValue,
            param._interestRate
        )
        FORM(config._formState)
    {}
}
