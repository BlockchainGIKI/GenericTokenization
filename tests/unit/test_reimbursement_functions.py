from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Parameters,
    REIMBURSEMENT,
    Asset,
    exceptions,
    chain,
    accounts,
    config,
)
import pytest
from datetime import datetime, timedelta


def test_can_pay_at_maturity():
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
    precision = 8
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    reimburse_state = 1  # Fixed Maturity
    payment_frequency = 1  # Daily
    maturity_date = int(datetime(2024, 4, 17, 12, 42).timestamp())
    face_value = 100
    interest_rate = 10
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    payment_token.transfer(token, (face_value * amount) * 2, {"from": account1})
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
    assert payment_token.balanceOf(account) == face_value * amount
    assert payment_token.balanceOf(token) == face_value * amount
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
    token1 = REIMBURSEMENT.deploy(
        8,
        payment_frequency,
        parameters,
        int(datetime(2024, 4, 18, 12, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account1},
    )
    payment_token.transfer(token1, face_value, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payAtMaturity(account, {"from": account1})
    # ---------------------------------------------
    # Checking 'Insufficient Balance' Condition
    # ---------------------------------------------
    token2 = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        int(datetime(2024, 4, 20, 12, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account1},
    )
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
    reimburse_state = 3  # Fixed Maturity with Put and Call
    payment_frequency = 1  # Daily
    maturity_date = int(datetime(2024, 4, 17, 18, 2).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 200
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
    asset.transfer(account2, amount, {"from": account1})
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
    assert payment_token.balanceOf(account) == face_value * 100
    assert payment_token.balanceOf(account2) == face_value * 100
    assert payment_token.balanceOf(token) == 0
    # Checking 'Has Maturity Payment' Condition
    # ---------------------------------------------
    token1 = REIMBURSEMENT.deploy(
        8,
        payment_frequency,
        parameters,
        int(datetime(2024, 4, 18, 18, 2).timestamp()),
        face_value,
        interest_rate,
        {"from": account1},
    )
    payment_token.transfer(token1, face_value, {"from": account1})
    chain.sleep(86400 + 60 * 60 * 12)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        token1.payAtMaturityToAll({"from": account1})
    # ---------------------------------------------
    # Checking 'Insufficient Balance' Condition
    # ---------------------------------------------
    token2 = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        int(datetime(2024, 4, 20, 18, 2).timestamp()),
        face_value,
        interest_rate,
        {"from": account1},
    )
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
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 1e6
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
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
    token1 = REIMBURSEMENT.deploy(
        1,
        payment_frequency,
        parameters,
        maturity_date,
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
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 1e6
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
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
    # Checking 'Is Amortizable' Condition
    # ---------------------------------------------
    token2 = REIMBURSEMENT.deploy(
        12,
        payment_frequency,
        parameters,
        maturity_date,
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
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 1e6
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
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
    asset.transfer(account2, amount, {"from": account1})
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
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 100
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 50
    asset.transfer(account, amount, {"from": account1})
    asset.transfer(account2, amount, {"from": account1})
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
    reimburse_state = 5  # Amortization
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2024, 5, 16, 18, 43).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 1e6
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 100
    asset.transfer(account, amount, {"from": account1})
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
    reimburse_state = 4  # Fixed maturity with put and call
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 150
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 50
    asset.transfer(account, amount, {"from": account1})
    payment_token.transfer(token, amount * face_value, {"from": account1})
    asset.transferOwnership(token, {"from": account1})
    asset.transfer(token, 100, {"from": account1})
    # Act
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.callToken(account, 0, {"from": account})
    # ---------------------------------------------
    token.callToken(account, 0, {"from": account1})
    # Assert
    assert asset.balanceOf(account) == 0
    assert payment_token.balanceOf(account) == amount * face_value
    assert asset.totalSupply() == initial_supply - amount
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
    token1 = REIMBURSEMENT.deploy(
        1,
        payment_frequency,
        parameters,
        int(datetime(2032, 3, 27, 15, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account1},
    )
    token.issueToken(amount, account, {"from": account1})
    payment_token.transfer(token1, amount * face_value, {"from": account1})
    # with pytest.raises(exceptions.VirtualMachineError):
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
    reimburse_state = 4  # Fixed maturity with put and call
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 150
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 50
    dividend = 100
    asset.transfer(account, amount, {"from": account1})
    asset.transfer(account2, amount, {"from": account1})
    payment_token.transfer(
        token, (amount * face_value + dividend) * 3, {"from": account1}
    )
    chain.sleep(31556952)
    chain.mine(1)
    asset.transferOwnership(token, {"from": account1})
    asset.transfer(token, asset.balanceOf(account1), {"from": account1})
    # Act
    # Checking 'Only Owner' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        token.callTokenFromAll(dividend, {"from": account})
    # ---------------------------------------------
    token.callTokenFromAll(dividend, {"from": account1})
    # Assert
    assert asset.balanceOf(account) == 0
    assert asset.balanceOf(account2) == 0
    assert asset.totalSupply() == initial_supply - amount * 2
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
    token1 = REIMBURSEMENT.deploy(
        1,
        payment_frequency,
        parameters,
        int(datetime(2050, 3, 27, 15, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account1},
    )
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
    reimburse_state = 4  # Fixed maturity with put and call
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 150
    asset = Asset.deploy(
        initial_supply, token_name, token_symbol, identityRegistry, {"from": account1}
    )
    precision = 1000
    price = 100
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    token = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    # Act
    start_date = int(datetime(2024, 4, 27, 15, 42).timestamp())
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
            int(datetime(2024, 4, 16, 12, 12).timestamp()),
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
    token1 = REIMBURSEMENT.deploy(
        1,
        payment_frequency,
        parameters,
        int(datetime(2050, 3, 27, 15, 42).timestamp()),
        face_value,
        interest_rate,
        {"from": account1},
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token1.setPutPeriod(start_date, end_date, {"from": account1})
    # ---------------------------------------------


def test_can_put_debt():
    # Arrange
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    (payment_token, identityRegistry) = deploy()
    debt_name = "Test"
    debt_symbol = "Test"
    reimburse_state = 4  # Fixed maturity with put and call
    payment_frequency = 4  # Monthly
    maturity_date = int(datetime(2029, 3, 27, 15, 42).timestamp())
    price = 100
    face_value = 100
    interest_rate = 10
    initial_supply = 150
    asset = Asset.deploy(
        initial_supply, debt_name, debt_symbol, identityRegistry, {"from": account1}
    )
    precision = 8
    parameters = Parameters.deploy(
        price, precision, asset, payment_token, identityRegistry, {"from": account1}
    )
    debt = REIMBURSEMENT.deploy(
        reimburse_state,
        payment_frequency,
        parameters,
        maturity_date,
        face_value,
        interest_rate,
        {"from": account1},
    )
    amount = 50
    asset.transfer(account, amount, {"from": account1})
    payment_token.transfer(debt, amount * face_value, {"from": account1})
    start_date = int((datetime.now() + timedelta(days=2)).timestamp())
    end_date = int((datetime.now() + timedelta(days=4)).timestamp())
    asset.transferOwnership(debt, {"from": account1})
    asset.transfer(debt, asset.balanceOf(account1), {"from": account1})
    # Checking 'Start Date is Non Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        debt.putToken(50, {"from": account})
    # ---------------------------------------------
    debt.setPutPeriod(start_date, end_date, {"from": account1})
    # Act
    # Checking 'Start Date <= Current Time' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        debt.putToken(50, {"from": account})
    # ---------------------------------------------
    chain.sleep(86400 * 3)
    chain.mine(1)
    # Checking 'Amount is Non Zero' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        debt.putToken(0, {"from": account})
    # ---------------------------------------------
    put_amount = 20
    debt.putToken(put_amount, {"from": account})
    # Assert
    assert payment_token.balanceOf(account) == put_amount * face_value
    assert asset.balanceOf(account) == amount - put_amount
    assert asset.totalSupply() == initial_supply - put_amount
    # Checking 'Investor Exists' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        debt.putToken(50, {"from": account2})
    # ---------------------------------------------
    # Checking 'Token Holder Balance >= Amount' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        debt.putToken(50, {"from": account})
    # ---------------------------------------------
    # Checking 'Insufficient Balance' Condition
    # ---------------------------------------------
    debt.issueToken(amount, account2, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        debt.putToken(amount, {"from": account2})
    # ---------------------------------------------
    # Checking 'Current Time <= End Date' Condition
    # ---------------------------------------------
    chain.sleep(86400 * 5)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        debt.putToken(put_amount, {"from": account})
    # ---------------------------------------------
