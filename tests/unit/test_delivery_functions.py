from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Parameters,
    DELIVERY,
    Asset,
    ERC20Mock,
    exceptions,
    accounts,
    config,
)
import pytest
from datetime import datetime
from eth_abi import encode_abi
from eth_account.messages import encode_defunct
from eth_account import Account
from web3 import Web3


def test_can_physically_deliver():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1000
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    delivery_state = 0
    delivery = DELIVERY.deploy(delivery_state, parameters.address, {"from": account1})
    # Act
    receipt_number = 1947
    date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    receiver = account
    amount_delivered = 1000
    encoded_message = encode_abi(
        ["uint256", "uint256", "address", "address", "uint256"],
        [receipt_number, date, receiver.address, account1.address, amount_delivered],
    )
    hashed_message = Web3.keccak(encoded_message)
    msg = encode_defunct(hexstr=str(hashed_message.hex()))
    signedObject = Account.sign_message(msg, config["wallets"]["from_key"])
    deliverer_signature = signedObject.signature
    delivery.physicallyDeliver(
        receipt_number,
        date,
        receiver,
        amount_delivered,
        deliverer_signature,
        {"from": account1},
    )
    # Assert
    assert delivery.receiverToDeliveryStatus(account) == True
    # Checking 'Physically Deliverable' Condition
    # ---------------------------------------------
    delivery1 = DELIVERY.deploy(1, parameters.address, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        delivery1.physicallyDeliver(
            receipt_number,
            date,
            receiver,
            amount_delivered,
            deliverer_signature,
            {"from": account1},
        )
    # ---------------------------------------------


def test_can_physically_deliver_tokenized_assets():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1000
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    delivery_state = 0
    delivery = DELIVERY.deploy(delivery_state, parameters.address, {"from": account1})
    eth = ERC20Mock.deploy({"from": account})
    supply = 1e6
    amount = 100
    # Checking 'Has Sufficient Balance' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.physicallyDeliver(
            eth,
            amount,
            account2,
            {"from": account},
        )
    # ---------------------------------------------
    eth.mint(account, supply, {"from": account})
    # Checking 'Has Sufficient Allowance' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.physicallyDeliver(
            eth,
            amount,
            account2,
            {"from": account},
        )
    # ---------------------------------------------
    eth.approve(delivery, amount * 2, {"from": account})
    # Act
    # Checking 'Address is Non-Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.physicallyDeliver(
            "0x0000000000000000000000000000000000000000",
            amount,
            account2,
            {"from": account},
        )
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.physicallyDeliver(
            eth,
            amount,
            "0x0000000000000000000000000000000000000000",
            {"from": account},
        )
    # ---------------------------------------------
    # Checking 'Amount is Non Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.physicallyDeliver(
            eth,
            0,
            account2,
            {"from": account},
        )
    # ---------------------------------------------
    delivery.physicallyDeliver(eth, amount, account2, {"from": account})
    # Assert
    assert eth.balanceOf(account) == supply - amount
    assert eth.balanceOf(account2) == amount
    # Checking 'Physically Deliverable' Condition
    # ---------------------------------------------
    delivery1 = DELIVERY.deploy(1, parameters.address, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        delivery1.physicallyDeliver(eth, amount, account2, {"from": account})
    # ---------------------------------------------
    # Checking 'Already Delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.physicallyDeliver(
            eth,
            amount,
            account2,
            {"from": account},
        )
    # ---------------------------------------------


def test_can_cash_deliver():
    # Arrange
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1000
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    delivery_state = 1
    delivery = DELIVERY.deploy(delivery_state, parameters.address, {"from": account1})
    amount = 100
    supply = 1e12
    # Checking 'Has Sufficient Balance' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.cashDeliver(
            supply * 2,
            account2,
            {"from": account1},
        )
    # ---------------------------------------------
    # Checking 'Has Sufficient Allowance' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.cashDeliver(
            amount,
            account2,
            {"from": account1},
        )
    # ---------------------------------------------
    payment_token.approve(delivery, amount * 2, {"from": account1})
    # Act
    # Checking 'Address is Non-Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.cashDeliver(
            amount,
            "0x0000000000000000000000000000000000000000",
            {"from": account1},
        )
    # ---------------------------------------------
    # Checking 'Amount is Non Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.cashDeliver(
            0,
            account2,
            {"from": account1},
        )
    # ---------------------------------------------
    delivery.cashDeliver(amount, account2, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account1) == supply - amount
    assert payment_token.balanceOf(account2) == amount
    # Checking 'Cash Deliverable' Condition
    # ---------------------------------------------
    delivery1 = DELIVERY.deploy(0, parameters.address, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        delivery1.cashDeliver(amount, account2, {"from": account1})
    # ---------------------------------------------
    # Checking 'Already Delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        delivery.cashDeliver(
            amount,
            account2,
            {"from": account1},
        )
    # ---------------------------------------------


def test_can_elect_delivery_option():
    # Arrange
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1000
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    delivery_state = 2
    delivery = DELIVERY.deploy(delivery_state, parameters.address, {"from": account1})
    # Act
    amount = 100
    supply = 1e12
    new_delivery_state = 1
    delivery.electDeliveryMethod(new_delivery_state, {"from": account1})
    payment_token.approve(delivery, amount * 2, {"from": account1})
    delivery.cashDeliver(amount, account2, {"from": account1})
    # Assert
    delivery.deliveryState() == new_delivery_state
    assert payment_token.balanceOf(account1) == supply - amount
    assert payment_token.balanceOf(account2) == amount
    assert delivery.receiverToDeliveryStatus(account2) == True
    # Checking 'Delivery Method Electable' Condition
    # ---------------------------------------------
    delivery1 = DELIVERY.deploy(0, parameters.address, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        delivery1.electDeliveryMethod(new_delivery_state, {"from": account1})
    # ---------------------------------------------
