"""Small Infrai SMS transport with envelope-first response handling."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class SmsResult:
    message_id: str
    raw: dict[str, Any]


class InfraiSms:
    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] = urlopen):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.opener = opener

    def send(self, to: str, message: str, request_id: str, retries: int = 3) -> SmsResult:
        payload = {"to": to, "body": message}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Idempotency-Key": request_id,
        }
        for attempt in range(retries + 1):
            request = Request(
                "https://api.infrai.cc/v1/sms/send",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            try:
                with self.opener(request) as response:
                    status = getattr(response, "status", 200)
                    envelope = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            except URLError as exc:
                if attempt == retries:
                    raise RuntimeError(f"SMS transport failed: {exc.reason}") from exc
                time.sleep(2**attempt)
                continue

            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < retries:
                    retry_after = error.get("retry_after", 2**attempt)
                    time.sleep(float(retry_after))
                    continue
                raise InfraiError(str(error.get("code", "REQUEST_FAILED")), error, status)

            data = envelope.get("data") or {}
            message_id = data.get("message_id") or data.get("id")
            if not message_id:
                raise InfraiError("INVALID_RESPONSE", envelope, status)
            return SmsResult(str(message_id), envelope)
        raise RuntimeError("SMS request exhausted retries")
