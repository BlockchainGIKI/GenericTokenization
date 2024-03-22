from scripts.helpfulscripts import get_account
from web3 import Web3
from eth_abi import encode_abi
from eth_account.messages import encode_defunct
from eth_account import Account
from datetime import datetime
from brownie import (
    IdentityRegistry,
    ClaimTopicsRegistry,
    TrustedIssuersRegistry,
    IdentityRegistryStorage,
    Identity,
    ClaimIssuer,
    Token,
    ERC20Mock,
    PaymentToken,
    accounts,
    config,
)


def test():
    # Setting up accounts and deploying contracts
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
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
    signedObject = Account.sign_message(msg, config["wallets"]["from_key"])

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
    # claimIssuer.revokeClaim(claimRequestId, identity.address, {"from": account1})
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

    # Testing execute and approve functions
    # calldata = token.test.encode_input()
    # execute_tx = identity.execute(token.address, 0, calldata, {"from": account})

    payment_token = PaymentToken.deploy(1e9, {"from": account})
    token = Token.deploy(
        "Name",
        "Symbol",
        1e9,
        0,
        int(datetime(2025, 3, 5, 19, 14).timestamp()),
        payment_token.address,
        identityRegistry.address,
        100,
        {"from": account},
    )


def deploy():
    # Setting up accounts and deploying contracts
    account = get_account()
    account1 = accounts.add(config["wallets"]["from_key"])
    account2 = get_account(2)
    trustedIssuersRegistry = TrustedIssuersRegistry.deploy({"from": account})
    claimTopicsRegistry = ClaimTopicsRegistry.deploy({"from": account})
    identityStorage = IdentityRegistryStorage.deploy({"from": account})
    identityRegistry = IdentityRegistry.deploy(
        trustedIssuersRegistry, claimTopicsRegistry, identityStorage, {"from": account}
    )
    identity = Identity.deploy(account, False, {"from": account})
    identity2 = Identity.deploy(account2, False, {"from": account2})
    claimIssuer = ClaimIssuer.deploy(account1, {"from": account})

    # Registering the claim key with the identity contract
    encoded_data = encode_abi(["address"], [account1.address])
    account1_key = Web3.keccak(encoded_data)
    identity.addKey(account1_key, 3, 1, {"from": account})
    identity2.addKey(account1_key, 3, 1, {"from": account2})

    # Adding claim
    data = Web3.toBytes(text="CFI code test")
    encoded_message = encode_abi(
        ["address", "uint256", "bytes"], [identity.address, 1947, data]
    )
    encoded_message2 = encode_abi(
        ["address", "uint256", "bytes"], [identity2.address, 1947, data]
    )
    hashed_message = Web3.keccak(encoded_message)
    hashed_message2 = Web3.keccak(encoded_message2)
    msg = encode_defunct(hexstr=str(hashed_message.hex()))
    msg2 = encode_defunct(hexstr=str(hashed_message2.hex()))
    signedObject = Account.sign_message(msg, config["wallets"]["from_key"])
    signedObject2 = Account.sign_message(msg2, config["wallets"]["from_key"])
    identity.addClaim(
        1947,
        1,
        claimIssuer.address,
        signedObject.signature,
        data,
        "Placeholder URI",
        {"from": account},
    )
    identity2.addClaim(
        1947,
        1,
        claimIssuer.address,
        signedObject2.signature,
        data,
        "Placeholder URI",
        {"from": account2},
    )

    # Adding identity to the identity registry
    identityRegistry.registerIdentity(account, identity, 586)
    identityRegistry.registerIdentity(account2, identity2, 586)

    # Adding trusted claim issuer to trusted issuers registry
    trustedIssuersRegistry.addTrustedIssuer(
        claimIssuer.address, [1947], {"from": account}
    )

    # Adding claim topic to Claim Topics Registry
    claimTopicsRegistry.addClaimTopic(1947, {"from": account})

    # Deploying tokens
    payment_token = PaymentToken.deploy(1e12, {"from": account1})
    # token = Token.deploy(
    #     "Name",
    #     "Symbol",
    #     1e9,
    #     0,
    #     int(datetime(2025, 3, 5, 19, 14).timestamp()),
    #     payment_token.address,
    #     identityRegistry.address,
    #     100,
    #     {"from": account},
    # )
    # # print(identityRegistry.isVerified(account))
    # # print(identityRegistry.isVerified(account2))
    # temp = int(datetime(2025, 3, 5, 19, 14).timestamp())

    return (payment_token, identityRegistry)


def main():
    (payment_token, identityRegistry) = deploy()
    # account = get_account()
    # token = Token.deploy(
    #     "Some",
    #     "Some",
    #     1e6,
    #     0,
    #     0,
    #     0,
    #     int(datetime(2025, 3, 5, 19, 14).timestamp()),
    #     account,
    #     account,
    #     1000,
    #     {"from": account},
    # )
    # params = {
    #     "receiptNumber": 1,
    #     "date": 2,
    #     "tokenHolder": account,
    #     "amount": 1947,
    #     "signature": "0x1947",
    # }
    # print(token.test((1, 2, account, 1947, "0x9")))
