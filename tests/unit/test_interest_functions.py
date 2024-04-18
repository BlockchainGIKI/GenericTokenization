from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Parameters,
    INTEREST,
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


def test_can_pay_interest_in_perpetuity():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    payment_frequency = 1  # Daily
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    face_value = 100
    interest_rate = 10
    token = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    payment_token.transfer(
        token, (face_value * interest_rate * amount), {"from": account1}
    )
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Act
    token.payInterest(account, {"from": account})
    # Assert
    assert payment_token.balanceOf(account) == (face_value * interest_rate * amount)
    assert token.maturityDate() == maturity_date


def test_can_pay_interest():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    payment_frequency = 1  # Daily
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    face_value = 100
    interest_rate = 10
    token = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    payment_token.transfer(
        token, face_value * interest_rate * amount, {"from": account1}
    )
    chain.sleep(86400)
    chain.mine(1)
    # Act
    token.payInterest(account, {"from": account})
    # Assert
    assert payment_token.balanceOf(account) == face_value * interest_rate * amount
    # Checking 'Investor Already Paid in this Payment Period' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterest(account, {"from": account})
    # Checking Only Owner Condition
    with pytest.raises(exceptions.VirtualMachineError):
        chain.sleep(86400)
        chain.mine(1)
        token.payInterest(account, {"from": account2})
    # Checking 'Investor Exists' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterest(account2, {"from": account})
    # Checking 'Insufficient Balance to Pay' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterest(account, {"from": account})
    # Checking 'Is Payable' Condition
    token1 = INTEREST.deploy(
        0,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterest(account, {"from": account})
    # Checking 'Is Fixed or Variable' Condition
    token2 = INTEREST.deploy(
        payment_frequency,
        5,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterest(account, {"from": account})
    # Checking 'Current Time < Maturity' Condition
    token3 = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        int(datetime(2024, 4, 22, 15, 3).timestamp()),
        face_value,
        interest_rate,
        {"from": account},
    )
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token3.payInterest(account, {"from": account})


def test_can_pay_interest_to_all_token_holders():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 200
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    payment_frequency = 4  # Monthly
    interest_type = 3  # Variable
    maturity_date = int(datetime(2026, 3, 13, 12, 42).timestamp())
    face_value = 100
    interest_rate = 10
    token = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account})
    asset.transfer(account2, amount, {"from": account})
    payment_token.transfer(
        token, (face_value * interest_rate * amount) * 2, {"from": account1}
    )
    token1 = INTEREST.deploy(
        5,
        3,
        parameters,
        int(datetime(2050, 3, 13, 12, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account},
    )
    # Act
    chain.sleep(2629800 + 60 * 60 * 12)
    chain.mine(1)
    token.payInterestToAll({"from": account})
    chain.sleep(31556952)
    chain.mine(1)
    # Assert
    assert payment_token.balanceOf(account) == face_value * interest_rate * amount
    assert payment_token.balanceOf(account2) == face_value * interest_rate * amount
    # Checking 'Insufficient Balance to Pay All Investors' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestToAll({"from": account})
    # Checking 'Only Owner' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestToAll({"from": account1})
    payment_token.transfer(token1, 1e6, {"from": account1})
    token1.payInterestToAll({"from": account})
    assert payment_token.balanceOf(account) == (face_value * interest_rate * amount) * 2
    assert (
        payment_token.balanceOf(account2) == (face_value * interest_rate * amount) * 2
    )
    # Checking 'Is Payable' Condition
    token2 = INTEREST.deploy(
        0,
        interest_type,
        parameters,
        int(datetime(2050, 3, 13, 12, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterestToAll({"from": account})
    # Checking 'Is Fixed or Variable' Condition
    token3 = INTEREST.deploy(
        payment_frequency,
        5,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        chain.sleep(86400)
        chain.mine(1)
        token3.payInterestToAll({"from": account})
    # Checking 'Current Time < Maturity' Condition
    token4 = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        int(datetime(2025, 5, 19, 16, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        chain.sleep(86400 + 60 * 60 * 12)
        chain.mine(1)
        token4.payInterestToAll({"from": account})


def test_can_pay_interest_in_payment_in_kind():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    payment_frequency = 1  # Daily
    interest_type = 5  # Payment in kind
    maturity_date = int(datetime(2026, 3, 13, 12, 42).timestamp())
    face_value = 100
    interest_rate = 100
    token = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth = ERC20Mock.deploy({"from": account})
    supply = 1e6
    amount = 100
    eth.mint(token, supply)
    asset.transfer(account, amount, {"from": account1})
    chain.sleep(86400)
    chain.mine(1)
    # Act
    # Checking 'Only Owner' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKind(
            account.address, eth.address, 100, {"from": account1}
        )
    token.payInterestInPaymentInKind(
        account.address, eth.address, 100, {"from": account}
    )
    # Assert
    assert eth.balanceOf(account) == amount
    assert eth.balanceOf(token) == supply - amount
    # Checking 'Investor Exists' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKind(
            account1.address, eth.address, 100, {"from": account}
        )
    # Checking 'Investor Already Paid' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKind(
            account.address, eth.address, 100, {"from": account}
        )
    chain.sleep(86400)
    chain.mine(1)
    # Checking 'Insufficient Balance' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKind(
            account.address, eth.address, 1e6, {"from": account}
        )
    # Checking 'Is Payment in Kind' Condition
    token1 = INTEREST.deploy(
        payment_frequency,
        4,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token1, supply, {"from": account})
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestInPaymentInKind(
            account.address, eth.address, 100, {"from": account}
        )
    # Checking 'Is Payable' Condition
    token2 = INTEREST.deploy(
        0,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token2, supply, {"from": account})
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterestInPaymentInKind(
            account.address, eth.address, 100, {"from": account}
        )
    # Checking 'Current Time < Maturity' Condition
    token4 = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        int(datetime(2024, 4, 21, 15, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token4, supply, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token4.payInterestInPaymentInKind(
            account.address, eth.address, 100, {"from": account}
        )


def test_can_pay_interest_in_payment_in_kind_to_all():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    payment_frequency = 1  # Daily
    interest_type = 5  # Payment in kind
    maturity_date = int(datetime(2026, 3, 13, 12, 42).timestamp())
    face_value = 100
    interest_rate = 10
    token = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth = ERC20Mock.deploy({"from": account})
    supply = 1e6
    eth.mint(token, supply)
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    asset.transfer(account2, amount, {"from": account1})
    chain.sleep(86400)
    chain.mine(1)
    # Act
    # Checking 'Only Owner' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account1})
    token.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account})
    # Assert
    assert eth.balanceOf(account) == amount
    assert eth.balanceOf(account2) == amount
    assert eth.balanceOf(token) == supply - amount * 2
    # Checking 'Insufficient Balance' Condition
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKindToAll(eth.address, 1e6, {"from": account})
    # Checking 'Is Payment in Kind' Condition
    token1 = INTEREST.deploy(
        payment_frequency,
        4,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token1, supply, {"from": account})
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account})
    # Checking 'Is Payable' Condition
    token2 = INTEREST.deploy(
        0,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token2, supply, {"from": account})
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account})
    # Checking 'Current Time < Maturity' Condition
    token4 = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        int(datetime(2024, 4, 21, 16, 4).timestamp()),
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token4, supply, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token4.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account})


