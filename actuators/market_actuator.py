import logging
import random
from .actuator_manager import Actuator

class MarketActuator(Actuator):
    """
    Actuator for financial operations.
    Currently simulates trades and balance checks.
    Future: Integrate with real exchange APIs (Coinbase/Binance).
    """
    def __init__(self):
        super().__init__("market")
        self.register_tool("execute_trade", self.execute_trade, "Execute a crypto trade (SIMULATED)")
        self.register_tool("check_balance", self.check_balance, "Check wallet balance")
        
        # Simulated wallet for now
        self.wallet = {
            "ETH": 4.5853742e-11, # Real dust from user's wallet
            "BTC": 0.0,
            "USDT": 1000.0 # Simulated starting capital
        }

    async def execute_trade(self, symbol: str, action: str, amount: float) -> str:
        """
        Simulate a trade.
        action: 'buy' or 'sell'
        """
        symbol = symbol.upper()
        action = action.lower()
        
        logging.info(f"[MarketActuator] 💸 Processing trade: {action} {amount} {symbol}")
        
        # Mock prices
        prices = {"ETH": 3000.0, "BTC": 90000.0}
        price = prices.get(symbol, 100.0)
        cost = amount * price

        if action == "buy":
            if self.wallet["USDT"] >= cost:
                self.wallet["USDT"] -= cost
                self.wallet[symbol] = self.wallet.get(symbol, 0.0) + amount
                return f"✅ SUCCESS: Bought {amount} {symbol} @ ${price}. New USDT Balance: ${self.wallet['USDT']:.2f}"
            else:
                return f"❌ FAILED: Insufficient USDT. Required: ${cost:.2f}, Available: ${self.wallet['USDT']:.2f}"
        
        elif action == "sell":
            if self.wallet.get(symbol, 0.0) >= amount:
                self.wallet[symbol] -= amount
                self.wallet["USDT"] += cost
                return f"✅ SUCCESS: Sold {amount} {symbol} @ ${price}. New USDT Balance: ${self.wallet['USDT']:.2f}"
            else:
                return f"❌ FAILED: Insufficient {symbol}. Required: {amount}, Available: {self.wallet.get(symbol, 0.0)}"

        return "Error: Invalid action. Use 'buy' or 'sell'."

    async def check_balance(self) -> str:
        """Return formatted wallet balance."""
        balances = [f"{k}: {v:.8f}" for k, v in self.wallet.items() if v > 0]
        return " | ".join(balances)
