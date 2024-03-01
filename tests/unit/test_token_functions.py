from scripts.helpfulscripts import get_account
from brownie import Token, exceptions
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
        1709301411,
        {"from": account},
    )
    # Assert
    assert token.redemptionState() == 0
    assert token.buybackDate() == 1709301411
    with pytest.raises(exceptions.VirtualMachineError):
        Token.deploy(
            "Test",
            "Test",
            100,
            0,
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
    buyback_date = 1709301411
    token = Token.deploy(
        token_name,
        token_symbol,
        initial_supply,
        redeem_state,
        buyback_date,
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
