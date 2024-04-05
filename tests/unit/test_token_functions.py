from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Token,
    ERC20Mock,
    PaymentToken,
    exceptions,
    interface,
    chain,
    accounts,
    config,
)
from datetime import datetime, timedelta
from eth_abi import encode_abi
from eth_account.messages import encode_defunct
from eth_account import Account
from web3 import Web3
import pytest


# def test_can_set_redemption_state():
#     # Arrange
#     account = get_account()
#     # Act
#     token = Token.deploy(
#         "Test",
#         "Test",
#         100,
#         0,
#         1741075174,
#         account,
#         account,
#         100,
#         {"from": account},
#     )
#     # Assert
#     assert token.redemptionState() == 0
#     assert token.buybackDate() == 1741075174
#     with pytest.raises(exceptions.VirtualMachineError):
#         Token.deploy(
#             "Test",
#             "Test",
#             100,
#             0,
#             100,
#             account,
#             account,
#             100,
#             {"from": account},
#         )


# def test_can_add_exchangeable_token():
#     # Arrange
#     account = get_account()
#     account1 = get_account(1)
#     token_name = "Test"
#     token_symbol = "Test"
#     initial_supply = 100
#     redeem_state = 6
#     buyback_date = 1741075174
#     payment_token = account
#     price = 100
#     token = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         redeem_state,
#         buyback_date,
#         payment_token,
#         payment_token,
#         price,
#         {"from": account},
#     )
#     # Act
#     conversion_rate = 100
#     token.addExchangeableToken(account, conversion_rate, {"from": account})
#     # Assert
#     assert token.conversionRate(account) == conversion_rate
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.addExchangeableToken(token, conversion_rate, {"from": account1})
#     token1 = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         3,
#         buyback_date,
#         payment_token,
#         payment_token,
#         price,
#         {"from": account},
#     )
#     with pytest.raises(exceptions.VirtualMachineError):
#         token1.addExchangeableToken(token, conversion_rate, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.addExchangeableToken(account, conversion_rate, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.addExchangeableToken(
#             "0x0000000000000000000000000000000000000000",
#             conversion_rate,
#             {"from": account},
#         )
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.addExchangeableToken(account1, 0, {"from": account})


