import json
from algosdk import account, transaction
from algosdk.v2client import algod

ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Create new account (for demo, generate 1 time)
def create_account():
    private_key, address = account.generate_account()
    print("Address:", address)
    print("Private key:", private_key)
    return private_key, address

def store_prediction(sender_pk, sender_address, prediction):
    params = algod_client.suggested_params()
    unsigned_txn = transaction.PaymentTxn(
        sender=sender_address,
        sp=params,
        receiver=sender_address,  # send to self (for demo)
        amt=0,
        note=json.dumps({"AI_Prediction": prediction}).encode()
    )
    signed_txn = unsigned_txn.sign(sender_pk)
    txid = algod_client.send_transaction(signed_txn)
    print("Transaction ID:", txid)
    return txid
