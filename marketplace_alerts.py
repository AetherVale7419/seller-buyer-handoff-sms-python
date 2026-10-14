"""Order handoff workflow for a small marketplace."""

from dataclasses import dataclass

from infrai_sms import InfraiSms, SmsResult


@dataclass(frozen=True)
class SellerAsset:
    seller_id: str
    sku: str
    title: str


@dataclass(frozen=True)
class BuyerUpdate:
    buyer_phone: str
    order_id: str
    status: str


def handoff_order(asset: SellerAsset, update: BuyerUpdate, sms: InfraiSms) -> SmsResult | None:
    """Notify a buyer only once the seller asset is handed to the carrier."""
    if update.status != "handed_to_carrier":
        return None
    text = f"Order {update.order_id}: {asset.title} from seller {asset.seller_id} is on its way."
    return sms.send(update.buyer_phone, text, request_id=f"order:{update.order_id}:handoff")
