// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";

contract GUARANTEE is Ownable {
    ///////////////////
    // Enums //////////
    ///////////////////
    enum Guarantee {
        GOVERNMENT,
        JOINT,
        SECURED,
        UNSECURED,
        NEGATIVE,
        SENIOR,
        SENIOR_SUBORDINATED,
        JUNIOR,
        JUNIOR_SUBORDINATED,
        SUPRANATURAL
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify guarantee state of the token
    Guarantee public guaranteeState;

    constructor(Guarantee _guaranteeState) {
        guaranteeState = _guaranteeState;
    }
}
