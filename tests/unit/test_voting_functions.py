from scripts.helpfulscripts import get_account
from brownie import Voting, exceptions
import pytest


def test_can_create_ballot():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    voting = Voting.deploy({"from": account})
    # Act
    voting.createBallot(
        "Which color is the best?",
        ["Black", "Blue", "Orange", "Red", "Brown"],
        1709181605,
        400,
        {"from": account},
    )
    # Assert
    assert voting.ballots(0)[0] == "Which color is the best?"
    assert voting.ballots(0)[1] == 1709181605
    assert voting.ballots(0)[3] == 0
    assert voting.options(0, 3) == "Red"
    with pytest.raises(exceptions.VirtualMachineError):
        voting.createBallot(
            "Which color is the best?",
            ["Black", "Blue", "Orange", "Red", "Brown"],
            1709181605,
            400,
            {"from": account1},
        )


def test_can_create_voter():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    account2 = get_account(2)
    voting = Voting.deploy({"from": account})
    # Act
    voting.createVoter(1, account1, {"from": account})
    # Assert
    assert voting.voters(account1)[0] == 1
    assert voting.voters(account1)[2] == True
    with pytest.raises(exceptions.VirtualMachineError):
        voting.createVoter(1, account1, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        voting.createVoter(1, account, {"from": account1})


def test_can_update_weight():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    voting = Voting.deploy({"from": account})
    voting.createVoter(1, account1, {"from": account})
    # Act
    voting.updateWeight(15, account1, {"from": account})
    # Assert
    assert voting.voters(account1)[0] == 15
    with pytest.raises(exceptions.VirtualMachineError):
        voting.updateWeight(20, account1, {"from": account1})


def test_can_start_voting():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    voting = Voting.deploy({"from": account})
    voting.createBallot(
        "Which color is the best?",
        ["Black", "Blue", "Orange", "Red", "Brown"],
        1709181605,
        400,
        {"from": account},
    )
    # Act
    with pytest.raises(exceptions.VirtualMachineError):
        voting.startVoting(0, {"from": account1})
    voting.startVoting(0, {"from": account})
    # Assert
    assert voting.ballots(0)[3] == 1
    with pytest.raises(exceptions.VirtualMachineError):
        voting.startVoting(0, {"from": account})


def test_can_end_voting():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    voting = Voting.deploy({"from": account})
    voting.createBallot(
        "Which color is the best?",
        ["Black", "Blue", "Orange", "Red", "Brown"],
        1709181605,
        400,
        {"from": account},
    )
    voting.startVoting(0, {"from": account})
    # Act
    with pytest.raises(exceptions.VirtualMachineError):
        voting.endVoting(0, {"from": account1})
    voting.endVoting(0, {"from": account})
    # Assert
    assert voting.ballots(0)[3] == 2
    with pytest.raises(exceptions.VirtualMachineError):
        voting.startVoting(0, {"from": account})


def test_can_cast_vote():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    account2 = get_account(2)
    voting = Voting.deploy({"from": account})
    voting.createBallot(
        "Which color is the best?",
        ["Black", "Blue", "Orange", "Red", "Brown"],
        1709181605,
        400,
        {"from": account},
    )
    voting.createBallot(
        "Yes or No?",
        ["Yes", "No"],
        1709181605,
        400,
        {"from": account},
    )
    voting.createVoter(0, account1, {"from": account})
    voting.createVoter(1, account2, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        voting.castVote(0, 1, {"from": account2})
    voting.startVoting(0, {"from": account})
    voting.startVoting(1, {"from": account})
    # Act
    with pytest.raises(exceptions.VirtualMachineError):
        voting.castVote(0, 2, {"from": account1})
    voting.castVote(0, 1, {"from": account2})
    voting.castVote(1, 0, {"from": account2})
    # Assert
    assert voting.voted(account2, 0) == True
    assert voting.voted(account2, 1) == True
    assert voting.tally(0, 1) == 1
    assert voting.tally(1, 0) == 1
    with pytest.raises(exceptions.VirtualMachineError):
        voting.castVote(0, 2, {"from": account2})


def test_can_compute_winning_option():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    account2 = get_account(2)
    voting = Voting.deploy({"from": account})
    voting.createBallot(
        "Which color is the best?",
        ["Black", "Blue", "Orange", "Red", "Brown"],
        1709181605,
        400,
        {"from": account},
    )
    voting.createBallot(
        "Yes or No?",
        ["Yes", "No"],
        1709181605,
        400,
        {"from": account},
    )
    voting.createVoter(2, account1, {"from": account})
    voting.createVoter(1, account2, {"from": account})
    voting.startVoting(0, {"from": account})
    voting.startVoting(1, {"from": account})
    voting.castVote(0, 1, {"from": account1})
    voting.castVote(1, 1, {"from": account1})
    voting.castVote(0, 1, {"from": account2})
    voting.castVote(1, 0, {"from": account2})
    with pytest.raises(exceptions.VirtualMachineError):
        voting.calculateWinningOption(0, {"from": account})
    voting.endVoting(0, {"from": account})
    voting.endVoting(1, {"from": account})
    # Act
    voting.calculateWinningOption(0, {"from": account})
    voting.calculateWinningOption(1, {"from": account})
    # Assert
    assert voting.viewBallotResult(0) == "Blue"
    assert voting.viewBallotResult(1) == "No"


def test_can_delegate_vote():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    account2 = get_account(2)
    account3 = get_account(3)
    account4 = get_account(4)
    account5 = get_account(5)
    voting = Voting.deploy({"from": account})
    voting.createBallot(
        "Yes or No?",
        ["Yes", "No"],
        1709181605,
        400,
        {"from": account},
    )
    voting.createVoter(0, account1, {"from": account})
    voting.createVoter(1, account2, {"from": account})
    voting.createVoter(1, account3, {"from": account})
    voting.createVoter(5, account4, {"from": account})
    voting.createVoter(6, account5, {"from": account})
    voting.startVoting(0, {"from": account})
    # Act
    voting.delegateVote(account5, 0, {"from": account4})
    # Assert
    assert voting.voted(account4, 0) == True
    assert voting.voters(account5)[0] == 11
    with pytest.raises(exceptions.VirtualMachineError):
        voting.delegateVote(account2, 0, {"from": account1})
    voting.castVote(0, 1, {"from": account2})
    with pytest.raises(exceptions.VirtualMachineError):
        voting.delegateVote(account3, 0, {"from": account2})
    with pytest.raises(exceptions.VirtualMachineError):
        voting.delegateVote(account, 0, {"from": account3})
    with pytest.raises(exceptions.VirtualMachineError):
        voting.delegateVote(account1, 0, {"from": account3})
    with pytest.raises(exceptions.VirtualMachineError):
        voting.delegateVote(account2, 0, {"from": account3})


def test_can_handle_tied_vote():
    # Arrange
    account = get_account()
    account1 = get_account(1)
    account2 = get_account(2)
    voting = Voting.deploy({"from": account})
    voting.createBallot(
        "Yes or No?",
        ["Yes", "No"],
        1709181605,
        400,
        {"from": account},
    )
    voting.createVoter(1, account1, {"from": account})
    voting.createVoter(1, account2, {"from": account})
    voting.startVoting(0, {"from": account})
    voting.castVote(0, 1, {"from": account1})
    voting.castVote(0, 0, {"from": account2})
    voting.endVoting(0, {"from": account})
    # Act
    voting.calculateWinningOption(0, {"from": account})
    # Assert
    assert voting.viewBallotResult(0) == "Tied Vote"
