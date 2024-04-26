// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.17;

import "./Features/EXERCISE.sol";
import {OptionAssets} from "./Features/UnderlyingAssets.sol";
import "./Features/DELIVERY.sol";
import "./Features/STANDARD.sol";
import "./IAsset.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract OPTIONS is EXERCISE, OptionAssets, DELIVERY, STANDARD, Ownable {
    ///////////////////
    // Errors /////////
    ///////////////////
    error OPTIONS__CallerIsNotTheOwner();
    error OPTIONS__OptionIsStandardized();

    ///////////////////
    // Enums //////////
    ///////////////////
    enum Options {
        CALL,
        PUT
    }

    ///////////////////
    // Struct /////////
    ///////////////////
    struct OptionsConfigurations {
        Options _optionsState;
        Exercise_Option_Style _exerciseOptionStyle;
        Periodicity _periodicity;
        Underlying _underlyingAsset;
        Delivery _deliveryState;
        Standard _standardState;
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify the type of option
    Options public optionState;
    // Refers to the strike price of the option
    uint256 public strikePrice;
    // Refers to the size of the options contract
    uint256 public contractSize;
    // Refers to the market price of the underlying set by the options writer or OCC or exchanges
    uint256 public spotPrice;

    ///////////////////
    // Modifiers //////
    ///////////////////
    modifier isNonStandardized() {
        if (standardState != Standard.NON_STANDARDIZED) {
            revert OPTIONS__OptionIsStandardized();
        }
        _;
    }

    ///////////////////
    // Functions //////
    ///////////////////
    constructor(
        OptionsConfigurations memory config,
        uint256 _expirationDate,
        uint256 _startDate,
        address _parameters
    )
        EXERCISE(
            config._exerciseOptionStyle,
            _expirationDate,
            _startDate,
            config._periodicity,
            _parameters
        )
        OptionAssets(config._underlyingAsset)
        DELIVERY(config._deliveryState, _parameters)
        STANDARD(config._standardState)
    {
        optionState = config._optionsState;
    }

    function call(address _receiver) internal {
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        (bool status, ) = asset.tokenHolderExists(_receiver);
        require(
            status &&
                investorToExerciseStatus[_receiver] &&
                !senderToReceiverToDeliveryStatus[msg.sender][_receiver],
            "Receiver is not a token holder or Receiver did not exercise option or Underlying already delivered"
        );
        uint256 amount = asset.balanceOf(_receiver) *
            strikePrice *
            contractSize;
        require(
            IERC20(paymentToken).balanceOf(_receiver) >= amount &&
                IERC20(paymentToken).allowance(_receiver, address(this)) >=
                amount,
            "Insufficient balance or allowance"
        );
        bool success = IERC20(paymentToken).transferFrom(
            _receiver,
            msg.sender,
            amount
        );
        if (!success) {
            revert Token__ExchangeFailed();
        }
    }

    function put() internal {
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        (bool status, ) = asset.tokenHolderExists(msg.sender);
        require(
            status &&
                investorToExerciseStatus[msg.sender] &&
                !senderToReceiverToDeliveryStatus[msg.sender][owner()],
            "Caller does not own options or Caller did not exercise option or Underlying already delivered"
        );
        uint256 amount = asset.balanceOf(msg.sender) *
            strikePrice *
            contractSize;
        require(
            IERC20(paymentToken).balanceOf(owner()) >= amount &&
                IERC20(paymentToken).allowance(owner(), address(this)) >=
                amount,
            "Insufficient balance or allowance"
        );
        bool success = IERC20(paymentToken).transferFrom(
            owner(),
            msg.sender,
            amount
        );
        if (!success) {
            revert Token__ExchangeFailed();
        }
    }

    function deliver(
        uint256 _receiptNumber,
        uint256 _date,
        address _receiver,
        bytes memory _delivererSignature
    ) external {
        if (optionState == Options.CALL && msg.sender != owner()) {
            revert OPTIONS__CallerIsNotTheOwner();
        }
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        if (optionState == Options.CALL) {
            call(_receiver);
            physicallyDeliver(
                _receiptNumber,
                _date,
                _receiver,
                asset.balanceOf(_receiver) * contractSize,
                _delivererSignature
            );
        } else {
            put();
            physicallyDeliver(
                _receiptNumber,
                _date,
                owner(),
                asset.balanceOf(_receiver) * contractSize,
                _delivererSignature
            );
        }
    }

    function deliver(address _token, address _receiver) external {
        if (optionState == Options.CALL && msg.sender != owner()) {
            revert OPTIONS__CallerIsNotTheOwner();
        }
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        if (optionState == Options.CALL) {
            call(_receiver);
            physicallyDeliver(
                _token,
                asset.balanceOf(_receiver) * contractSize,
                _receiver
            );
        } else {
            put();
            physicallyDeliver(
                _token,
                asset.balanceOf(_receiver) * contractSize,
                _receiver
            );
        }
    }

    function deliver(address _receiver) external {
        if (optionState == Options.CALL && msg.sender != owner()) {
            revert OPTIONS__CallerIsNotTheOwner();
        }
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        uint256 amount;
        if (optionState == Options.CALL) {
            (bool status, ) = asset.tokenHolderExists(_receiver);
            require(
                status &&
                    investorToExerciseStatus[_receiver] &&
                    !senderToReceiverToDeliveryStatus[msg.sender][_receiver],
                "Receiver is not a token holder or Receiver did not exercise option or Underlying already delivered"
            );
            if (spotPrice <= strikePrice) {
                amount = (strikePrice - spotPrice) * asset.balanceOf(_receiver);
                address paymentToken = IParameters(parameters)
                    .getPaymentTokenAddress();
                require(
                    IERC20(paymentToken).balanceOf(_receiver) >= amount &&
                        IERC20(paymentToken).allowance(
                            _receiver,
                            address(this)
                        ) >=
                        amount,
                    "Insufficient balance or allowance"
                );
                bool success = IERC20(paymentToken).transferFrom(
                    _receiver,
                    msg.sender,
                    amount
                );
                if (!success) {
                    revert Token__ExchangeFailed();
                }
            } else {
                amount = (spotPrice - strikePrice) * asset.balanceOf(_receiver);
                cashDeliver(amount, _receiver);
            }
        } else {
            (bool status, ) = asset.tokenHolderExists(msg.sender);
            require(
                status &&
                    investorToExerciseStatus[msg.sender] &&
                    !senderToReceiverToDeliveryStatus[msg.sender][owner()],
                "Caller does not own options or Caller did not exercise option or Underlying already delivered"
            );
            if (spotPrice >= strikePrice) {
                amount =
                    (spotPrice - strikePrice) *
                    asset.balanceOf(msg.sender);
                address paymentToken = IParameters(parameters)
                    .getPaymentTokenAddress();
                require(
                    IERC20(paymentToken).balanceOf(msg.sender) >= amount &&
                        IERC20(paymentToken).allowance(
                            msg.sender,
                            address(this)
                        ) >=
                        amount,
                    "Insufficient balance or allowance"
                );
                bool success = IERC20(paymentToken).transferFrom(
                    msg.sender,
                    owner(),
                    amount
                );
                if (!success) {
                    revert Token__ExchangeFailed();
                }
            } else {
                amount =
                    (strikePrice - spotPrice) *
                    asset.balanceOf(msg.sender);
                cashDeliver(amount, owner());
            }
        }
    }

    function modifySpotPrice(uint256 _spotPrice) external onlyOwner {
        require(
            block.timestamp <= expirationDate + AVERAGE_SECONDS_IN_A_DAY,
            "Option has expired"
        );
        spotPrice = _spotPrice;
    }

    function modifyStrikePrice(
        uint256 _strikePrice
    ) external onlyOwner isNonStandardized {
        require(
            block.timestamp <= expirationDate + AVERAGE_SECONDS_IN_A_DAY,
            "Option has expired"
        );
        strikePrice = _strikePrice;
    }

    function modifyContractSize(
        uint256 _contractSize
    ) external onlyOwner isNonStandardized {
        require(
            block.timestamp <= expirationDate + AVERAGE_SECONDS_IN_A_DAY,
            "Option has expired"
        );
        contractSize = _contractSize;
    }
}
