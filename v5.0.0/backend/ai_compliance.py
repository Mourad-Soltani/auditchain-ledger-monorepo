import math
from typing import Dict, Any, Tuple


class ComplianceAnomalyEngine:
    def __init__(self, risk_threshold: float = 0.75):
        self.risk_threshold = risk_threshold
        self.mean_amount = 5000.0
        self.var_amount = 250000.0
        self.alpha = 0.05
        self.sanctioned_entities = {"SANCTIONED_NODE_01", "BLACK_HAT_POOL", "DARK_RELAY_42"}

    def update_statistics(self, amount: float):
        diff = amount - self.mean_amount
        self.mean_amount += self.alpha * diff
        self.var_amount = (1 - self.alpha) * (self.var_amount + self.alpha * (diff ** 2))

    def evaluate_transaction(self, tx: Dict[str, Any]) -> Tuple[bool, float, str]:
        sender = tx.get("sender", "")
        recipient = tx.get("recipient", "")
        amount = float(tx.get("amount", 0.0))

        if sender in self.sanctioned_entities or recipient in self.sanctioned_entities:
            return False, 1.0, "SANCTIONED_ENTITY_MATCH"

        std_dev = math.sqrt(max(self.var_amount, 1.0))
        z_score = abs(amount - self.mean_amount) / std_dev
        risk_score = 1.0 / (1.0 + math.exp(-0.5 * (z_score - 3.0)))

        if risk_score > self.risk_threshold:
            return False, risk_score, f"OUTLIER_ANOMALY_DETECTED_ZSCORE_{z_score:.2f}"

        self.update_statistics(amount)
        return True, risk_score, "APPROVED"
