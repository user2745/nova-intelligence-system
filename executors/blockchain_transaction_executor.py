import logging
from web3 import Web3

logging.basicConfig(level=logging.INFO)

class BlockchainTransactionExecutor:
    def __init__(self, wallet):
        self.wallet = wallet

    async def run(self, task_data):
        try:
            logging.info(f"Starting transaction: {task_data}")
            to_address = task_data["to_address"]
            amount = task_data["amount"]
            logging.info(f"Initiating transaction: {amount} WEI to {to_address}")
            tx_hash = self.wallet.send_transaction(to_address, amount)
            logging.info(f"Transaction successful. Hash: {tx_hash}")
            return {"status": "success", "tx_hash": tx_hash}
        except Exception as e:
            logging.error(f"Transaction failed: {e}")
            return {"status": "error", "message": str(e)}
