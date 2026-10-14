from marketplace_alerts import BuyerUpdate, SellerAsset, handoff_order


class FakeSms:
    def __init__(self):
        self.calls = []

    def send(self, to, message, request_id):
        self.calls.append((to, message, request_id))
        return {"message_id": "msg-1"}


def test_handoff_notifies_buyer_with_stable_request_id():
    sms = FakeSms()
    result = handoff_order(
        SellerAsset("seller-42", "sku-8", "Hand-thrown mug"),
        BuyerUpdate("+15551234567", "order-1007", "handed_to_carrier"),
        sms,
    )
    assert result == {"message_id": "msg-1"}
    assert sms.calls == [
        ("+15551234567", "Order order-1007: Hand-thrown mug from seller seller-42 is on its way.", "order:order-1007:handoff")
    ]


def test_pending_order_does_not_text_buyer():
    sms = FakeSms()
    assert handoff_order(
        SellerAsset("seller-42", "sku-8", "Hand-thrown mug"),
        BuyerUpdate("+15551234567", "order-1007", "packed"),
        sms,
    ) is None
    assert sms.calls == []
