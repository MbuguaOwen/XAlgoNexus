# /src/risk_manager/risk_manager.py

import logging
from datetime import datetime

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("risk_manager")


class RiskManager:
    """
    Enforces risk constraints on trade execution decisions.
    Includes slippage filtering, size limits, and daily loss caps.
    """

    def __init__(self, max_position_size: float = 5000.0, max_daily_loss: float = 0.02, slippage_tolerance: float = 0.0015):
        """
        Args:
            max_position_size (float): Maximum USD value per trade
            max_daily_loss (float): Max daily P&L drawdown as fraction (e.g., 0.02 = -2%)
            slippage_tolerance (float): Maximum tolerated slippage before blocking execution
        """
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.slippage_tolerance = slippage_tolerance

        self.current_exposure = 0.0  # Not yet used, placeholder for future leverage logic
        self.daily_pnl = 0.0
        self.start_of_day = datetime.utcnow().date()

    def reset_daily_limits(self):
        """
        Resets daily limits if the day has rolled over.
        """
        today = datetime.utcnow().date()
        if today != self.start_of_day:
            logger.info("[RISK] Resetting daily P&L and session counters.")
            self.daily_pnl = 0.0
            self.start_of_day = today

    def check_trade_permission(self, signal: dict, estimated_trade_value: float, slippage_estimate: float) -> bool:
        """
        Validates whether a trade may be executed under current risk constraints.

        Args:
            signal (dict): Trade signal
            estimated_trade_value (float): Value of trade in USD
            slippage_estimate (float): Slippage in decimal (e.g., 0.0004)

        Returns:
            bool: Whether the trade is allowed
        """
        self.reset_daily_limits()

        # Daily loss cap check
        if self.daily_pnl < (-self.max_daily_loss):
            logger.warning("[RISK] ❌ Daily loss limit exceeded.")
            return False

        # Position size check
        if estimated_trade_value > self.max_position_size:
            logger.warning(f"[RISK] ❌ Trade size {estimated_trade_value:.2f} > allowed max {self.max_position_size:.2f}.")
            return False

        # Slippage check
        if slippage_estimate > self.slippage_tolerance:
            logger.warning(f"[RISK] ❌ Slippage {slippage_estimate:.5f} exceeds tolerance {self.slippage_tolerance:.5f}.")
            return False

        logger.info(f"[RISK] ✅ Trade approved: {signal['decision']} | Est. Value: ${estimated_trade_value:.2f} | Slippage: {slippage_estimate:.5f}")
        return True

    def update_pnl(self, realized_pnl: float):
        """
        Updates current day's realized PnL.

        Args:
            realized_pnl (float): Profit or loss from latest trade
        """
        self.daily_pnl += realized_pnl
        logger.info(f"[RISK] 📈 Updated Daily PnL: {self.daily_pnl:.4f}")

    def get_daily_status(self) -> dict:
        """
        Returns:
            dict: Daily performance and risk metrics
        """
        return {
            "pnl": round(self.daily_pnl, 4),
            "max_loss_allowed": -self.max_daily_loss,
            "date": self.start_of_day.isoformat()
        }


if __name__ == "__main__":
    logger.info("[XALGO] Risk Manager Initialized.")
