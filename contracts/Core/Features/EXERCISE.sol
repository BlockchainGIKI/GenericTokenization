// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.17;

import "../IParameters.sol";
import "../IAsset.sol";

contract EXERCISE {
    ///////////////////
    // Errors /////////
    ///////////////////
    error Token__InvestorDoesNotExist();
    error Token__OptionAlreadyExercised();
    error Token__AmericanExerciseOptionExpired();
    error Token__InvalidExerciseOfEuropeanOption();
    error Token__BermudanExerciseOptionExpired();
    error Token__PrematureExerciseAttempt();
    error Token__InvalidExerciseOfBermudanOption();

    ///////////////////
    // Enums //////////
    ///////////////////
    enum Exercise_Option_Style {
        AMERICAN,
        EUROPEAN,
        BERMUDAN
    }

    enum Periodicity {
        DAILY,
        WEEKLY,
        SEMIMONTHLY,
        MONTHLY,
        ANNUALY
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify the exercise option style of the token
    Exercise_Option_Style public exerciseOptionStyle;
    // Used to specify the expiration date of the token
    uint256 public expirationDate;
    // Used to specify start date of the expiration period if the exercise option style is EUROPEAN
    uint256 public startDate;
    // Used to specify the periodicity of the exercise dates if the exercise option style is BERMUDAN
    Periodicity public periodicity;
    // Set to the address of the parameters contract
    address public exerciseParameters;

    ////////////////////
    // Constants ///////
    ///////////////////
    uint256 internal constant AVERAGE_SECONDS_IN_A_DAY = 86400;
    uint256 internal constant AVERAGE_SECONDS_IN_A_WEEK = 604800;
    uint256 internal constant AVERAGE_SECONDS_IN_SEMI_MONTH = 1209600;
    uint256 internal constant AVERAGE_SECONDS_IN_A_MONTH = 2629800;
    uint256 internal constant AVERAGE_SECONDS_IN_A_YEAR = 31556952;

    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(address => bool) public investorToExerciseStatus;
    mapping(Periodicity => uint256) internal periodicityToSeconds;

    ///////////////////
    // Modifiers //////
    ///////////////////
    modifier investorExists() {
        address assetAddress = IParameters(exerciseParameters)
            .getAssetAddress();
        (bool status, ) = IAsset(assetAddress).tokenHolderExists(msg.sender);
        if (!status) {
            revert Token__InvestorDoesNotExist();
        }
        _;
    }

    modifier alreadyExercised() {
        if (investorToExerciseStatus[msg.sender]) {
            revert Token__OptionAlreadyExercised();
        }
        _;
    }

    modifier expirationCheck() {
        if (exerciseOptionStyle == Exercise_Option_Style.AMERICAN) {
            if (block.timestamp > expirationDate + AVERAGE_SECONDS_IN_A_DAY) {
                revert Token__AmericanExerciseOptionExpired();
            }
        } else if (exerciseOptionStyle == Exercise_Option_Style.EUROPEAN) {
            if (
                expirationDate - AVERAGE_SECONDS_IN_A_DAY > block.timestamp ||
                block.timestamp > expirationDate + AVERAGE_SECONDS_IN_A_DAY
            ) {
                revert Token__InvalidExerciseOfEuropeanOption();
            }
        } else if (exerciseOptionStyle == Exercise_Option_Style.BERMUDAN) {
            if (block.timestamp < startDate) {
                revert Token__PrematureExerciseAttempt();
            } else if (
                block.timestamp > expirationDate + AVERAGE_SECONDS_IN_A_DAY
            ) {
                revert Token__BermudanExerciseOptionExpired();
            }
            if (block.timestamp < expirationDate - AVERAGE_SECONDS_IN_A_DAY) {
                uint256 duration = (
                    ((block.timestamp - startDate) /
                        periodicityToSeconds[periodicity])
                ) *
                    periodicityToSeconds[periodicity] +
                    startDate;
                if (
                    duration - AVERAGE_SECONDS_IN_A_DAY > block.timestamp ||
                    block.timestamp > duration + AVERAGE_SECONDS_IN_A_DAY
                ) {
                    revert Token__InvalidExerciseOfBermudanOption();
                }
            }
        }
        _;
    }

    constructor(
        Exercise_Option_Style _exerciseOptionStyle,
        uint256 _expirationDate,
        uint256 _startDate,
        Periodicity _periodicity,
        address _parameters
    ) {
        exerciseOptionStyle = _exerciseOptionStyle;
        require(
            _expirationDate > block.timestamp,
            "Expiration date cannot be less than current time"
        );
        expirationDate = _expirationDate;
        exerciseParameters = _parameters;
        if (_exerciseOptionStyle == Exercise_Option_Style.BERMUDAN) {
            require(
                _startDate >= block.timestamp && _startDate < _expirationDate,
                "Start date cannot be less than current time and greater than expiration date"
            );
            startDate = _startDate;
            periodicity = _periodicity;
            periodicityToSeconds[Periodicity.DAILY] = AVERAGE_SECONDS_IN_A_DAY;
            periodicityToSeconds[
                Periodicity.SEMIMONTHLY
            ] = AVERAGE_SECONDS_IN_SEMI_MONTH;
            periodicityToSeconds[
                Periodicity.WEEKLY
            ] = AVERAGE_SECONDS_IN_A_WEEK;
            periodicityToSeconds[
                Periodicity.MONTHLY
            ] = AVERAGE_SECONDS_IN_A_MONTH;
            periodicityToSeconds[
                Periodicity.ANNUALY
            ] = AVERAGE_SECONDS_IN_A_YEAR;
        }
    }

    function exercise() public investorExists alreadyExercised expirationCheck {
        investorToExerciseStatus[msg.sender] = true;
    }
}
