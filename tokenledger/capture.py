"""Extract Messages API calls from a mitmproxy tracer capture (one JSON flow per line)."""

import json


def _is_messages_call(flow: dict) -> bool:
    path = flow.get("path", "").split("?")[0]
    body = flow.get("resp_body")
    return (flow.get("method") == "POST" and path == "/v1/messages"
            and isinstance(body, dict) and "usage" in body)


def load_calls(path) -> list[dict]:
    """[{"model": ..., "usage": ...}] for every Messages API call in the capture, in capture order."""
    calls = []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            flow = json.loads(line)
            if _is_messages_call(flow):
                body = flow["resp_body"]
                model = body.get("model") or (flow.get("req_body") or {}).get("model")
                calls.append({"model": model, "usage": body["usage"]})
    return calls
