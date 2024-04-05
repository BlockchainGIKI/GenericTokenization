from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Equities,
    Parameters,
    INCOME,
    Asset,
    exceptions,
    chain,
    accounts,
    config,
)
from datetime import datetime, timedelta
from web3 import Web3
import pytest


# def test_can_pay_income():
#     # Arrange
#     account = get_account()
#     account1 = accounts.add(config["wallets"]["from_key"])
#     account2 = get_account(2)
#     (payment_token, identityRegistry) = deploy()
#     equity_name = "Test"
#     equity_symbol = "Test"
#     initial_supply = 100
#     redeem_state = 0  # Redeemable
#     payment_frequency = 1  # Daily
#     income_state = 3  # Participating
#     maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
#     price = 100
#     income_rate = 10
#     equity = Equities.deploy(
#         equity_name,
#         equity_symbol,
#         initial_supply,
#         redeem_state,
#         income_state,
#         payment_frequency,
#         maturity_date,
#         payment_token,
#         identityRegistry,
#         price,
#         income_rate,
#         {"from": account1},
#     )
#     amount = 50
#     dividend = 100
#     equity.issueToken(amount, account, {"from": account1})
#     payment_token.transfer(
#         equity, (income_rate * amount + dividend) * 1, {"from": account1}
#     )
#     # Act
#     equity.payIncome(account, dividend, {"from": account1})
#     # Assert
#     assert payment_token.balanceOf(account) == income_rate * amount + dividend
#     # Checking 'Investor Already Paid in this Payment Period' Condition
#     # ---------------------------------------------
#     with pytest.raises(exceptions.VirtualMachineError):
#         equity.payIncome(account, dividend, {"from": account1})
#     # ---------------------------------------------
#     # Checking Only Owner Condition
#     # ---------------------------------------------
#     chain.sleep(86400 + 60 * 60 * 12)
#     chain.mine(1)
#     with pytest.raises(exceptions.VirtualMachineError):
#         equity.payIncome(account, dividend, {"from": account})
#     # ---------------------------------------------
#     # Checking 'Investor Exists' Condition
#     # ---------------------------------------------
#     with pytest.raises(exceptions.VirtualMachineError):
#         equity.payIncome(account2, dividend, {"from": account1})
#     # ---------------------------------------------
#     # Checking 'Insufficient Balance to Pay' Condition
#     # ---------------------------------------------
#     equity.issueToken(amount, account2, {"from": account1})
#     with pytest.raises(exceptions.VirtualMachineError):
#         equity.payIncome(account2, dividend, {"from": account1})
#     # ---------------------------------------------
#     # Checking 'Dividend cannot be zero in case of participating income type' Condition
#     # ---------------------------------------------
#     with pytest.raises(exceptions.VirtualMachineError):
#         equity.payIncome(account2, 0, {"from": account1})
#     # ---------------------------------------------
#     # Checking 'Current Time is Less than Maturity' Condition
#     # ---------------------------------------------
#     chain.sleep(31556952 * 2)
#     with pytest.raises(exceptions.VirtualMachineError):
#         equity.payIncome(account, dividend, {"from": account1})
#     # ---------------------------------------------
#     # # Checking 'Is Payable' Condition
#     # ---------------------------------------------
#     equity1 = Equities.deploy(
#         equity_name,
#         equity_symbol,
#         initial_supply,
#         redeem_state,
#         income_state,
#         0,
#         maturity_date,
#         payment_token,
#         identityRegistry,
#         price,
#         income_rate,
#         {"from": account1},
#     )
#     equity1.issueToken(amount, account, {"from": account1})
#     payment_token.transfer(
#         equity1, (income_rate * amount + dividend) * 1, {"from": account1}
#     )
#     with pytest.raises(exceptions.VirtualMachineError):
#         equity1.payIncome(account, dividend, {"from": account1})


