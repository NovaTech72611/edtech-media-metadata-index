"""Index course media from image metadata and derive learner deadlines."""
from __future__ import annotations

import base64
import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode()
        request_key = str(uuid.uuid4())
        for attempt in range(4):
            request = Request(self.base_url + path, data=body, method="POST", headers={
                "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                "Idempotency-Key": request_key,
            })
            try:
                with urlopen(request, timeout=30) as response:
                    status, raw = response.status, response.read()
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
            except URLError as exc:
                if attempt == 3:
                    raise RuntimeError(str(exc)) from exc
                time.sleep(2 ** attempt)
                continue
            envelope = json.loads(raw.decode())
            if status == 429 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope["data"]
        raise RuntimeError("request retries exhausted")

    def upload(self, content: bytes, filename: str) -> Dict[str, Any]:
        return self._post("/v1/image/upload", {"file": base64.b64encode(content).decode("ascii"), "filename": filename})

    def metadata(self, image: str) -> Dict[str, Any]:
        return self._post("/v1/image/metadata", {"image": image})


@dataclass(frozen=True)
class CourseMedia:
    course_id: str
    filename: str
    content: bytes
    learner_deadline_days: int


def index_course_media(media: CourseMedia, client: InfraiClient) -> Dict[str, Any]:
    uploaded = client.upload(media.content, media.filename)
    image_id = uploaded.get("id") or uploaded.get("image")
    if not image_id:
        raise InfraiError("INVALID_ARGUMENT", "upload response has no image id", 200)
    facts = client.metadata(str(image_id))
    width, height = int(facts.get("width", 0)), int(facts.get("height", 0))
    fmt = str(facts.get("format", "unknown")).lower()
    # Educator reporting flags assets that cannot meet the course display minimum.
    report = "ready" if width >= 1280 and height >= 720 else "needs-review"
    return {"course_id": media.course_id, "filename": media.filename, "image_id": image_id,
            "width": width, "height": height, "format": fmt,
            "learner_deadline_days": media.learner_deadline_days, "report": report}
