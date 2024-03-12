from scripts.helpfulscripts import get_account
from web3 import Web3
from eth_abi import encode_abi
from eth_account.messages import encode_defunct
from eth_account import Account
from brownie import (
    IdentityRegistry,
    ClaimTopicsRegistry,
    TrustedIssuersRegistry,
    IdentityRegistryStorage,
    Identity,
    ClaimIssuer,
    accounts,
)


def deploy():
    # Setting up accounts and deploying contracts
    account = get_account()
    account1 = accounts.add(
        private_key="0x416b8a7d9290502f5661da81f0cf43893e3d19cb9aea3c426cfb36e8186e9c09"
    )
    trustedIssuersRegistry = TrustedIssuersRegistry.deploy({"from": account})
    claimTopicsRegistry = ClaimTopicsRegistry.deploy({"from": account})
    identityStorage = IdentityRegistryStorage.deploy({"from": account})
    identityRegistry = IdentityRegistry.deploy(
        trustedIssuersRegistry, claimTopicsRegistry, identityStorage, {"from": account}
    )
    identity = Identity.deploy(account, False, {"from": account})
    claimIssuer = ClaimIssuer.deploy(account1, {"from": account})

    # Registering the claim key with the identity contract
    encoded_data = encode_abi(["address"], [account1.address])
    account1_key = Web3.keccak(encoded_data)
    print("Claim Key: {}".format(account1_key.hex()))
    identity.addKey(account1_key, 3, 1, {"from": account})

    # Signing the message
    data = Web3.toBytes(text="CFI code test")
    encoded_message = encode_abi(
        ["address", "uint256", "bytes"], [identity.address, 1947, data]
    )
    hashed_message = Web3.keccak(encoded_message)
    print(hashed_message.hex())
    msg = encode_defunct(hexstr=str(hashed_message.hex()))
    signedObject = Account.sign_message(
        msg, "0x416b8a7d9290502f5661da81f0cf43893e3d19cb9aea3c426cfb36e8186e9c09"
    )

    # Adding claim
    a = claimIssuer.isClaimValid(identity.address, 1947, signedObject.signature, data)
    b = identity.isClaimValid(identity.address, 1947, signedObject.signature, data)
    print(a, b)
    addClaim_tx = identity.addClaim(
        1947,
        1,
        claimIssuer.address,
        signedObject.signature,
        data,
        "Nothing",
        {"from": account},
    )
    addClaim_tx.wait(1)
    claimRequestId = addClaim_tx.events["ClaimAdded"]["claimId"]
    print("Claim Request Id: {}".format(claimRequestId))

    claim = identity.getClaim(claimRequestId)
    print("Claim: {}".format(claim))

    # Adding identity to the identity registry
    identityRegistry.registerIdentity(account, identity, 586)

    # Adding trusted claim issuer to trusted issuers registry
    trustedIssuersRegistry.addTrustedIssuer(
        claimIssuer.address, [1947], {"from": account}
    )
    print(
        "List of Trusted Issuers: {}".format(trustedIssuersRegistry.getTrustedIssuers())
    )
    print(
        "Types of Claims Issued by {}:  {}".format(
            claimIssuer, trustedIssuersRegistry.getTrustedIssuerClaimTopics(claimIssuer)
        )
    )

    # Adding claim topic to Claim Topics Registry
    claimTopicsRegistry.addClaimTopic(1947, {"from": account})
    print(
        "Claim Topics in Claim Topics Registry: {}".format(
            claimTopicsRegistry.getClaimTopics()
        )
    )

    # Revoking claim
    claimIssuer.revokeClaim(claimRequestId, identity.address, {"from": account1})
    print(
        "Is Claim #{} revoked: {}".format(
            claimRequestId, claimIssuer.isClaimRevoked(signedObject.signature)
        )
    )
    print(
        "Verification status of {}: {}".format(
            identity, identityRegistry.isVerified(account)
        )
    )


def main():
    deploy()