# def test_can_extend_buyback_date():
#     # Arrange
#     account = get_account()
#     account1 = get_account(1)
#     token_name = "Test"
#     token_symbol = "Test"
#     initial_supply = 100
#     redeem_state = 6
#     buyback_date = 1741075174  # refers to 2025 March 4, 12:59:34 (PKT)
#     payment_token = account
#     price = 100
#     token = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         redeem_state,
#         buyback_date,
#         payment_token,
#         payment_token,
#         price,
#         {"from": account},
#     )
#     # Act
#     token.extendBuybackDate(1772611174, {"from": account})
#     # Assert
#     token.buybackDate() == 1772611174
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.extendBuybackDate(1709301411, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.extendBuybackDate(1772611174, {"from": account1})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.extendBuybackDate(0, {"from": account})
#     token1 = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         0,
#         buyback_date,
#         payment_token,
#         payment_token,
#         price,
#         {"from": account},
#     )
#     with pytest.raises(exceptions.VirtualMachineError):
#         token1.extendBuybackDate(1772611174, {"from": account})


# def test_can_issue_token():
#     # Arrange
#     account = get_account()
#     account1 = get_account(1)
#     token_name = "Test"
#     token_symbol = "Test"
#     initial_supply = 100
#     redeem_state = 6
#     buyback_date = 1741075174  # refers to 2025 March 4, 12:59:34 (PKT)
#     payment_token = account
#     price = 100
#     token = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         redeem_state,
#         buyback_date,
#         payment_token,
#         payment_token,
#         price,
#         {"from": account},
#     )
#     # Act
#     amount = 50
#     token.issueToken(amount, account1, {"from": account})
#     # Assert
#     assert token.getBalance(account1) == amount
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.issueToken(amount, account1, {"from": account1})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.issueToken(0, account1, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.issueToken(100, account1, {"from": account})


# def test_can_exchange_token():
#     # Arrange
#     account = get_account()
#     (payment_token, identityRegistry) = deploy()
#     token_name = "Test"
#     token_symbol = "Test"
#     initial_supply = 100
#     redeem_state = 6
#     buyback_date = 1741075174  # refers to 2025 March 4, 12:59:34 (PKT)
#     price = 100
#     token = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         redeem_state,
#         buyback_date,
#         payment_token,
#         identityRegistry,
#         price,
#         {"from": account},
#     )
#     eth = ERC20Mock.deploy({"from": account})
#     eth.mint(token, 1e18)
#     conversion_rate = 2
#     token.addExchangeableToken(eth, conversion_rate, {"from": account})
#     # Act
#     amount = 100
#     token.issueToken(amount, account, {"from": account})
#     asset = interface.IERC20(token.getAddress())
#     asset.approve(token, amount, {"from": account})
#     # print(token.temp({"from": account}))
#     token.exchangeToken(eth, amount, {"from": account})
#     # Asset
#     assert eth.balanceOf(account) == amount * conversion_rate
#     assert token.getBalance(account) == 0
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.exchangeToken(eth, amount, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token.exchangeToken(account, amount, {"from": account})
#     token1 = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         1,
#         buyback_date,
#         payment_token,
#         identityRegistry,
#         price,
#         {"from": account},
#     )
#     with pytest.raises(exceptions.VirtualMachineError):
#         token1.exchangeToken(eth, amount, {"from": account})


# def test_can_redeem_tokens():
#     # Arrange
#     account = get_account()
#     (payment_token, identityRegistry) = deploy()
#     token_name = "Test"
#     token_symbol = "Test"
#     initial_supply = 1e9
#     redeem_state = 0
#     buyback_date = int(datetime(2024, 3, 13, 12, 42).timestamp())
#     price = 100
#     token = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         redeem_state,
#         buyback_date,
#         payment_token,
#         identityRegistry.address,
#         price,
#         {"from": account},
#     )
#     token1 = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         3,
#         buyback_date,
#         payment_token,
#         identityRegistry.address,
#         price,
#         {"from": account},
#     )
#     token2 = Token.deploy(
#         token_name,
#         token_symbol,
#         initial_supply,
#         0,
#         buyback_date,
#         payment_token,
#         identityRegistry.address,
#         price,
#         {"from": account},
#     )
#     payment_token.transfer(token, 1e9, {"from": account})
#     token.issueToken(100, account, {"from": account})
#     asset = interface.IERC20(token.getAddress())
#     # Act
#     amount = 100
#     asset.approve(token, amount, {"from": account})
#     chain.sleep(60 * 2)
#     chain.mine(1)
#     token.redeemToken(amount, {"from": account})
#     # Assert
#     assert payment_token.balanceOf(account) == price * amount
#     assert interface.IERC20(token.getAddress()).balanceOf(token) == initial_supply
#     token1.issueToken(100, account, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token1.redeemToken(amount, {"from": account})
#     token2.issueToken(100, account, {"from": account})
#     token2.issueToken(100, account, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token2.redeemToken(0, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token2.redeemToken(101, {"from": account})
#     with pytest.raises(exceptions.VirtualMachineError):
#         token2.redeemToken(100, {"from": account})


def test_cannot_pay_interest_if_amortized():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    redeem_state = 0  # Redeemable
    payment_frequency = 1  # Daily
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    reimburse_state = 5  # Amortization
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    payment_token.transfer(token, (face_value * interest_rate), {"from": account1})
    token.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # with pytest.raises(exceptions.VirtualMachineError):
    token.payInterest(account, {"from": account})


def test_can_pay_interest_in_perpetuity():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    redeem_state = 0  # Redeemable
    payment_frequency = 1  # Daily
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    reimburse_state = 10
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    payment_token.transfer(token, (face_value * interest_rate), {"from": account1})
    token.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Act
    token.payInterest(account, {"from": account})
    # Assert
    assert payment_token.balanceOf(account) == (face_value * interest_rate)
    assert token.maturityDate() == 0


def test_can_pay_interest():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    redeem_state = 0  # Redeemable
    payment_frequency = 1  # Daily
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    payment_token.transfer(
        token, (face_value * interest_rate) / 1000, {"from": account1}
    )
    token.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Act
    token.payInterest(account, {"from": account})
    # Assert
    assert payment_token.balanceOf(account) == (face_value * interest_rate) / 1000
    # Checking 'Investor Already Paid in this Payment Period' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterest(account, {"from": account})
    # Checking Only Owner Condition
    with pytest.raises(exceptions.VirtualMachineError):
        chain.sleep(86400 + 60 * 60 * 12)
        chain.mine(1)
        token.payInterest(account, {"from": account2})
    # Checking 'Investor Exists' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterest(account2, {"from": account})
    # Checking 'Insufficient Balance to Pay' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterest(account, {"from": account})
    # Checking 'Is Payable' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token1 = Token.deploy(
            token_name,
            token_symbol,
            initial_supply,
            (redeem_state, 0, interest_type),
            maturity_date,
            payment_token.address,
            identityRegistry.address,
            price,
            face_value,
            interest_rate,
            {"from": account},
        )
        token1.issueToken(100, account, {"from": account})
        chain.sleep(86400 + 60 * 60 * 12)
        chain.mine(1)
        token1.payInterest(account, {"from": account})
    # Checking 'Is Fixed or Variable' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token2 = Token.deploy(
            token_name,
            token_symbol,
            initial_supply,
            (redeem_state, payment_frequency, 5),
            maturity_date,
            payment_token.address,
            identityRegistry.address,
            price,
            face_value,
            interest_rate,
            {"from": account},
        )
        token2.issueToken(100, account, {"from": account})
        chain.sleep(86400 + 60 * 60 * 12)
        chain.mine(1)
        token2.payInterest(account, {"from": account})
    # Checking 'Current Time < Maturity' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token3 = Token.deploy(
            token_name,
            token_symbol,
            initial_supply,
            (redeem_state, payment_frequency, interest_type),
            int(datetime(2024, 3, 25, 18, 42).timestamp()),
            payment_token.address,
            identityRegistry.address,
            price,
            face_value,
            interest_rate,
            {"from": account},
        )
        token3.issueToken(100, account, {"from": account})
        chain.sleep(86400 + 60 * 60 * 12)
        chain.mine(1)
        token3.payInterest(account, {"from": account})


