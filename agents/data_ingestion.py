from dataclasses import dataclass
from typing import Dict

@dataclass
class IngestionResult:
    ok: bool
    reason: str = ""

class DataIngestionAgent:
    """Validates user/donation/request address for Belagavi District."""

    def __init__(self):
        # ✅ Allowed taluks inside Belagavi District
        self.allowed_taluks = {
            "belagavi",
            "gokak",
            "khanapur",
            "ramdurg",
            "saundatti",
            "bailhongal",
            "athani",
            "chikkodi",
            "raibag",
            "hukkeri",
        }

    def validate_user_address(self, address: Dict) -> IngestionResult:
        # Expected keys: district, taluk, pincode
        district = (address.get("district") or "").strip().lower()
        taluk = (address.get("taluk") or "").strip().lower()
        pincode = (address.get("pincode") or "").strip()

        # ✅ District must be Belagavi
        if district != "belagavi":
            return IngestionResult(False, "Only Belagavi district is supported.")

        # ✅ Taluk must be one of the valid Belagavi taluks
        if taluk not in self.allowed_taluks:
            return IngestionResult(False, "Only taluks within Belagavi district are allowed.")

        # ✅ Belagavi pincodes start with 59
        if not pincode.startswith("59"):
            return IngestionResult(False, "Enter a valid Belagavi pincode (starts with 59).")

        return IngestionResult(True, "ok")
