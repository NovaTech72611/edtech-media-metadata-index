import json
import sys

from media_index_service import CourseMedia, InfraiClient, index_course_media


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python src/run_index.py COURSE_ID IMAGE_PATH")
    course_id, path = sys.argv[1:]
    with open(path, "rb") as stream:
        media = CourseMedia(course_id, path.rsplit("/", 1)[-1], stream.read(), 7)
    print(json.dumps(index_course_media(media, InfraiClient()), indent=2))


if __name__ == "__main__":
    main()
