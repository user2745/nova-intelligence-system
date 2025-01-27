# blockchain_merc.py
from rx import operators as ops
import os
from web3 import Web3
from utils.blockchain_wallet import BlockchainWallet

class EVMMercenaries:
    def __init__(self, ucp):
        # Subscribe to transaction commands
        self.ucp = ucp
        self.wallet = BlockchainWallet(
            rpc_url="https://mainnet.base.org",
            private_key = os.environ.get("WALLET_PRIVATE_KEY", "")
        )
        ucp.command_stream.pipe(
            ops.filter(lambda cmd: cmd.get("action") == "send_funds")
        ).subscribe(self._execute_transaction)

    def _execute_transaction(self, cmd: dict):
        try:
            print(f"⚡️ Mercenary executing: {cmd}")
            
            # Extract amount from params sub-object
            to_address = cmd.get("params", {}).get("to_address", "")
            amount = cmd.get("params", {}).get("amount", 0)
            
            tx_hash = self.wallet.send_transaction(to_address, amount)
            self.ucp.emit_response({
                "type": "transaction_success",
                "tx_hash": tx_hash,
                "original_cmd": cmd
            })
        except Exception as e:
            print(f"💥 Mercenary error: {str(e)}")
            self.ucp.emit_response({
                "type": "transaction_failed",
                "error": str(e)
            })