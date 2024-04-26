// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.17;

import "../IParameters.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract DELIVERY {
    ///////////////////
    // Errors /////////
    ///////////////////
    error Token__InputParameterIsZero();
    error Token__InputAddressIsZero();
    error Token__ExchangeFailed();
    error Token__InsufficientTokenBalance();
    error Token__InsufficientTokenAllowance();
    error Token__TokenIsNotPhysicallyDeliverable();
    error Token__TokenIsNotCashDeliverable();
    // error Token__TokenIsDeliverable();
    error Token__DeliveryMethodIsNotElectable();

    ///////////////////
    // Enums //////////
    ///////////////////
    enum Delivery {
        PHYSICAL,
        CASH,
        // NON_DELIVERABLE,
        ELECT_AT_EXERCISE
    }

    ///////////////////
    // Structs ////////
    ///////////////////
    struct DeliveryReceipt {
        uint256 receiptNumber;
        uint256 date;
        address receiver;
        address deliverer;
        uint256 amountDelivered;
        bytes delivererSignature;
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify the delivery state of the token
    Delivery public deliveryState;
    // Set to the address of the parameters contract
    address public parameters;

    ///////////////////
    // Mappings ///////
    ///////////////////
    mapping(address => mapping(address => bool))
        public senderToReceiverToDeliveryStatus;
    mapping(address => DeliveryReceipt) public receiverToDeliveryReceipt;

    ///////////////////
    // Modifiers //////
    ///////////////////
    modifier isNonZero(uint256 _input) {
        if (_input == 0) {
            revert Token__InputParameterIsZero();
        }
        _;
    }

    modifier addressIsNonZero(address _input) {
        if (_input == address(0)) {
            revert Token__InputAddressIsZero();
        }
        _;
    }

    modifier hasSufficientBalance(uint256 _amount, address _token) {
        if (_amount > IERC20(_token).balanceOf(msg.sender)) {
            revert Token__InsufficientTokenBalance();
        }
        _;
    }

    modifier hasSufficientAllowance(uint256 _amount, address _token) {
        if (_amount > IERC20(_token).allowance(msg.sender, address(this))) {
            revert Token__InsufficientTokenAllowance();
        }
        _;
    }

    modifier isPhysicallyDeliverable() {
        if (deliveryState != Delivery.PHYSICAL) {
            revert Token__TokenIsNotPhysicallyDeliverable();
        }
        _;
    }

    modifier isCashDeliverable() {
        if (deliveryState != Delivery.CASH) {
            revert Token__TokenIsNotCashDeliverable();
        }
        _;
    }

    // modifier isNonDeliverable() {
    //     if (deliveryState != Delivery.NON_DELIVERABLE) {
    //         revert Token__TokenIsDeliverable();
    //     }
    //     _;
    // }

    modifier isDeliveryMethodElectable() {
        if (deliveryState != Delivery.ELECT_AT_EXERCISE) {
            revert Token__DeliveryMethodIsNotElectable();
        }
        _;
    }

    ///////////////////
    // Functions //////
    ///////////////////
    constructor(Delivery _deliveryState, address _parameters) {
        deliveryState = _deliveryState;
        parameters = _parameters;
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

    function physicallyDeliver(
        uint256 _receiptNumber,
        uint256 _date,
        address _receiver,
        uint256 _amountDelivered,
        bytes memory _delivererSignature
    ) internal isPhysicallyDeliverable {
        bytes32 dataHash = keccak256(
            abi.encode(
                _receiptNumber,
                _date,
                _receiver,
                msg.sender,
                _amountDelivered
            )
        );
        bytes32 prefixedHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", dataHash)
        );
        address recovered = getRecoveredAddress(
            _delivererSignature,
            prefixedHash
        );
        require(
            recovered == msg.sender,
            "The deliverer is not the transaction sender"
        );
        require(
            !senderToReceiverToDeliveryStatus[msg.sender][_receiver],
            "Underlying asset already delivered"
        );
        receiverToDeliveryReceipt[_receiver] = DeliveryReceipt(
            _receiptNumber,
            _date,
            _receiver,
            msg.sender,
            _amountDelivered,
            _delivererSignature
        );
        senderToReceiverToDeliveryStatus[msg.sender][_receiver] = true;
    }

    function physicallyDeliver(
        address _token,
        uint256 _amount,
        address _receiver
    )
        internal
        isPhysicallyDeliverable
        addressIsNonZero(_token)
        isNonZero(_amount)
        addressIsNonZero(_receiver)
        hasSufficientBalance(_amount, _token)
        hasSufficientAllowance(_amount, _token)
    {
        require(
            !senderToReceiverToDeliveryStatus[msg.sender][_receiver],
            "Underlying asset already delivered"
        );
        bool success = IERC20(_token).transferFrom(
            msg.sender,
            _receiver,
            _amount
        );
        if (!success) {
            revert Token__ExchangeFailed();
        }
        senderToReceiverToDeliveryStatus[msg.sender][_receiver] = true;
    }

    function cashDeliver(
        uint256 _amount,
        address _receiver
    )
        internal
        isCashDeliverable
        isNonZero(_amount)
        addressIsNonZero(_receiver)
        hasSufficientBalance(
            _amount,
            IParameters(parameters).getPaymentTokenAddress()
        )
        hasSufficientAllowance(
            _amount,
            IParameters(parameters).getPaymentTokenAddress()
        )
    {
        require(
            !senderToReceiverToDeliveryStatus[msg.sender][_receiver],
            "Underlying asset already delivered"
        );
        address paymentToken = IParameters(parameters).getPaymentTokenAddress();
        bool success = IERC20(paymentToken).transferFrom(
            msg.sender,
            _receiver,
            _amount
        );
        if (!success) {
            revert Token__ExchangeFailed();
        }
        senderToReceiverToDeliveryStatus[msg.sender][_receiver] = true;
    }

    // function nonDeliver(
    //     address _receiver
    // ) public isNonDeliverable addressIsNonZero(_receiver) {
    //     require(
    //         !receiverToDeliveryStatus[_receiver],
    //         "Underlying asset already delivered"
    //     );
    //     receiverToDeliveryStatus[_receiver] = true;
    // }

    function electDeliveryMethod(
        Delivery _deliveryState
    ) public isDeliveryMethodElectable {
        deliveryState = _deliveryState;
    }
}
