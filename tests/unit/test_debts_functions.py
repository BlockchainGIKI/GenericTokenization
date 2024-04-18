from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Debts,
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


# def test_can_put_debt():
#     # Arrange
#     account = get_account()
#     account1 = accounts.add(config["wallets"]["from_key"])
#     account2 = get_account(2)
#     (payment_token, identityRegistry) = deploy()
#     debt_name = "Test"
#     debt_symbol = "Test"
#     redeem_state = 0  # Redeemable
#     reimburse_state = 4  # Fixed maturity with put and call
#     payment_frequency = 4  # Monthly
#     interest_type = 1  # Fixed
#     maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
#     price = 100
#     face_value = 100
#     interest_rate = 10
#     initial_supply = 150
#     debt = Debts.deploy(
#         debt_name,
#         debt_symbol,
#         initial_supply,
#         (redeem_state, reimburse_state, payment_frequency, interest_type),
#         maturity_date,
#         payment_token.address,
#         identityRegistry.address,
#         price,
#         face_value,
#         interest_rate,
#         {"from": account1},
#     )
#     amount = 50
#     debt.issueToken(amount, account, {"from": account1})
#     payment_token.transfer(debt, amount * face_value, {"from": account1})
#     start_date = int((datetime.now() + timedelta(days=2)).timestamp())
#     end_date = int((datetime.now() + timedelta(days=4)).timestamp())
#     # Checking 'Start Date is Non Zero' Condition
#     # ---------------------------------------------
#     with pytest.raises(exceptions.VirtualMachineError):
#         debt.putToken(50, {"from": account})
#     # ---------------------------------------------
#     debt.setPutPeriod(start_date, end_date, {"from": account1})
#     # Act
#     # Checking 'Start Date <= Current Time' Condition
#     # ---------------------------------------------
#     with pytest.raises(exceptions.VirtualMachineError):
#         debt.putToken(50, {"from": account})
#     # ---------------------------------------------
#     chain.sleep(86400 * 3)
#     chain.mine(1)
#     # Checking 'Amount is Non Zero' Condition
#     # ---------------------------------------------
#     with pytest.raises(exceptions.VirtualMachineError):
#         debt.putToken(0, {"from": account})
#     # ---------------------------------------------
#     put_amount = 20
#     debt.putToken(put_amount, {"from": account})
#     # Assert
#     assert payment_token.balanceOf(account) == put_amount * face_value
#     assert debt.getBalance(account) == amount - put_amount
#     assert debt.getTotalSupply() == initial_supply - put_amount
#     # Checking 'Investor Exists' Condition
#     # ---------------------------------------------
#     with pytest.raises(exceptions.VirtualMachineError):
#         debt.putToken(50, {"from": account2})
#     # ---------------------------------------------
#     # Checking 'Token Holder Balance >= Amount' Condition
#     # ---------------------------------------------
#     with pytest.raises(exceptions.VirtualMachineError):
#         debt.putToken(50, {"from": account})
#     # ---------------------------------------------
#     # Checking 'Insufficient Balance' Condition
#     # ---------------------------------------------
#     debt.issueToken(amount, account2, {"from": account1})
#     with pytest.raises(exceptions.VirtualMachineError):
#         debt.putToken(amount, {"from": account2})
#     # ---------------------------------------------
#     # Checking 'Current Time <= End Date' Condition
#     # ---------------------------------------------
#     chain.sleep(86400 * 5)
#     chain.mine(1)
#     with pytest.raises(exceptions.VirtualMachineError):
#         debt.putToken(put_amount, {"from": account})
#     # ---------------------------------------------
