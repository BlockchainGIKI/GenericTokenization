from scripts.helpfulscripts import get_account
from scripts.deploy import deploy
from brownie import Asset, exceptions
import pytest


def test_can_transfer():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    account2 = get_account(2)
    account3 = get_account(3)
    (_, identityRegistry) = deploy()
    asset = Asset.deploy(
        100, "Token", "Symbol", identityRegistry.address, {"from": account1}
    )
    # Act
    asset.transfer(account, 50, {"from": account1})
    # Assert
    assert asset.balanceOf(account) == 50
    assert asset.tokenHolders(0) == account
    asset.transfer(account2, 50, {"from": account})
    assert asset.balanceOf(account2) == 50
    assert asset.tokenHolders(0) == account2
    with pytest.raises(exceptions.VirtualMachineError):
        asset.transfer(account, 100, {"from": account1})
    with pytest.raises(exceptions.VirtualMachineError):
        asset.transfer(account3, 25, {"from": account1})


def test_can_transfer_from():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    account2 = get_account(2)
    account3 = get_account(3)
    (_, identityRegistry) = deploy()
    asset = Asset.deploy(
        100, "Token", "Symbol", identityRegistry.address, {"from": account1}
    )
    # Act
    asset.approve(account3, 100, {"from": account1})
    asset.transferFrom(account1, account, 50, {"from": account3})
    # Assert
    assert asset.balanceOf(account) == 50
    assert asset.tokenHolders(0) == account
    asset.approve(account3, 500, {"from": account})
    asset.transferFrom(account, account2, 50, {"from": account3})
    assert asset.balanceOf(account2) == 50
    assert asset.tokenHolders(0) == account2
    with pytest.raises(exceptions.VirtualMachineError):
        asset.transferFrom(account1, account, 100, {"from": account3})
    with pytest.raises(exceptions.VirtualMachineError):
        asset.transferFrom(account1, account3, 25, {"from": account3})