def test_can_disburse_income_to_all():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    equity_name = "Test"
    equity_symbol = "Test"
    initial_supply = 100
    redeem_state = 0  # Redeemable
    payment_frequency = 1  # Daily
    income_state = 6  # Normal Rate
    maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    price = 100
    income_rate = 10
    equity = Equities.deploy(
        equity_name,
        equity_symbol,
        initial_supply,
        redeem_state,
        income_state,
        payment_frequency,
        maturity_date,
        payment_token,
        identityRegistry,
        price,
        income_rate,
        {"from": account1},
    )
    amount = 50
    dividend = 0
    equity.issueToken(amount, account, {"from": account1})
    equity.issueToken(amount, account2, {"from": account1})
    payment_token.transfer(equity, (income_rate * amount) * 2, {"from": account1})
    # Act
    equity.payIncomeToAll(dividend, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account) == income_rate * amount + dividend
    assert payment_token.balanceOf(account) == income_rate * amount + dividend
    # Checking Only Owner Condition
    # ---------------------------------------------
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncomeToAll(dividend, {"from": account})
    # ---------------------------------------------
    # Checking 'Insufficient Balance to Pay' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncomeToAll(dividend, {"from": account1})
    # ---------------------------------------------
    # Checking 'Current Time is Less than Maturity' Condition
    # ---------------------------------------------
    chain.sleep(31556952 * 2)
    payment_token.transfer(equity, (income_rate * amount) * 2, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncomeToAll(dividend, {"from": account1})
    # ---------------------------------------------
    # Checking 'Is Payable' Condition
    # ---------------------------------------------
    equity1 = Equities.deploy(
        equity_name,
        equity_symbol,
        initial_supply,
        redeem_state,
        income_state,
        0,
        maturity_date,
        payment_token,
        identityRegistry,
        price,
        income_rate,
        {"from": account1},
    )
    equity1.issueToken(amount, account, {"from": account1})
    dividend = 50
    payment_token.transfer(
        equity1, (income_rate * amount + dividend) * 2, {"from": account1}
    )
    with pytest.raises(exceptions.VirtualMachineError):
        equity1.payIncomeToAll(dividend, {"from": account1})


def test_can_pay_cumulative_income():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    equity_name = "Test"
    equity_symbol = "Test"
    initial_supply = 1000
    redeem_state = 0  # Redeemable
    payment_frequency = 1  # Daily
    income_state = 2  # Cumulative Fixed Rate
    maturity_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    price = 100
    income_rate = 10
    equity = Equities.deploy(
        equity_name,
        equity_symbol,
        initial_supply,
        redeem_state,
        income_state,
        payment_frequency,
        maturity_date,
        payment_token,
        identityRegistry,
        price,
        income_rate,
        {"from": account1},
    )
    amount = 50
    dividend = 1e18
    equity.issueToken(amount, account, {"from": account1})
    payment_token.transfer(equity, (income_rate * amount) * 2, {"from": account1})
    # Act
    chain.sleep(86400)
    chain.mine(1)
    payment_period = 0
    equity.payCumulativeIncome(account, payment_period, dividend, {"from": account1})
    # Assert
    assert payment_token.balanceOf(account) == income_rate * amount
    assert equity.investorToPaymentPeriodToStatus(account, 0) == True
    # Checking 'Investor Already Paid in this Payment Period' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payCumulativeIncome(
            account, payment_period, dividend, {"from": account1}
        )
    # ---------------------------------------------
    # Checking Only Owner Condition
    # ---------------------------------------------
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payCumulativeIncome(account, 1, dividend, {"from": account})
    # ---------------------------------------------
    # Checking 'Investor Exists' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payCumulativeIncome(
            account2, payment_period, dividend, {"from": account1}
        )
    # ---------------------------------------------
    # Checking 'Insufficient Balance to Pay' Condition
    # ---------------------------------------------
    equity.issueToken(amount + amount, account2, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payCumulativeIncome(
            account2, payment_period, dividend, {"from": account1}
        )
    # ---------------------------------------------
    # Checking 'Current Time is Less than Maturity' Condition
    # ---------------------------------------------
    chain.sleep(31556952 * 2)
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payCumulativeIncome(account, 2, dividend, {"from": account1})
    # ---------------------------------------------
    # Checking 'Is Payable' Condition
    # ---------------------------------------------
    equity1 = Equities.deploy(
        equity_name,
        equity_symbol,
        initial_supply,
        redeem_state,
        income_state,
        0,
        int(datetime(2050, 3, 13, 12, 42).timestamp()),
        payment_token,
        identityRegistry,
        price,
        income_rate,
        {"from": account1},
    )
    equity1.issueToken(amount, account, {"from": account1})
    payment_token.transfer(equity1, (income_rate * amount) * 1, {"from": account1})
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        equity1.payCumulativeIncome(
            account, payment_period, dividend, {"from": account1}
        )
    # ---------------------------------------------
    # Checking 'Is Cumulative' Condition
    # ---------------------------------------------
    equity2 = Equities.deploy(
        equity_name,
        equity_symbol,
        initial_supply,
        redeem_state,
        0,
        payment_frequency,
        int(datetime(2050, 3, 13, 12, 42).timestamp()),
        payment_token,
        identityRegistry,
        price,
        income_rate,
        {"from": account1},
    )
    equity2.issueToken(amount, account, {"from": account1})
    payment_token.transfer(equity2, (income_rate * amount) * 1, {"from": account1})
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        equity2.payCumulativeIncome(
            account, payment_period, dividend, {"from": account1}
        )
    # ---------------------------------------------


def test_prank():
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    equity_name = "Test"
    equity_symbol = "Test"
    initial_supply = 1000
    payment_frequency = 1  # Daily
    income_state = 2  # Cumulative Fixed Rate
    income_rate = 10
    asset = Asset.deploy(
        initial_supply, equity_name, equity_symbol, identityRegistry, {"from": account1}
    )
    parameters = Parameters.deploy(1000, asset, payment_token, {"from": account1})
    equity = INCOME.deploy(
        income_state, payment_frequency, income_rate, parameters, {"from": account1}
    )
    amount = 50
    asset.transfer(account, amount, {"from": account1})
    payment_token.transfer(equity, (income_rate * amount) * 2, {"from": account1})
    equity.payIncome(account, 1000, {"from": account1})
    assert payment_token.balanceOf(account) == income_rate * amount
    with pytest.raises(exceptions.VirtualMachineError):
        equity.payIncome(account2, 1000, {"from": account1})
