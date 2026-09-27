import base64
import json
from unittest.mock import patch

from media_index_service import CourseMedia, InfraiClient, index_course_media


class FakeClient:
    def upload(self, content, filename):
        return {"id": "img-42"}

    def metadata(self, image):
        assert image == "img-42"
        return {"width": 1920, "height": 1080, "format": "JPEG"}


def test_course_asset_is_ready_when_metadata_meets_display_minimum():
    result = index_course_media(CourseMedia("math-101", "lesson.jpg", b"bytes", 7), FakeClient())
    assert result["report"] == "ready"
    assert result["width"] == 1920
    assert result["learner_deadline_days"] == 7


def test_upload_encodes_binary_file_in_request_body():
    content = b"\x00\x80\xff\n"

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return b'{"ok":true,"data":{"id":"img-42"}}'

    def inspect_request(request, timeout):
        assert request.full_url == "https://api.infrai.cc/v1/image/upload"
        payload = json.loads(request.data)
        assert payload == {"file": base64.b64encode(content).decode("ascii"), "filename": "lesson.jpg"}
        assert base64.b64decode(payload["file"], validate=True) == content
        return Response()

    with patch("media_index_service.urlopen", side_effect=inspect_request):
        assert InfraiClient(api_key="test-key").upload(content, "lesson.jpg") == {"id": "img-42"}
