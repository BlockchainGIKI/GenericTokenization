// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";

contract FORM is Ownable {
    ///////////////////
    // Enums //////////
    ///////////////////
    enum Form {
        BEARER,
        REGISTERED,
        BEARER_REGISTERED,
        OTHERS
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify form state of the token
    Form public formState;

    constructor(Form _formState) {
        formState = _formState;
    }
}
