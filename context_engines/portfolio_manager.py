import asyncio
import requests
from context_engines.wallet_surveillance import WalletSurveillance
from execution.blockchain_merc import EVMMercenaries

class CryptoPortfolioManager:
    def __init__(self, ucp):
        self.ucp = ucp
        self.wallets = []  # List of tracked wallet addresses
        self.holdings = {}  # {symbol: balance}
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.trader = EVMMercenaries(ucp)  # Trading execution layer
        
        asyncio.create_task(self.update_prices())
        self.ucp.context_stream.subscribe(self.process_wallet_update)

    async def update_prices(self):
        while True:
            if self.holdings:
                symbols = ",".join(self.holdings.keys())
                response = requests.get(f"{self.api_url}?ids={symbols}&vs_currencies=usd")
                if response.status_code == 200:
                    data = response.json()
                    for symbol in self.holdings.keys():
                        self.holdings[symbol]['price'] = data.get(symbol, {}).get('usd', 0)
            await asyncio.sleep(60)  # Update prices every minute
    
    def process_wallet_update(self, context):
        wallet_data = context.get("wallet", {})
        address = wallet_data.get("address")
        balance = wallet_data.get("balance", 0)
        if address and balance:
            self.wallets.append(address) if address not in self.wallets else None
            self.holdings[address] = {"balance": balance, "price": 0}
        
    def get_portfolio_value(self):
        return sum(v['balance'] * v['price'] for v in self.holdings.values())
    
    def generate_report(self):
        report = "\nPortfolio Summary:\n"
        for addr, data in self.holdings.items():
            report += f"Wallet: {addr} - Balance: {data['balance']} - Price: ${data['price']} - Value: ${data['balance'] * data['price']}\n"
        report += f"\nTotal Portfolio Value: ${self.get_portfolio_value()}"
        return report
    
    def alert_price_drop(self, threshold=5):
        for addr, data in self.holdings.items():
            if data["price"] > 0 and data["balance"] * data["price"] < threshold:
                self.ucp.emit_response({
                    "action": "alert",
                    "message": f"Alert: Portfolio value for {addr} dropped below ${threshold}",
                })
    
    def execute_trade(self, action, asset, amount):
        """Execute a trade using the integrated trading engine."""
        trade_result = self.trader.execute(action, asset, amount)
        self.ucp.emit_response({
            "action": "trade_executed",
            "message": f"Executed {action} of {amount} {asset}.",
            "result": trade_result
        })
    
# Usage Example
if __name__ == "__main__":
    ucp = None  # Replace with actual UCP instance
    manager = CryptoPortfolioManager(ucp)
    print(manager.generate_report())
