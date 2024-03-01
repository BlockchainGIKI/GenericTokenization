// SPDX-License-Identifier: MIT

pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";

contract Voting is Ownable {
    enum Vote_State {
        Ballot_Created,
        Voting_Started,
        Voting_Ended
    }

    struct Ballot {
        string proposal;
        uint256 startTime;
        uint256 duration;
        Vote_State state;
        uint256 winningOption;
    }

    struct Voter {
        uint256 weight;
        address delegate;
        bool registered;
    }

    mapping(address => Voter) public voters;
    mapping(uint256 => Ballot) public ballots;
    mapping(uint256 => string[]) public options;
    mapping(address => mapping(uint256 => bool)) public voted;
    mapping(uint256 => mapping (uint256 => uint256)) public tally;
    uint256 private count;

    function createBallot(
        string memory _proposal,
        string[] memory _options,
        uint256 _startTime,
        uint256 _duration
    ) external onlyOwner {
        
        ballots[count] = Ballot(
            _proposal,
            _startTime,
            _duration,
            Vote_State.Ballot_Created,
            0
        );
        options[count] = _options;
        count++;
    }

    function createVoter(uint256 _weight, address _voter) public onlyOwner {
        require(voters[_voter].registered != true, "This voter already exists");
        voters[_voter] = Voter(_weight, address(0), true);
    }

    function updateWeight(uint256 _weight, address _voter) public onlyOwner {
        voters[_voter].weight = _weight;
    }

    function startVoting(uint256 _ballot) public onlyOwner {
        require(ballots[_ballot].state == Vote_State.Ballot_Created, "You can't start voting when the state is Voting_Started/Voting_Ended");
        ballots[_ballot].state = Vote_State.Voting_Started;
    }

    function endVoting(uint256 _ballot) public onlyOwner {
        require(ballots[_ballot].state == Vote_State.Voting_Started, "You can't end voting when the state is Ballot_Created/Voting_Started");
        ballots[_ballot].state = Vote_State.Voting_Ended;
    }

    function delegateVote(address _delegatee, uint256 _ballot) public {
        require(voters[msg.sender].weight !=0, "You have no right to vote");
        require(voted[msg.sender][_ballot] != true, "You have already voted in this ballot");
        require(voters[_delegatee].registered == true, "The delegatee is not registered as a voter");
        require(voters[_delegatee].weight >0 , "The delegatee is not allowed to vote");
        require(voted[_delegatee][_ballot] != true, "The delegatee already voted");
        voters[msg.sender].delegate = _delegatee;
        voted[msg.sender][_ballot] = true;
        voters[_delegatee].weight += voters[msg.sender].weight;
    }

    function castVote(uint256 _ballot, uint256 _option) public {
        require(ballots[_ballot].state == Vote_State.Voting_Started, "You can only vote if the voting period has started");
        require(voters[msg.sender].weight > 0, "You don't have permission to vote in this ballot");
        require(voted[msg.sender][_ballot] != true, "You have already cast your vote for this ballot");
        tally[_ballot][_option]+=voters[msg.sender].weight;
        voted[msg.sender][_ballot] = true;
    }

    function calculateWinningOption(uint256 _ballot) public {
        require(ballots[_ballot].state == Vote_State.Voting_Ended, "You can only count votes when the voting period has finished");
        uint256 winningVoteCount = 0;
        uint256 winningOption = 0;
        uint256 tiedOptionsCount = 0;
        for (uint256 i =0; i<options[_ballot].length; i++){
            if (tally[_ballot][i] > winningVoteCount) {
                winningVoteCount = tally[_ballot][i];
                winningOption = i;
                tiedOptionsCount = 0;
            }
            else if (tally[_ballot][i] == winningVoteCount){
                tiedOptionsCount++;
            }
        }
        if (tiedOptionsCount > 0)
        {
            ballots[_ballot].winningOption = options[_ballot].length + 1;
        }
        else {
        ballots[_ballot].winningOption = winningOption;
        }
    }

    function viewBallotResult(uint256 _ballot) public view returns (string memory){
        require(ballots[_ballot].state == Vote_State.Voting_Ended, "You can only view results when the voting period has ended");
        if (ballots[_ballot].winningOption > options[_ballot].length)
        {
            return "Tied Vote";
        }
        else{
        return options[_ballot][ballots[_ballot].winningOption];
        }
    }
}
