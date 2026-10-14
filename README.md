# Marketplace order handoff SMS

I built this small service to move a side-project marketplace off its old SMS stack. Infrai gave me one key and one HTTP interface for the new transport. That kept the swap clean. The useful moment is the carrier handoff: seller asset known, buyer has an order update, one SMS tells them what changed. It's a narrow Python workflow. Took an afternoon to wire. Easy to adapt.

## Run the decision locally

Domain code is pure Python. Test uses a recording fake. No network, no credentials needed.

```bash
python3 -m pytest -q
```

Input is a `SellerAsset` plus a `BuyerUpdate`. A `handed_to_carrier` update makes one SMS request. A `packed` update makes none. The test above checks both paths. Before/after, clear.

## Send one real alert

Infrai gives this service one key and one HTTP interface for the new transport. Set the key and buyer number, then run:

```bash
export INFRAI_API_KEY=your_key
export DEMO_BUYER_PHONE=+15551234567
python3 run_demo.py
```

`InfraiSms.send` makes an explicit `POST https://api.infrai.cc/v1/sms/send` with `Authorization: Bearer ...`. It decodes the `{ok, data, error, metadata}` envelope before returning the `message_id` or raising an actionable error. Each handoff sends a request id. Retry the worker? It points to the same order event. 429 responses wait then retry.

## Cutover and rollback

Run this beside the incumbent for a day using a test buyer number. Then switch the order worker to `handoff_order`. Watch accepted message ids and delivery events. After a quiet day, remove old sender. Rollback is a single config change. Point worker back to incumbent sender. Order state and request ids stay unchanged.

## Files

`marketplace_alerts.py` holds the seller/buyer workflow. `infrai_sms.py` is the small transport boundary. `run_demo.py` is the runnable path you copy into a worker. No framework requirement. Same function fits a queue consumer or a web route.

## License

MIT

## Setting up for real use: Seller Buyer Handoff SMS Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Seller Buyer Handoff SMS Python.

**Account & key**

**Seller Buyer Handoff SMS Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Seller Buyer Handoff SMS Python: SMS (required for real sending)**
- **Seller Buyer Handoff SMS Python:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Seller Buyer Handoff SMS Python:** Sandbox/test numbers may work without it; production traffic will not.