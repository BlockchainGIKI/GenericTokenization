// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.17;

import {FuturesAssets} from "./Features/UnderlyingAssets.sol";
import "./Features/DELIVERY.sol";
import "./Features/STANDARD.sol";
import "./IAsset.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract FUTURES is FuturesAssets, DELIVERY, STANDARD, Ownable {
    ///////////////////
    // Errors /////////
    ///////////////////
    error FUTURES__CallerIsNotTheOwner();
    error FUTURES__FutureIsStandardized();

    ///////////////////
    // Enums //////////
    ///////////////////
    enum Futures {
        FINANCIAL,
        COMMODITIES
    }

    ///////////////////
    // Struct /////////
    ///////////////////
    struct FuturesConfigurations {
        Futures _futureState;
        FinancialUnderlying _financialUnderlying;
        CommoditiesUnderlying _commoditiesUnderlying;
        Delivery _deliveryState;
        Standard _standardState;
    }

    struct FuturesParams {
        uint256 _strikePrice;
        uint256 _contractSize;
        uint256 _spotPrice;
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify the type of future
    Futures public futureState;
    // Used to specify the expiration date of the futures token
    uint256 public expirationDate;
    // Refers to the strike price of the future
    uint256 public strikePrice;
    // Refers to the size of the futures contract
    uint256 public contractSize;
    // Refers to the market price of the underlying set by the options writer or OCC or exchanges
    uint256 public spotPrice;

    ////////////////////
    // Constants ///////
    ///////////////////
    uint256 internal constant AVERAGE_SECONDS_IN_A_DAY = 86400;

    ///////////////////
    // Modifiers //////
    ///////////////////
    modifier isNonStandardized() {
        if (standardState != Standard.NON_STANDARDIZED) {
            revert FUTURES__FutureIsStandardized();
        }
        _;
    }

    ///////////////////
    // Functions //////
    ///////////////////
    constructor(
        FuturesConfigurations memory config,
        FuturesParams memory params,
        uint256 _expirationDate,
        address _parameters
    )
        FuturesAssets(
            config._financialUnderlying,
            config._commoditiesUnderlying
        )
        DELIVERY(config._deliveryState, _parameters)
        STANDARD(config._standardState)
    {
        futureState = config._futureState;
        expirationDate = _expirationDate;
        strikePrice = params._strikePrice;
        contractSize = params._contractSize;
        spotPrice = params._spotPrice;
    }

    function call(address _receiver) internal {
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        (bool status, ) = asset.tokenHolderExists(_receiver);
        require(
            status &&
                block.timestamp >= expirationDate - AVERAGE_SECONDS_IN_A_DAY &&
                !senderToReceiverToDeliveryStatus[msg.sender][_receiver],
            "Receiver is not a token holder or Future not expired or Underlying already delivered"
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

    function deliver(
        uint256 _receiptNumber,
        uint256 _date,
        address _receiver,
        bytes memory _delivererSignature
    ) external onlyOwner {
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        call(_receiver);
        physicallyDeliver(
            _receiptNumber,
            _date,
            _receiver,
            asset.balanceOf(_receiver) * contractSize,
            _delivererSignature
        );
    }

    function deliver(address _token, address _receiver) external onlyOwner {
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        call(_receiver);
        physicallyDeliver(
            _token,
            asset.balanceOf(_receiver) * contractSize,
            _receiver
        );
    }

    function deliver(address _receiver) external onlyOwner {
        IAsset asset = IAsset(IParameters(parameters).getAssetAddress());
        uint256 amount;
        (bool status, ) = asset.tokenHolderExists(_receiver);
        require(
            status &&
                block.timestamp >= expirationDate - AVERAGE_SECONDS_IN_A_DAY &&
                !senderToReceiverToDeliveryStatus[msg.sender][_receiver],
            "Receiver is not a token holder or Current time < delivery date or Underlying already delivered"
        );
        if (spotPrice <= strikePrice) {
            amount = (strikePrice - spotPrice) * asset.balanceOf(_receiver);
            address paymentToken = IParameters(parameters)
                .getPaymentTokenAddress();
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
        } else {
            amount = (spotPrice - strikePrice) * asset.balanceOf(_receiver);
            cashDeliver(amount, _receiver);
        }
    }

    function modifySpotPrice(uint256 _spotPrice) external onlyOwner {
        require(
            block.timestamp <= expirationDate - AVERAGE_SECONDS_IN_A_DAY,
            "Future has expired"
        );
        spotPrice = _spotPrice;
    }

    function modifyStrikePrice(
        uint256 _strikePrice
    ) external onlyOwner isNonStandardized {
        require(
            block.timestamp <= expirationDate - AVERAGE_SECONDS_IN_A_DAY,
            "Future has expired"
        );
        strikePrice = _strikePrice;
    }

    function modifyContractSize(
        uint256 _contractSize
    ) external onlyOwner isNonStandardized {
        require(
            block.timestamp <= expirationDate + AVERAGE_SECONDS_IN_A_DAY,
            "Future has expired"
        );
        contractSize = _contractSize;
    }
}
