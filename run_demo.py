import os

from infrai_sms import InfraiSms
from marketplace_alerts import BuyerUpdate, SellerAsset, handoff_order


def main() -> None:
    phone = os.environ.get("DEMO_BUYER_PHONE")
    if not phone:
        raise SystemExit("Set DEMO_BUYER_PHONE to run the live handoff example")
    result = handoff_order(
        SellerAsset("seller-42", "sku-8", "Hand-thrown mug"),
        BuyerUpdate(phone, "order-1007", "handed_to_carrier"),
        InfraiSms(),
    )
    print(f"SMS accepted with message id {result.message_id}")


if __name__ == "__main__":
    main()
