from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Parameters,
    INCOME,
    Asset,
    exceptions,
    chain,
    accounts,
    config,
)
import pytest


def test_can_pay_income():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    equity_name = "Test"
    equity_symbol = "Test"
    initial_supply = 1000
    payment_frequency = 1  # Daily
    income_state = 3  # Participating
    income_rate = 10
    redemption = "0x0000000000000000000000000000000000000000"
    asset = Asset.deploy(
        initial_supply, equity_name, equity_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    equity = INCOME.deploy(
        income_state,
        payment_frequency,
        income_rate,
        parameters,
        redemption,
        {"from": account1},
    )
    amount = 50
    dividend = 100
    asset.transfer(account, amount, {"from": account1})
    payment_token.transfer(
        equity, (income_rate * amount + dividend) * 1, {"from": account1}
    )
    # Act
    equity.payIncome(account, dividend, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account) == income_rate * amount + dividend
    # Checking 'Investor Already Paid in this Payment Period' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncome(account, dividend, {"from": account1})
    # ---------------------------------------------
    # Checking Only Owner Condition
    # ---------------------------------------------
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncome(account, dividend, {"from": account})
    # ---------------------------------------------
    # Checking 'Investor Exists' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncome(account2, dividend, {"from": account1})
    # ---------------------------------------------
    # Checking 'Insufficient Balance to Pay' Condition
    # ---------------------------------------------
    asset.transfer(account2, amount, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncome(account2, dividend, {"from": account1})
    # ---------------------------------------------
    # Checking 'Dividend cannot be zero in case of participating income type' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncome(account2, 0, {"from": account1})
    # ---------------------------------------------
    # # Checking 'Is Payable' Condition
    # ---------------------------------------------
    equity1 = INCOME.deploy(
        income_state, 0, income_rate, parameters, redemption, {"from": account1}
    )
    # asset.transfer(account2, amount, {"from": account1})
    payment_token.transfer(
        equity1, (income_rate * amount + dividend) * 1, {"from": account1}
    )
    with pytest.raises(exceptions.VirtualMachineError):
        equity1.payIncome(account, dividend, {"from": account1})
