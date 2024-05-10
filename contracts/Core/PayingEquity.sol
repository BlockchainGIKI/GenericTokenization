// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.17;

import {Voting} from "./Voting.sol";
import {REDEMPTION} from "./REDEMPTION.sol";
import {INCOME} from "./INCOME.sol";
import {FORM} from "./FORM.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract PayingEquity is Voting, REDEMPTION, INCOME, FORM {
    ///////////////////
    // Enums //////////
    ///////////////////
    enum PayingEquityType {
        PREFERRED_SHARES,
        PREFERRED_CONVERTIBLE_SHARES,
        PREFERENCE_SHARES,
        PREFERENCE_CONVERTIBLE_SHARES
    }

    ///////////////////
    // Struct /////////
    ///////////////////
    struct params {
        Redemption _redemptionState;
        Income _incomeState;
        PaymentFrequency _paymentFrequency;
        Form _formState;
        uint256 _buybackDate;
        uint256 _maturityDate;
        uint256 _callPrice;
        uint256 _incomeRate;
    }

    constructor(
        params memory config,
        address _parameters
    )
        REDEMPTION(
            config._redemptionState,
            config._buybackDate,
            config._maturityDate,
            config._callPrice,
            _parameters
        )
        INCOME(
            config._incomeState,
            config._paymentFrequency,
            config._incomeRate,
            config._maturityDate,
            _parameters
        )
        FORM(config._formState)
    {}
}
