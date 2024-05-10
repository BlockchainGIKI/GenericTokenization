from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Parameters,
    OPTIONS,
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


def test_can_physically_deliver_call_option():
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
    options_state = 0
    exercise_option_style = 0
    periodicity = 3
    underlying_asset = 0
    deliver_state = 0
    standard_state = 0
    strike_price = 100
    contract_size = 100
    spot_price = 75
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    start_date = 1947
    option = OPTIONS.deploy(
        (
            options_state,
            exercise_option_style,
            periodicity,
            underlying_asset,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        start_date,
        parameters.address,
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
    payment_token.approve(option, total_payment, {"from": account})
    # Act
    # Checking 'Receiver did not exercise option' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(
            receipt_number, date, account, deliverer_signature, {"from": account1}
        )
    # ---------------------------------------------
    option.exercise({"from": account})
    # Checking 'Caller is not Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(
            receipt_number, date, receiver, deliverer_signature, {"from": account}
        )
    # ---------------------------------------------
    option.deliver(
        receipt_number, date, receiver, deliverer_signature, {"from": account1}
    )
    # Assert
    assert option.senderToReceiverToDeliveryStatus(account1, account) == True
    assert option.receiverToDeliveryReceipt(account)[3] == account1
    # Checking 'Receiver not token holder' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(
            receipt_number, date, account2, deliverer_signature, {"from": account1}
        )
    # ---------------------------------------------
    # Checking 'Underlying already delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(
            receipt_number, date, account, deliverer_signature, {"from": account1}
        )
    # ---------------------------------------------


def test_can_physically_deliver_put_option():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    account3 = get_account(3)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1000
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account3}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account3}
    )
    options_state = 1
    exercise_option_style = 0
    periodicity = 3
    underlying_asset = 0
    deliver_state = 0
    standard_state = 0
    strike_price = 100
    contract_size = 100
    spot_price = 75
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    start_date = 1947
    option = OPTIONS.deploy(
        (
            options_state,
            exercise_option_style,
            periodicity,
            underlying_asset,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        start_date,
        parameters.address,
        {"from": account},
    )
    amount = 100
    asset.transfer(account1, amount, {"from": account3})
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
    payment_token.transfer(account, total_payment, {"from": account3})
    payment_token.approve(option, total_payment, {"from": account})
    null_address = "0x0000000000000000000000000000000000000000"
    # Act
    # Checking 'Caller did not exercise option' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(
            receipt_number, date, null_address, deliverer_signature, {"from": account1}
        )
    # ---------------------------------------------
    option.exercise({"from": account1})
    option.deliver(
        receipt_number, date, receiver, deliverer_signature, {"from": account1}
    )
    # Assert
    assert option.senderToReceiverToDeliveryStatus(account1, account) == True
    assert option.receiverToDeliveryReceipt(account)[3] == account1
    # Checking 'Sender not token holder' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(
            receipt_number, date, null_address, deliverer_signature, {"from": account2}
        )
    # ---------------------------------------------
    # Checking 'Underlying already delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(
            receipt_number, date, null_address, deliverer_signature, {"from": account1}
        )
    # ---------------------------------------------


