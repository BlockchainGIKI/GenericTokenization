from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import (
    Parameters,
    EXERCISE,
    Asset,
    exceptions,
    chain,
    accounts,
    config,
)
import pytest
from datetime import datetime


def test_can_deploy_exercise():
    # Arrange
    account1 = accounts.add(config["wallets"]["from_key"])
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
    exercise_option_style = 1
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    start_date = 1947
    periodicity = 3
    # Act
    # Checking 'Expiration Date > Current Time' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        exercise = EXERCISE.deploy(
            exercise_option_style,
            int(datetime(2022, 3, 13, 12, 42).timestamp()),
            start_date,
            periodicity,
            parameters.address,
            {"from": account1},
        )
    # ---------------------------------------------
    exercise = EXERCISE.deploy(
        exercise_option_style,
        expiration_date,
        start_date,
        periodicity,
        parameters.address,
        {"from": account1},
    )
    # Assert
    assert exercise.exerciseOptionStyle() == exercise_option_style
    # Checking 'Start Date > Current Time' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        exercise1 = EXERCISE.deploy(
            2,
            expiration_date,
            int(datetime(2022, 7, 13, 12, 42).timestamp()),
            periodicity,
            parameters.address,
            {"from": account1},
        )
    # ---------------------------------------------
    # Checking 'Start Date < Expiration Date' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        exercise2 = EXERCISE.deploy(
            2,
            expiration_date,
            int(datetime(2026, 7, 13, 12, 42).timestamp()),
            periodicity,
            parameters.address,
            {"from": account1},
        )
    # ---------------------------------------------


def test_can_exercise_american_token():
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
    exercise_option_style = 0
    expiration_date = int(datetime(2025, 3, 13, 12, 42).timestamp())
    start_date = 1947
    periodicity = 3
    exercise = EXERCISE.deploy(
        exercise_option_style,
        expiration_date,
        start_date,
        periodicity,
        parameters.address,
        {"from": account1},
    )
    amount = 50
    asset.transfer(account, amount, {"from": account1})
    # Act
    exercise.exercise({"from": account})
    # Assert
    assert exercise.investorToExerciseStatus(account) == True
    # Checking 'Investor Exists' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        exercise.exercise({"from": account2})
    # ---------------------------------------------
    # Checking 'Already Exercised' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        exercise.exercise({"from": account})
    # ---------------------------------------------
    # Checking 'American Expiration Check' Condition
    # ---------------------------------------------
    asset.transfer(account2, amount, {"from": account1})
    chain.sleep(31556952 * 2)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        exercise.exercise({"from": account2})
    # ---------------------------------------------


def test_can_exercise_european_token():
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
    exercise_option_style = 1
    expiration_date = int(datetime(2025, 4, 24, 12, 42).timestamp())
    start_date = 1947
    periodicity = 3
    exercise = EXERCISE.deploy(
        exercise_option_style,
        expiration_date,
        start_date,
        periodicity,
        parameters.address,
        {"from": account1},
    )
    amount = 50
    asset.transfer(account, amount, {"from": account1})
    # Act
    chain.sleep(31556952)
    chain.mine(1)
    exercise.exercise({"from": account})
    # Assert
    assert exercise.investorToExerciseStatus(account) == True
    # Checking 'European Expiration Check' Condition
    # ---------------------------------------------
    asset.transfer(account2, amount, {"from": account1})
    chain.sleep(86400 * 2)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        exercise.exercise({"from": account2})
    # ---------------------------------------------


def test_can_exercise_bermudan_token():
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
    exercise_option_style = 2
    expiration_date = int(datetime(2025, 4, 24, 0, 0).timestamp())
    start_date = int(datetime(2024, 4, 25, 0, 0).timestamp())
    periodicity = 1
    exercise = EXERCISE.deploy(
        exercise_option_style,
        expiration_date,
        start_date,
        periodicity,
        parameters.address,
        {"from": account1},
    )
    amount = 50
    asset.transfer(account, amount, {"from": account1})
    asset.transfer(account2, amount, {"from": account1})
    # Act
    # Checking 'Premature Exercise Attempt' Condition
    # ---------------------------------------------
    with pytest.raises(exceptions.VirtualMachineError):
        exercise.exercise({"from": account})
    # ---------------------------------------------
    chain.sleep(604800 + 86400)
    chain.mine(1)
    # duration = exercise.getDuration()
    # print(duration)
    print(exercise.getTimestamp())
    exercise.exercise({"from": account})
    # Checking 'Invalid Exercise Attempt Of Bermudan Option' Condition
    # ---------------------------------------------
    chain.sleep(86400)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        exercise.exercise({"from": account2})
    # ---------------------------------------------
    chain.sleep(31556952 - 604800 - 86400 - 86400)
    chain.mine(1)
    exercise.exercise({"from": account2})
    # Assert
    assert exercise.investorToExerciseStatus(account) == True
    assert exercise.investorToExerciseStatus(account2) == True
    # Checking 'Bermudan Option Expired' Condition
    # ---------------------------------------------
    exercise1 = EXERCISE.deploy(
        exercise_option_style,
        int(datetime(2025, 5, 24, 0, 0).timestamp()),
        int(datetime(2025, 4, 30, 0, 0).timestamp()),
        periodicity,
        parameters.address,
        {"from": account1},
    )
    chain.sleep(31556952 * 2)
    chain.mine(1)
    with pytest.raises(exceptions.VirtualMachineError):
        exercise1.exercise({"from": account})
    # ---------------------------------------------
