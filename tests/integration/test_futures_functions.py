from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Parameters,
    FUTURES,
    Asset,
    ERC20Mock,
    exceptions,
    chain,
    accounts,
    config,
)
import pytest
from datetime import datetime
from eth_abi import encode_abi
from eth_account.messages import encode_defunct
from eth_account import Account
from web3 import Web3


def test_can_physically_deliver_future():
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
    future_state = 0
    financial_underlying = 5
    commodity_underlying = 0
    deliver_state = 0
    standard_state = 0
    strike_price = 100
    contract_size = 100
    spot_price = 75
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    future = FUTURES.deploy(
        (
            future_state,
            financial_underlying,
            commodity_underlying,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        parameters,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    receipt_number = 1947
    date = int(datetime(2024, 3, 13, 12, 42).timestamp())
    receiver = account
    amount_delivered = amount * contract_size
    encoded_message = encode_abi(
        ["uint256", "uint256", "address", "address", "uint256"],
        [receipt_number, date, receiver.address, account1.address, amount_delivered],
    )
    hashed_message = Web3.keccak(encoded_message)
    msg = encode_defunct(hexstr=str(hashed_message.hex()))
    signedObject = Account.sign_message(msg, config["wallets"]["from_key"])
    deliverer_signature = signedObject.signature
    total_payment = amount * strike_price * contract_size
    payment_token.transfer(account, total_payment, {"from": account1})
    payment_token.approve(future, total_payment, {"from": account})
    # Act
    # Checking 'Future Not Expired' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(
            receipt_number, date, receiver, deliverer_signature, {"from": account1}
        )
    # ---------------------------------------------
    chain.sleep(31556952)
    # Checking 'Caller is not Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(
            receipt_number, date, receiver, deliverer_signature, {"from": account}
        )
    # ---------------------------------------------
    future.deliver(
        receipt_number, date, receiver, deliverer_signature, {"from": account1}
    )
    # Assert
    assert future.senderToReceiverToDeliveryStatus(account1, account) == True
    assert future.receiverToDeliveryReceipt(account)[3] == account1
    # Checking 'Receiver not token holder' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(
            receipt_number, date, account2, deliverer_signature, {"from": account1}
        )
    # ---------------------------------------------
    # Checking 'Underlying already delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(
            receipt_number, date, account, deliverer_signature, {"from": account1}
        )
    # ---------------------------------------------


def test_can_physically_deliver_tokenized_assets_for_future():
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
    future_state = 1
    financial_underlying = 0
    commodity_underlying = 8
    deliver_state = 0
    standard_state = 0
    strike_price = 100
    contract_size = 100
    spot_price = 75
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    future = FUTURES.deploy(
        (
            future_state,
            financial_underlying,
            commodity_underlying,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        parameters,
        {"from": account1},
    )
    eth = ERC20Mock.deploy({"from": account1})
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    eth.mint(account1, amount * contract_size, {"from": account1})
    total_payment = amount * strike_price * contract_size
    payment_token.transfer(account, total_payment, {"from": account1})
    payment_token.approve(future, total_payment, {"from": account})
    eth.approve(future, amount * contract_size, {"from": account1})
    # Act
    # Checking 'Future Not Expired' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(eth, account, {"from": account1})
    # ---------------------------------------------
    chain.sleep(31556952)
    # Checking 'Caller is not Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(eth, account, {"from": account})
    # ---------------------------------------------
    future.deliver(eth, account, {"from": account1})
    # Assert
    assert future.senderToReceiverToDeliveryStatus(account1, account) == True
    assert eth.balanceOf(account1) == 0
    assert eth.balanceOf(account) == amount * contract_size
    # Checking 'Receiver not token holder' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(eth, account2, {"from": account1})
    # ---------------------------------------------
    # Checking 'Underlying already delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(eth, account, {"from": account1})
    # ---------------------------------------------


def test_can_cash_deliver_future():
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
    deliver_state = 1
    standard_state = 1
    strike_price = 75
    contract_size = 100
    spot_price = 100
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    future_state = 1
    financial_underlying = 0
    commodity_underlying = 8
    future = FUTURES.deploy(
        (
            future_state,
            financial_underlying,
            commodity_underlying,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        parameters,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    payment_token.approve(
        future, amount * (spot_price - strike_price), {"from": account1}
    )
    # Act
    # Checking 'Future Not Expired' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(account, {"from": account1})
    # ---------------------------------------------
    chain.sleep(31556952)
    # Checking 'Caller is not Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(account, {"from": account})
    # ---------------------------------------------
    future.deliver(account, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account1) == 1e12 - amount * (
        spot_price - strike_price
    )
    assert payment_token.balanceOf(account) == amount * (spot_price - strike_price)
    # Checking 'Receiver not token holder' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(account2, {"from": account1})
    # ---------------------------------------------
    # Checking 'Underlying already delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.deliver(account2, {"from": account1})
    # ---------------------------------------------


def test_can_modify_strke_price():
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
    deliver_state = 1
    standard_state = 1
    strike_price = 75
    contract_size = 100
    spot_price = 100
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    future_state = 1
    financial_underlying = 0
    commodity_underlying = 8
    future = FUTURES.deploy(
        (
            future_state,
            financial_underlying,
            commodity_underlying,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        parameters,
        {"from": account1},
    )
    future1 = FUTURES.deploy(
        (
            future_state,
            financial_underlying,
            commodity_underlying,
            deliver_state,
            0,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        parameters,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    strike_price = 120
    payment_token.transfer(
        account, amount * (strike_price - spot_price), {"from": account1}
    )
    payment_token.approve(
        future, amount * (strike_price - spot_price), {"from": account}
    )
    # Act
    # Checking 'Caller is not Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.modifyStrikePrice(strike_price, {"from": account})
    # ---------------------------------------------
    # Checking 'Future Standardized' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future1.modifyStrikePrice(strike_price, {"from": account1})
    # ---------------------------------------------
    future.modifyStrikePrice(strike_price, {"from": account1})
    chain.sleep(31556952)
    future.deliver(account, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account) == 0
    assert payment_token.balanceOf(account1) == 1e12
    # Checking 'Future Expired' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        future.modifyStrikePrice(strike_price, {"from": account1})
    # ---------------------------------------------
