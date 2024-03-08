from scripts.helpfulscripts import get_account
from brownie import Token, ERC20Mock, PaymentToken, exceptions, interface, chain
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
        price,
        {"from": account},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token1.exchangeToken(eth, amount, {"from": account})


def test_can_redeem_tokens():
    # Arrange
    account = get_account()
    token_name = "Test"
    token_symbol = "Test"
    initial_supply = 1e9
    redeem_state = 0
    buyback_date = int(datetime(2024, 3, 5, 19, 14).timestamp())
    payment_token = PaymentToken.deploy(1e9, {"from": account})
    price = 100
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        redeem_state,
        buyback_date,
        payment_token,
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