def test_can_pay_interest_to_all_token_holders():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    redeem_state = 0  # Redeemable
    payment_frequency = 4  # Monthly
    interest_type = 3  # Variable
    maturity_date = int(datetime(2026, 3, 13, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    amount = ((face_value * interest_rate) / 1000) * 2
    payment_token.transfer(token, amount, {"from": account1})
    token.issueToken(100, account, {"from": account})
    token.issueToken(100, account2, {"from": account})
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (3, 5, 3),
        int(datetime(2050, 3, 13, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    token1.issueToken(100, account, {"from": account})
    token1.issueToken(100, account2, {"from": account})
    # Act
    chain.sleep(2628288 + 60 * 60 * 12)
    chain.mine(1)
    token.payInterestToAll({"from": account})
    chain.sleep(31556952)
    chain.mine(1)
    # Assert
    assert payment_token.balanceOf(account) == (face_value * interest_rate) / 1000
    assert payment_token.balanceOf(account2) == (face_value * interest_rate) / 1000
    # Checking 'Insufficient Balance to Pay All Investors' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestToAll({"from": account})
    # Checking 'Only Owner' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestToAll({"from": account1})
    payment_token.transfer(token1, 1e6, {"from": account1})
    token1.payInterestToAll({"from": account})
    assert payment_token.balanceOf(account) == ((face_value * interest_rate) / 1000) * 2
    assert (
        payment_token.balanceOf(account2) == ((face_value * interest_rate) / 1000) * 2
    )
    # Checking 'Is Payable' Condition
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (3, 0, 3),
        int(datetime(2050, 3, 13, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterestToAll({"from": account})
    # Checking 'Is Fixed or Variable' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token3 = Token.deploy(
            token_name,
            token_symbol,
            initial_supply,
            (redeem_state, payment_frequency, 5),
            maturity_date,
            payment_token.address,
            identityRegistry.address,
            price,
            face_value,
            interest_rate,
            {"from": account},
        )
        token3.issueToken(100, account, {"from": account})
        chain.sleep(86400 + 60 * 60 * 12)
        chain.mine(1)
        token3.payInterestToAll({"from": account})
    # Checking 'Current Time < Maturity' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token4 = Token.deploy(
            token_name,
            token_symbol,
            initial_supply,
            (redeem_state, payment_frequency, interest_type),
            int(datetime(2024, 3, 25, 18, 42).timestamp()),
            payment_token.address,
            identityRegistry.address,
            price,
            face_value,
            interest_rate,
            {"from": account},
        )
        token4.issueToken(100, account, {"from": account})
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
    redeem_state = 2  # Exchangeable
    payment_frequency = 1  # Daily
    interest_type = 5  # Payment in kind
    maturity_date = int(datetime(2026, 3, 13, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    print(token.interestType())
    eth = ERC20Mock.deploy({"from": account})
    supply = 1e6
    conversion_rate = 2
    eth.mint(token, supply)
    token.addExchangeableToken(eth, conversion_rate, {"from": account})
    token.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Act
    amount = 100
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
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    token.issueToken(100, account, {"from": account})
    # Checking 'Insufficient Balance' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKind(
            account.address, eth.address, 1e6, {"from": account}
        )
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, 4),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token1, supply, {"from": account})
    token1.addExchangeableToken(eth, conversion_rate, {"from": account})
    token1.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Is Payment in Kind' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestInPaymentInKind(
            account.address, eth.address, 100, {"from": account}
        )
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 0, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token2, supply, {"from": account})
    token2.addExchangeableToken(eth, conversion_rate, {"from": account})
    token2.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Is Payable' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterestInPaymentInKind(
            account.address, eth.address, 100, {"from": account}
        )
    token3 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token3, supply, {"from": account})
    token3.addExchangeableToken(eth, conversion_rate, {"from": account})
    token3.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Is Allowed Exchange Token' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token3.payInterestInPaymentInKind(
            account.address, account.address, 100, {"from": account}
        )
    token4 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        int(datetime(2024, 4, 2, 18, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token4, supply, {"from": account})
    token4.addExchangeableToken(eth, conversion_rate, {"from": account})
    token4.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Current Time < Maturity' Condition
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
    redeem_state = 2  # Exchangeable
    payment_frequency = 1  # Daily
    interest_type = 5  # Payment in kind
    maturity_date = int(datetime(2026, 3, 13, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth = ERC20Mock.deploy({"from": account})
    supply = 1e6
    conversion_rate = 2
    eth.mint(token, supply)
    token.addExchangeableToken(eth, conversion_rate, {"from": account})
    token.issueToken(100, account, {"from": account})
    token.issueToken(100, account2, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Act
    amount = 100
    # Checking 'Only Owner' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account1})
    token.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account})
    # Assert
    assert eth.balanceOf(account) == amount
    assert eth.balanceOf(account2) == amount
    assert eth.balanceOf(token) == supply - amount * 2
    token.issueToken(100, account, {"from": account})
    # Checking 'Insufficient Balance' Condition
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestInPaymentInKindToAll(eth.address, 1e6, {"from": account})
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, 4),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token1, supply, {"from": account})
    token1.addExchangeableToken(eth, conversion_rate, {"from": account})
    token1.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Is Payment in Kind' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account})
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 0, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token2, supply, {"from": account})
    token2.addExchangeableToken(eth, conversion_rate, {"from": account})
    token2.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Is Payable' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterestInPaymentInKindToAll(eth.address, 100, {"from": account})
    token3 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token3, supply, {"from": account})
    token3.addExchangeableToken(eth, conversion_rate, {"from": account})
    token3.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Is Allowed Exchange Token' Condition
    with pytest.raises(exceptions.VirtualMachineError):
        token3.payInterestInPaymentInKindToAll(account.address, 100, {"from": account})
    token4 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        int(datetime(2024, 4, 2, 18, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    eth.mint(token4, supply, {"from": account})
    token4.addExchangeableToken(eth, conversion_rate, {"from": account})
    token4.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Current Time < Maturity' Condition
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
    redeem_state = 2  # Exchangeable
    payment_frequency = 1  # Daily
    interest_type = 4  # Cash
    maturity_date = int(datetime(2026, 3, 13, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token.issueToken(100, account, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Act
    receipt_number = 0
    date = int(datetime(2024, 3, 25, 12, 42).timestamp())
    amount = 100
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
    with pytest.raises(exceptions.VirtualMachineError):
        encoded_message = encode_abi(
            ["uint256", "uint256", "address", "uint256"],
            [receipt_number, date, account2.address, amount],
        )
        hashed_message = Web3.keccak(encoded_message)
        msg = encode_defunct(hexstr=str(hashed_message.hex()))
        signedObject = Account.sign_message(msg, config["wallets"]["from_key"])
        token.payInterestInCash(
            receipt_number,
            date,
            account2.address,
            amount,
            signedObject.signature,
            {"from": account1},
        )
    # Checking 'Signer is not Owner' Condition
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account},
    )
    token1.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
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
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, 1),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token2.issueToken(100, account, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
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
    token3 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 0, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token3.issueToken(100, account, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
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
    token4 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, payment_frequency, interest_type),
        int(datetime(2024, 4, 1, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token4.issueToken(100, account, {"from": account1})
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


def test_can_pay_at_maturity():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e12
    redeem_state = 2  # Exchangeable
    reimburse_state = 1  # Fixed Maturity
    payment_frequency = 1  # Daily
    interest_type = 4  # Cash
    maturity_date = int(datetime(2024, 3, 27, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token.issueToken(100, account, {"from": account1})
    payment_token.transfer(token, (face_value * 100) * 2, {"from": account1})
    # Act
    # Checking 'Maturity <= Current Time' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAtMaturity(account, {"from": account1})
    # ---------------------------------------------
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAtMaturity(account, {"from": account})
    # ---------------------------------------------
    token.payAtMaturity(account, {"from": account1})
    # Assert
    payment_token.balanceOf(account) == face_value * 100
    payment_token.balanceOf(token) == face_value * 100
    # Checking 'Investor Exists' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAtMaturity(account2, {"from": account1})
    # ---------------------------------------------
    # Checking 'Investor Already Paid' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAtMaturity(account, {"from": account1})
    # ---------------------------------------------
    # Checking 'Has Maturity Payment' Condition
    # ---------------------------------------------
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 8, payment_frequency, interest_type),
        int(datetime(2024, 3, 28, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token1.issueToken(100, account, {"from": account1})
    payment_token.transfer(token1, face_value, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payAtMaturity(account, {"from": account1})
    # ---------------------------------------------
    # Checking 'Insufficient Balance' Condition
    # ---------------------------------------------
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        int(datetime(2024, 3, 30, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token2.issueToken(100, account, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payAtMaturity(account, {"from": account1})
    # ---------------------------------------------


def test_can_pay_at_maturity_to_all():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 2  # Exchangeable
    reimburse_state = 3  # Fixed Maturity with Put and Call
    payment_frequency = 1  # Daily
    interest_type = 4  # Cash
    maturity_date = int(datetime(2024, 3, 27, 12, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 1000
    initial_supply = 200
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token.issueToken(100, account, {"from": account1})
    token.issueToken(100, account2, {"from": account1})
    payment_token.transfer(token, (face_value * 100) * 2, {"from": account1})
    # Act
    # Checking 'Maturity <= Current Time' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAtMaturityToAll({"from": account1})
    # ---------------------------------------------
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAtMaturityToAll({"from": account})
    # ---------------------------------------------
    token.payAtMaturityToAll({"from": account1})
    # Assert
    payment_token.balanceOf(account) == face_value * 100
    payment_token.balanceOf(account2) == face_value * 100
    payment_token.balanceOf(token) == 0
    # Checking 'Has Maturity Payment' Condition
    # ---------------------------------------------
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 8, payment_frequency, interest_type),
        int(datetime(2024, 3, 28, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token1.issueToken(100, account, {"from": account1})
    payment_token.transfer(token1, face_value, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payAtMaturityToAll({"from": account1})
    # ---------------------------------------------
    # Checking 'Insufficient Balance' Condition
    # ---------------------------------------------
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        int(datetime(2030, 3, 30, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token2.issueToken(100, account, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payAtMaturityToAll({"from": account1})
    # ---------------------------------------------


def test_can_set_amortization_schedule():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 2  # Exchangeable
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 1e6
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    # Act
    r = token.periodicInterestRate() / 10**8
    n = token.loanTerm() / 10**8
    nume = r * (1 + r) ** n
    deno = (1 + r) ** n - 1
    token.setAmortizationSchedule(nume * 1e8, deno * 1e8, {"from": account1})
    monthly = token.getPeriodicPayment() / 1e8
    # Assert
    assert (
        round(monthly, 2) == 2.13
    )  # This value is taken from an online amortization calculator based on the same parameters
    # Checking 'Numerator and Denominator Non Zero Condition' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.setAmortizationSchedule(0, deno * 1e8, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token.setAmortizationSchedule(nume * 1e8, 0, {"from": account1})
    # ---------------------------------------------
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.setAmortizationSchedule(nume * 1e8, deno * 1e8, {"from": account})
    # ---------------------------------------------
    # Checking 'Is Amortizable' Condition
    # ---------------------------------------------
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 1, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token1.setAmortizationSchedule(0, deno * 1e8, {"from": account1})
    # ---------------------------------------------


def test_can_modify_periodic_interest_rate():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 2  # Exchangeable
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    interest_type = 3  # Variable
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 1e6
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    # Act
    new_rate = 15
    r = token.calculatePeriodicInterestRate(new_rate) / 1e8
    n = token.loanTerm() / 1e8
    nume = r * (1 + r) ** n
    deno = (1 + r) ** n - 1
    monthly = (face_value * nume) / deno
    token.modifyInterestRate(new_rate, nume * 1e8, deno * 1e8, {"from": account1})
    # Assert
    assert token.interestRate() == new_rate
    assert token.periodicInterestRate() / 1e8 == r
    assert round(token.periodicPayment() / 1e8, 2) == round(monthly, 2)
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.modifyInterestRate(new_rate, nume * 1e8, deno * 1e8, {"from": account})
    # ---------------------------------------------
    # Checking 'New Rate Non-Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.modifyInterestRate(0, nume * 1e8, deno * 1e8, {"from": account1})
    # ---------------------------------------------
    # Checking 'Numerator Non-Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.modifyInterestRate(new_rate, 0, deno * 1e8, {"from": account1})
    # ---------------------------------------------
    # Checking 'Denominator Non-Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.modifyInterestRate(new_rate, nume * 1e8, 0, {"from": account1})
    # ---------------------------------------------
    # Checking 'Is Variable' Condition
    # ---------------------------------------------
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, 1),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token1.modifyInterestRate(new_rate, nume * 1e8, deno * 1e8, {"from": account1})
    # ---------------------------------------------
    # Checking 'Is Amortizable' Condition
    # ---------------------------------------------
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 12, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token2.modifyInterestRate(new_rate, nume * 1e8, deno * 1e8, {"from": account1})
    # ---------------------------------------------


def test_pay_amortized_payments():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 0  # Redeemable
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 1e6
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 100
    token.issueToken(amount, account, {"from": account1})
    r = token.periodicInterestRate() / 10**8
    n = token.loanTerm() / 10**8
    nume = r * (1 + r) ** n
    deno = (1 + r) ** n - 1
    # Checking 'Periodic Payment is Non Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPayments(account, {"from": account1})
    # ---------------------------------------------
    token.setAmortizationSchedule(nume * 1e8, deno * 1e8, {"from": account1})
    monthly = token.getPeriodicPayment() / 1e8
    payment_token.transfer(token, monthly * amount, {"from": account1})
    # Act
    chain.sleep(2629800 + 86400)
    chain.mine(1)
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPayments(account, {"from": account})
    # ---------------------------------------------
    token.payAmortizedPayments(account, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account) == amount * monthly
    # Checking 'Investor Exists' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPayments(account2, {"from": account1})
    # ---------------------------------------------
    # Checking 'Token Holder Already Paid' Condition
    # ---------------------------------------------
    token.issueToken(amount, account2, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPayments(account2, {"from": account1})
    # ---------------------------------------------
    # Checking 'Token Holder Already Paid' Condition
    # ---------------------------------------------
    payment_token.transfer(token, monthly * amount, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPayments(account, {"from": account1})
    # ---------------------------------------------


def test_can_pay_amortized_payments_to_all():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 0  # Redeemable
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 50
    token.issueToken(amount, account, {"from": account1})
    token.issueToken(amount, account2, {"from": account1})
    r = token.periodicInterestRate() / 10**8
    n = token.loanTerm() / 10**8
    nume = r * (1 + r) ** n
    deno = (1 + r) ** n - 1
    # Checking 'Periodic Payment is Non Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPaymentsToAll({"from": account1})
    # ---------------------------------------------
    token.setAmortizationSchedule(nume * 1e8, deno * 1e8, {"from": account1})
    monthly = token.getPeriodicPayment() / 1e8
    payment_token.transfer(token, (initial_supply * monthly) * 2, {"from": account1})
    # Act
    chain.sleep(2629800 + 86400)
    chain.mine(1)
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPaymentsToAll({"from": account})
    # ---------------------------------------------
    token.payAmortizedPaymentsToAll({"from": account1})
    # Assert
    assert payment_token.balanceOf(account) == amount * monthly
    assert payment_token.balanceOf(account2) == amount * monthly
    chain.sleep(31556952 * 5)
    chain.mine(1)
    token.payAmortizedPaymentsToAll({"from": account1})
    assert token.investorToMaturityPaymentStatus(account) == True
    assert token.investorToMaturityPaymentStatus(account2) == True
    chain.sleep(2629800 + 86400)
    chain.mine(1)
    # Checking 'Insufficient Balance' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPaymentsToAll({"from": account1})
    # ---------------------------------------------
    payment_token.transfer(token, (initial_supply * monthly), {"from": account1})
    token.payAmortizedPaymentsToAll({"from": account1})
    assert payment_token.balanceOf(account) == amount * monthly * 2
    assert payment_token.balanceOf(account2) == amount * monthly * 2


def test_cannot_pay_amortized_payments_after_maturity():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 1  # Extendible
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2024, 4, 27, 13, 3).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 1e6
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 100
    token.issueToken(amount, account, {"from": account1})
    r = token.periodicInterestRate() / 10**8
    n = token.loanTerm() / 10**8
    nume = r * (1 + r) ** n
    deno = (1 + r) ** n - 1
    token.setAmortizationSchedule(nume * 1e8, deno * 1e8, {"from": account1})
    payment_token.transfer(token, 1e6, {"from": account1})
    chain.sleep(2629800 + 86400)
    chain.mine(1)
    token.payAmortizedPayments(account, {"from": account1})
    chain.sleep(2629800 + 86400)
    chain.mine(1)
    assert token.investorToMaturityPaymentStatus(account) == True
    with pytest.raises(exceptions.VirtualMachineError):
        token.payAmortizedPayments(account, {"from": account1})


def test_can_call_token():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 0  # Redeemable
    reimburse_state = 4  # Fixed maturity with put and call
    payment_frequency = 4  # Monthly
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 50
    token.issueToken(amount, account, {"from": account1})
    payment_token.transfer(token, amount * face_value, {"from": account1})
    # Act
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.callToken(account, 0, {"from": account})
    # ---------------------------------------------
    token.callToken(account, 0, {"from": account1})
    # Assert
    assert token.getBalance(account) == 0
    assert payment_token.balanceOf(account) == amount * face_value
    assert token.getTotalSupply() == initial_supply - amount
    # Checking 'Investor Exists' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.callToken(account2, 0, {"from": account1})
    # ---------------------------------------------
    # Checking 'Insufficient Balance' Condition
    # ---------------------------------------------
    token.issueToken(amount, account2, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token.callToken(account2, 0, {"from": account1})
    # ---------------------------------------------
    # Checking 'Current Time < Maturity' Condition
    # ---------------------------------------------
    payment_token.transfer(token, amount * face_value + 100, {"from": account1})
    chain.sleep(31556952 * 5 + 86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token.callToken(account2, 0, {"from": account1})
    # ---------------------------------------------
    # Checking 'Is Callable' Condition
    # ---------------------------------------------
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 1, payment_frequency, interest_type),
        int(datetime(2034, 3, 27, 15, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token1.issueToken(amount, account, {"from": account1})
    payment_token.transfer(token1, amount * face_value, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token1.callToken(account, 0, {"from": account1})
    # ---------------------------------------------


def test_can_call_token_from_all():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 0  # Redeemable
    reimburse_state = 4  # Fixed maturity with put and call
    payment_frequency = 4  # Monthly
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 150
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 50
    dividend = 100
    token.issueToken(amount, account, {"from": account1})
    token.issueToken(amount, account2, {"from": account1})
    payment_token.transfer(
        token, (amount * face_value + dividend) * 3, {"from": account1}
    )
    chain.sleep(31556952)
    chain.mine(1)
    # Act
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.callTokenFromAll(dividend, {"from": account})
    # ---------------------------------------------
    token.callTokenFromAll(dividend, {"from": account1})
    # Assert
    assert token.getBalance(account) == 0
    assert token.getBalance(account2) == 0
    assert token.getTotalSupply() == initial_supply - amount * 2
    assert payment_token.balanceOf(account) == amount * face_value + dividend
    assert payment_token.balanceOf(account2) == amount * face_value + dividend
    # Checking 'Insufficient Balance' Condition
    # ---------------------------------------------
    token.issueToken(amount, account2, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token.callTokenFromAll(dividend * 2, {"from": account1})
    # ---------------------------------------------
    # Checking 'Current Time < Maturity' Condition
    # ---------------------------------------------
    chain.sleep(31556952 * 5 + 86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token.callTokenFromAll(dividend, {"from": account1})
    # ---------------------------------------------
    # ---------------------------------------------
    # Checking 'Is Callable' Condition
    # ---------------------------------------------
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 1, payment_frequency, interest_type),
        int(datetime(2050, 3, 27, 15, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    token1.issueToken(amount, account, {"from": account1})
    payment_token.transfer(token1, amount * face_value, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token1.callTokenFromAll(0, {"from": account1})
    # ---------------------------------------------


def test_can_set_put_period():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    redeem_state = 0  # Redeemable
    reimburse_state = 4  # Fixed maturity with put and call
    payment_frequency = 4  # Monthly
    interest_type = 1  # Fixed
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 150
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, reimburse_state, payment_frequency, interest_type),
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    # Act
    start_date = int(datetime(2024, 4, 1, 15, 42).timestamp())
    end_date = int(datetime(2025, 4, 27, 15, 42).timestamp())
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.setPutPeriod(start_date, end_date, {"from": account})
    # ---------------------------------------------
    # Checking 'Start Date Non Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.setPutPeriod(0, end_date, {"from": account1})
    # ---------------------------------------------
    # Checking 'End Date Non Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.setPutPeriod(start_date, 0, {"from": account1})
    # ---------------------------------------------
    # Checking 'End Date > Start Date ' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.setPutPeriod(end_date, start_date, {"from": account1})
    # ---------------------------------------------
    # Checking 'End Date <= Maturity' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.setPutPeriod(
            start_date,
            int(datetime(2030, 3, 27, 15, 42).timestamp()),
            {"from": account1},
        )
    # ---------------------------------------------
    # Checking 'Contract Deployment Time <= Start Date' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.setPutPeriod(
            int(datetime(2020, 3, 27, 15, 42).timestamp()),
            end_date,
            {"from": account1},
        )
    # ---------------------------------------------
    # Checking 'Current Time < Start Date' Condition
    # ---------------------------------------------
    chain.sleep(60 * 5)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token.setPutPeriod(
            int(datetime(2024, 4, 1, 12, 12).timestamp()),
            end_date,
            {"from": account1},
        )
    # ---------------------------------------------
    token.setPutPeriod(start_date, end_date, {"from": account1})
    # Assert
    assert token.startDate() == start_date
    assert token.endDate() == end_date
    # Checking 'Is Putable' Condition
    # ---------------------------------------------
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        (redeem_state, 1, payment_frequency, interest_type),
        int(datetime(2050, 3, 27, 15, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        face_value,
        interest_rate,
        {"from": account1},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token1.setPutPeriod(start_date, end_date, {"from": account1})
    # ---------------------------------------------