def test_can_physically_deliver_tokenized_assets_for_call_option():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    account3 = get_account(3)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1000
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account3}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account3}
    )
    options_state = 0
    exercise_option_style = 0
    periodicity = 3
    underlying_asset = 0
    deliver_state = 0
    standard_state = 0
    strike_price = 100
    contract_size = 100
    spot_price = 75
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    start_date = 1947
    option = OPTIONS.deploy(
        (
            options_state,
            exercise_option_style,
            periodicity,
            underlying_asset,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        start_date,
        parameters.address,
        {"from": account1},
    )
    eth = ERC20Mock.deploy({"from": account3})
    supply = 1e6
    amount = 100
    asset.transfer(account, amount, {"from": account3})
    eth.mint(account1, amount * contract_size, {"from": account3})
    total_payment = amount * strike_price * contract_size
    payment_token.transfer(account, total_payment, {"from": account3})
    payment_token.approve(option, total_payment, {"from": account})
    eth.approve(option, amount * contract_size, {"from": account1})
    # Act
    # Checking 'Receiver did not exercise option' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(eth, account, {"from": account1})
    # ---------------------------------------------
    option.exercise({"from": account})
    # Checking 'Caller is not Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(eth, account, {"from": account})
    # ---------------------------------------------
    option.deliver(eth, account, {"from": account1})
    # Assert
    assert option.senderToReceiverToDeliveryStatus(account1, account) == True
    assert eth.balanceOf(account1) == 0
    assert eth.balanceOf(account) == amount * contract_size
    # Checking 'Receiver not token holder' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(eth, account2, {"from": account1})
    # ---------------------------------------------
    # Checking 'Underlying already delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(eth, account, {"from": account1})
    # ---------------------------------------------


def test_can_physically_deliver_tokenized_assets_for_put_option():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    account3 = get_account(3)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1000
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account3}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account3}
    )
    options_state = 1
    exercise_option_style = 0
    periodicity = 3
    underlying_asset = 0
    deliver_state = 0
    standard_state = 0
    strike_price = 100
    contract_size = 100
    spot_price = 75
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    start_date = 1947
    option = OPTIONS.deploy(
        (
            options_state,
            exercise_option_style,
            periodicity,
            underlying_asset,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        start_date,
        parameters.address,
        {"from": account1},
    )
    eth = ERC20Mock.deploy({"from": account3})
    amount = 100
    asset.transfer(account, amount, {"from": account3})
    eth.mint(account, amount * contract_size, {"from": account3})
    total_payment = amount * strike_price * contract_size
    payment_token.transfer(account1, total_payment, {"from": account3})
    payment_token.approve(option, total_payment, {"from": account1})
    eth.approve(option, amount * contract_size, {"from": account})
    null_address = "0x0000000000000000000000000000000000000000"
    # Act
    # Checking 'Receiver did not exercise option' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(eth, null_address, {"from": account})
    # ---------------------------------------------
    option.exercise({"from": account})
    option.deliver(eth, null_address, {"from": account})
    # Assert
    assert option.senderToReceiverToDeliveryStatus(account, account1) == True
    assert eth.balanceOf(account) == 0
    assert eth.balanceOf(account1) == amount * contract_size
    # Checking 'Sender not token holder' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(eth, null_address, {"from": account2})
    # ---------------------------------------------
    # Checking 'Underlying already delivered' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        option.deliver(eth, account, {"from": account1})
    # ---------------------------------------------


def test_can_cash_deliver_call_option():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    account3 = get_account(3)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1000
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account3}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account3}
    )
    options_state = 0
    exercise_option_style = 0
    periodicity = 3
    underlying_asset = 0
    deliver_state = 1
    standard_state = 1
    strike_price = 75
    contract_size = 100
    spot_price = 100
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    start_date = 1947
    option = OPTIONS.deploy(
        (
            options_state,
            exercise_option_style,
            periodicity,
            underlying_asset,
            deliver_state,
            standard_state,
        ),
        (strike_price, contract_size, spot_price),
        expiration_date,
        start_date,
        parameters.address,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account3})
    payment_token.transfer(
        account1, amount * (spot_price - strike_price), {"from": account3}
    )
    payment_token.approve(
        option, amount * (spot_price - strike_price), {"from": account1}
    )
    option.exercise({"from": account})
    # Act
    option.deliver(account, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account1) == 0
    assert payment_token.balanceOf(account) == amount * (spot_price - strike_price)
    # Changing strike price
    strike_price = 120
    option.modifyStrikePrice(strike_price, {"from": account1})
    asset.transfer(account2, amount, {"from": account3})
    payment_token.transfer(
        account2, amount * (strike_price - spot_price), {"from": account3}
    )
    payment_token.approve(
        option, amount * (strike_price - spot_price), {"from": account2}
    )
    option.exercise({"from": account2})
    # Act
    option.deliver(account2, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account2) == 0
    assert payment_token.balanceOf(account1) == amount * (strike_price - spot_price)
