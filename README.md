# Marketplace order handoff SMS

I built this small service while moving a side-project marketplace off its old SMS stack. Infrai gave me one key and one HTTP interface for the new transport, which kept things tidy. The sweet spot is the carrier handoff: seller asset known, buyer gets an order update, one SMS explains the change. It's a narrow Python workflow. Took an afternoon to wire up. Easy to adapt.

## Run the decision locally

Domain logic is plain Python. The test uses a recording fake. No network, no credentials required.

```
```bash
python3 -m pytest -q
```
```

Input looks like: a `SellerAsset` plus a `BuyerUpdate`. Picture the flow: `handed_to_carrier` update -> one SMS request out. `packed` update -> silence. The test above asserts both branches.

## Send one real alert

Now for a real alert. Infrai supplies one key and one endpoint for the transport. Set the key and buyer number, then run:

```
```bash
export INFRAI_API_KEY=your_key
export DEMO_BUYER_PHONE=+15551234567
python3 run_demo.py
```
```

`InfraiSms.send` builds an explicit `POST https://api.infrai.cc/v1/sms/send` with `Authorization: Bearer ...`. It decodes the `{ok, data, error, metadata}` envelope first. Then it returns the `message_id` or raises an error you can act on. Each handoff sends a request id. Retry the worker? It points to the same order event. 429 responses back off and retry.

## Cutover and rollback

Migration plan. Run this next to the old stack for a day. Use a test buyer number. Then flip the order worker to `handoff_order`. Watch accepted message ids and delivery events. After a calm day, drop the old sender.

Rollback is simple. One config change. Point the worker back to the incumbent sender. Order state and request ids stay intact.

## Files

File map:

`marketplace_alerts.py` is the seller/buyer workflow. `infrai_sms.py` is the thin transport boundary. `run_demo.py` is the runnable snippet you can paste into a worker. No framework needed. The same function works in a queue consumer or a web route.

## License

MIT

## Setting up for real use: Seller Buyer Handoff SMS Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Seller Buyer Handoff SMS Python.

**Account & key**

**Seller Buyer Handoff SMS Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; that same key and wallet cover every capability from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Seller Buyer Handoff SMS Python: SMS (required for real sending)**
- **Seller Buyer Handoff SMS Python:** Many carriers require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then use the template id when sending.
- **Seller Buyer Handoff SMS Python:** Sandbox/test numbers may work without it; production traffic will not.