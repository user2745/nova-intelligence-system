# modules/blockchain_wallet.py
import os
import logging
from web3 import Web3

logging.basicConfig(level=logging.INFO)

class BlockchainWallet:
    def __init__(self, rpc_url, private_key):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.web3.eth.account.from_key(private_key)

    def get_balance(self):
        """Fetch wallet balance."""
        balance = self.web3.eth.get_balance(self.account.address)
        return self.web3.from_wei(balance, 'ether')

    def get_address(self):
        """Get the wallet address."""
        return self.account.address
    
    def get_transaction_receipt(self, tx_hash):
        """Get the transaction receipt."""
        return self.web3.eth.get_transaction_receipt(tx_hash)
    
    def get_transaction_count(self):
        """Get the number of transactions sent from the wallet."""
        return self.web3.eth.get_transaction_count(self.account.address)
    

    def send_transaction(self, to_address, amount):
        """Send a transaction."""
        logging.info(f"Preparing to send {amount} ETH to {to_address}...")

        # Get the current nonce
        nonce = self.web3.eth.get_transaction_count(self.account.address)

        # Fetch dynamic gas price or use a default (e.g., 5 gwei)
        gas_price = self.web3.eth.gas_price
        logging.info(f"Using gas price: {self.web3.from_wei(gas_price, 'gwei')} gwei")

        # Set the gas limit for a simple transfer (21,000)
        gas_limit = 53000
        gas_fee = gas_price * gas_limit

        # Calculate total transaction cost
        total_cost = amount + gas_fee
        logging.info(f"Gas fee: {self.web3.from_wei(gas_fee, 'ether')} ETH")
        logging.info(f"Total transaction cost: {self.web3.from_wei(total_cost, 'ether')} ETH")

        # Check wallet balance
        balance = self.web3.eth.get_balance(self.account.address)
        if balance < total_cost:
            raise ValueError(
                f"Insufficient funds. Required: {self.web3.from_wei(total_cost, 'ether')} ETH, "
                f"Available: {self.web3.from_wei(balance, 'ether')} ETH."
            )

        # Construct the transaction
        transaction = {
            'to': to_address,
            'value': amount,  # Convert amount to WEI
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': 8453,  # Replace with the appropriate chain ID
        }

        # Sign and send the transaction
        signed_tx = self.account.sign_transaction(transaction)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)  # Correct case
        logging.info(f"Transaction sent. Hash: {self.web3.to_hex(tx_hash)}")
        return self.web3.to_hex(tx_hash)

    def estimate_gas(self, to_address, amount):
        """Estimate the gas required for a transaction."""
        transaction = {
            'to': to_address,
            'value': self.web3.to_wei(amount, 'ether'),
            'from': self.account.address,
        }
        return self.web3.eth.estimateGas(transaction)

        