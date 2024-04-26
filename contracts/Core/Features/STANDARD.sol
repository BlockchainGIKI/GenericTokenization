// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.17;

contract STANDARD {
    enum Standard {
        STANDARDIZED,
        NON_STANDARDIZED
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify standard state of the token
    Standard public standardState;

    constructor(Standard _standardState) {
        standardState = _standardState;
    }
}
