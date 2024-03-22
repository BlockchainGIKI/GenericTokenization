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
from datetime import datetime
import pytest


def test_can_set_redemption_state():
    # Arrange
    account = get_account()
    # Act
    token = Token.deploy(
        "Test",
        "Test",
        100,
        0,
        1741075174,
        account,
        account,
        100,
        {"from": account},
    )
    # Assert
    assert token.redemptionState() == 0
    assert token.buybackDate() == 1741075174
    with pytest.raises(exceptions.VirtualMachineError):
        Token.deploy(
            "Test",
            "Test",
            100,
            0,
            100,
            account,
            account,
            100,
            {"from": account},
        )


def test_can_add_exchangeable_token():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 100
    redeem_state = 6
    buyback_date = 1741075174
    payment_token = account
    price = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        redeem_state,
        buyback_date,
        payment_token,
        payment_token,
        price,
        {"from": account},
    )
    # Act
    conversion_rate = 100
    token.addExchangeableToken(account, conversion_rate, {"from": account})
    # Assert
    assert token.conversionRate(account) == conversion_rate
    with pytest.raises(exceptions.VirtualMachineError):
        token.addExchangeableToken(token, conversion_rate, {"from": account1})
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        3,
        buyback_date,
        payment_token,
        payment_token,
        price,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token1.addExchangeableToken(token, conversion_rate, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token.addExchangeableToken(account, conversion_rate, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token.addExchangeableToken(
            "0x0000000000000000000000000000000000000000",
            conversion_rate,
            {"from": account},
        )
    with pytest.raises(exceptions.VirtualMachineError):
        token.addExchangeableToken(account1, 0, {"from": account})


def test_can_extend_buyback_date():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 100
    redeem_state = 6
    buyback_date = 1741075174  # refers to 2025 March 4, 12:59:34 (PKT)
    payment_token = account
    price = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        redeem_state,
        buyback_date,
        payment_token,
        payment_token,
        price,
        {"from": account},
    )
    # Act
    token.extendBuybackDate(1772611174, {"from": account})
    # Assert
    token.buybackDate() == 1772611174
    with pytest.raises(exceptions.VirtualMachineError):
        token.extendBuybackDate(1709301411, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token.extendBuybackDate(1772611174, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token.extendBuybackDate(0, {"from": account})
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        0,
        buyback_date,
        payment_token,
        payment_token,
        price,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token1.extendBuybackDate(1772611174, {"from": account})


def test_can_issue_token():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 100
    redeem_state = 6
    buyback_date = 1741075174  # refers to 2025 March 4, 12:59:34 (PKT)
    payment_token = account
    price = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        redeem_state,
        buyback_date,
        payment_token,
        payment_token,
        price,
        {"from": account},
    )
    # Act
    amount = 50
    token.issueToken(amount, account1, {"from": account})
    # Assert
    assert token.getBalance(account1) == amount
    with pytest.raises(exceptions.VirtualMachineError):
        token.issueToken(amount, account1, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token.issueToken(0, account1, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token.issueToken(100, account1, {"from": account})


def test_can_exchange_token():
    # Arrange
    account = get_account()
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 100
    redeem_state = 6
    buyback_date = 1741075174  # refers to 2025 March 4, 12:59:34 (PKT)
    price = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        redeem_state,
        buyback_date,
        payment_token,
        identityRegistry,
        price,
        {"from": account},
    )
    eth = ERC20Mock.deploy({"from": account})
    eth.mint(token, 1e18)
    conversion_rate = 2
    token.addExchangeableToken(eth, conversion_rate, {"from": account})
    # Act
    amount = 100
    token.issueToken(amount, account, {"from": account})
    asset = interface.IERC20(token.getAddress())
    asset.approve(token, amount, {"from": account})
    # print(token.temp({"from": account}))
    token.exchangeToken(eth, amount, {"from": account})
    # Asset
    assert eth.balanceOf(account) == amount * conversion_rate
    assert token.getBalance(account) == 0
    with pytest.raises(exceptions.VirtualMachineError):
        token.exchangeToken(eth, amount, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token.exchangeToken(account, amount, {"from": account})
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        1,
        buyback_date,
        payment_token,
        identityRegistry,
        price,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token1.exchangeToken(eth, amount, {"from": account})


def test_can_redeem_tokens():
    # Arrange
    account = get_account()
    (payment_token, identityRegistry) = deploy()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e9
    redeem_state = 0
    buyback_date = int(datetime(2024, 3, 13, 12, 42).timestamp())
    price = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        redeem_state,
        buyback_date,
        payment_token,
        identityRegistry.address,
        price,
        {"from": account},
    )
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        3,
        buyback_date,
        payment_token,
        identityRegistry.address,
        price,
        {"from": account},
    )
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        0,
        buyback_date,
        payment_token,
        identityRegistry.address,
        price,
        {"from": account},
    )
    payment_token.transfer(token, 1e9, {"from": account})
    token.issueToken(100, account, {"from": account})
    asset = interface.IERC20(token.getAddress())
    # Act
    amount = 100
    asset.approve(token, amount, {"from": account})
    chain.sleep(60 * 2)
    chain.mine(1)
    token.redeemToken(amount, {"from": account})
    # Assert
    assert payment_token.balanceOf(account) == price * amount
    assert interface.IERC20(token.getAddress()).balanceOf(token) == initial_supply
    token1.issueToken(100, account, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token1.redeemToken(amount, {"from": account})
    token2.issueToken(100, account, {"from": account})
    token2.issueToken(100, account, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token2.redeemToken(0, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token2.redeemToken(101, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token2.redeemToken(100, {"from": account})


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
    interest_type = 0  #
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
    payment_token.transfer(token, 1e6, {"from": account1})
    token.issueToken(100, account, {"from": account})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    # Act
    token.payInterest(account, {"from": account})


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
    payment_frequency = 1  # Daily
    maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    price = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        redeem_state,
        payment_frequency,
        maturity_date,
        payment_token.address,
        identityRegistry.address,
        price,
        {"from": account},
    )
    payment_token.transfer(token, 1e6, {"from": account1})
    token.issueToken(100, account, {"from": account})
    token.issueToken(100, account2, {"from": account})
    token1 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        3,
        5,
        int(datetime(2050, 3, 13, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        {"from": account},
    )
    token1.issueToken(100, account, {"from": account})
    token1.issueToken(100, account2, {"from": account})
    # Act
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    rate = 150
    token.payInterestToAll(rate, {"from": account})
    chain.sleep(31556952)
    chain.mine(1)
    # Assert
    assert payment_token.balanceOf(account) == (rate * price) / 1000
    assert payment_token.balanceOf(account2) == (rate * price) / 1000
    with pytest.raises(exceptions.VirtualMachineError):
        token.payInterestToAll(rate, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestToAll(rate, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payInterestToAll(rate, {"from": account})
    payment_token.transfer(token1, 1e6, {"from": account1})
    token1.payInterestToAll(rate, {"from": account})
    assert payment_token.balanceOf(account) == ((rate * price) / 1000) * 2
    assert payment_token.balanceOf(account2) == ((rate * price) / 1000) * 2
    token2 = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        3,
        0,
        int(datetime(2050, 3, 13, 12, 42).timestamp()),
        payment_token.address,
        identityRegistry.address,
        price,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token2.payInterestToAll(rate, {"from": account})
