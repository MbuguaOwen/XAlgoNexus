from prometheus_client import Gauge
from datetime import datetime

# Prometheus Gauge
pnl_gauge = Gauge('xalgo_pnl_simulated', 'Simulated running PnL')

class PnLTracker:
    def __init__(self):
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.positions = {}  # format: {'btcusdt': {'side': 'long', 'qty': 0.005, 'entry_price': 34000.0}}

    def update_position(self, symbol, fill_price, qty, side):
        if symbol not in self.positions:
            self.positions[symbol] = {'side': side, 'qty': qty, 'entry_price': fill_price}
        else:
            pos = self.positions[symbol]
            if pos['side'] == side:
                # Average the position
                total_cost = pos['entry_price'] * pos['qty'] + fill_price * qty
                total_qty = pos['qty'] + qty
                pos['entry_price'] = total_cost / total_qty
                pos['qty'] = total_qty
            else:
                # Opposite side = reduce/close
                closing_qty = min(pos['qty'], qty)
                pnl = (fill_price - pos['entry_price']) * closing_qty
                if pos['side'] == 'short':
                    pnl = -pnl
                self.realized_pnl += pnl
                pos['qty'] -= closing_qty
                if pos['qty'] <= 0:
                    del self.positions[symbol]
        pnl_gauge.set(self.realized_pnl + self.unrealized_pnl)

    def mark_to_market(self, prices: dict):
        self.unrealized_pnl = 0.0
        for symbol, pos in self.positions.items():
            if symbol not in prices:
                continue
            current_price = prices[symbol]
            if pos['side'] == 'long':
                self.unrealized_pnl += (current_price - pos['entry_price']) * pos['qty']
            else:
                self.unrealized_pnl += (pos['entry_price'] - current_price) * pos['qty']
        pnl_gauge.set(self.realized_pnl + self.unrealized_pnl)

    def get_total_pnl(self):
        return self.realized_pnl + self.unrealized_pnl

    def summary(self):
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'positions': self.positions
        }