def test_can_pay_interest_in_cash():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    payment_frequency = 1  # Daily
    interest_type = 4  # Cash
    maturity_date = int(datetime(2026, 3, 13, 12, 42).timestamp())
    face_value = 100
    interest_rate = 10
    token = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    chain.sleep(86400)
    chain.mine(1)
    # Act
    receipt_number = 0
    date = int(datetime(2024, 3, 25, 12, 42).timestamp())
    encoded_message = encode_abi(
        ["uint256", "uint256", "address", "uint256"],
        [receipt_number, date, account.address, amount],
    )
    hashed_message = Web3.keccak(encoded_message)
    msg = encode_defunct(hexstr=str(hashed_message.hex()))
    signedObject = Account.sign_message(msg, config["wallets"]["from_key"])
    # Checking 'Only Owner' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInCash(
            receipt_number,
            date,
            account.address,
            amount,
            signedObject.signature,
            {"from": account},
        )
    token.payInterestInCash(
        receipt_number,
        date,
        account.address,
        amount,
        signedObject.signature,
        {"from": account1},
    )
    # Assert
    assert token.investorToPaymentPeriodToReceipt(account, 1)[3] == amount
    assert (
        token.investorToPaymentPeriodToReceipt(account, 1)[4]
        == signedObject.signature.hex()
    )
    # Checking 'Investor Already Paid for this Payment Period' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInCash(
            receipt_number,
            date,
            account.address,
            amount,
            signedObject.signature,
            {"from": account1},
        )
    # Checking 'Investor Exists' Condition
    encoded_message = encode_abi(
        ["uint256", "uint256", "address", "uint256"],
        [receipt_number, date, account2.address, amount],
    )
    hashed_message = Web3.keccak(encoded_message)
    msg = encode_defunct(hexstr=str(hashed_message.hex()))
    signedObject = Account.sign_message(msg, config["wallets"]["from_key"])
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInCash(
            receipt_number,
            date,
            account2.address,
            amount,
            signedObject.signature,
            {"from": account1},
        )
    # Checking 'Signer is not Owner' Condition
    token1 = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account},
    )
    chain.sleep(86400)
    chain.mine(1)
    temp = Account.sign_message(msg, config["wallets"]["from_key"])
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestInCash(
            receipt_number,
            date,
            account.address,
            amount,
            temp.signature,
            {"from": account},
        )
    # Checking 'Interest Type is Cash Payment' Condition
    token2 = INTEREST.deploy(
        payment_frequency,
        1,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterestInCash(
            receipt_number,
            date,
            account.address,
            amount,
            signedObject.signature,
            {"from": account1},
        )
    # Checking 'Token is of Payable Type' Condition
    token3 = INTEREST.deploy(
        0,
        interest_type,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token3.payInterestInCash(
            receipt_number,
            date,
            account.address,
            amount,
            signedObject.signature,
            {"from": account1},
        )
    # Checking 'Current Time is less than Maturity' Condition
    token4 = INTEREST.deploy(
        payment_frequency,
        interest_type,
        parameters,
        int(datetime(2024, 4, 21, 16, 15).timestamp()),
        face_value,
        interest_rate,
        {"from": account1},
    )
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token4.payInterestInCash(
            receipt_number,
            date,
            account.address,
            amount,
            signedObject.signature,
            {"from": account1},
        )
