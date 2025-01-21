import os
from engines.modules.blockchain_wallet import BlockchainWallet

class WalletContextEngine:
    """
    Gathers and processes real-time wallet context for the Nova system.
    """

    def __init__(self):
        self.name = "WalletContextEngine"
        # It's best to keep your API key in an environment variable:
        # export INFURA_API_KEY="your_api_key"
        self.rpc_url = "https://mainnet.base.org"
    
    def gather_context(self):
        """
        Fetches wallet data through an RPC API.
        """
        if not self.rpc_url:
            print("No RPC URL found. Please set INFURA_RPC_URL in your environment.")
            return {}

        private_key = os.environ.get("WALLET_PRIVATE_KEY", "")
        if not private_key:
            print("No private key found. Please set WALLET_PRIVATE_KEY in your environment.")
            return {}

        wallet = BlockchainWallet(self.rpc_url, private_key)
        address = wallet.get_address()
        balance = wallet.get_balance()
        transaction_count = wallet.get_transaction_count()

        # Build a dictionary of relevant wallet data.
        wallet_context = {
            "address": address,
            "balance": str(balance),
            "transaction_count": transaction_count,
        }

        print(f"Wallet context gathered: {wallet_context}")
        return wallet_context

    def run(self):
        """
        Runs the engine, returning or optionally logging the wallet data.
        """
        wallet_data = self.gather_context()
        # Here you could store, log, or further process the wallet_data
        