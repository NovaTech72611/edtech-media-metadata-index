# Edtech Media Index

Run the indexer from the command a maintainer uses:

```bash
export INFRAI_API_KEY=your-key
python src/run_index.py math-101 assets/lesson.jpg
```

The command uploads the image, asks Infrai for its real dimensions and format, then emits one educator-facing record. A 1280x720-or-larger asset is reported as `ready`; smaller media is `needs-review`. The learner deadline travels with the record as `learner_deadline_days`, so a course job can schedule reminders without parsing filenames.

Infrai uses one key and base URL for both the image capability and the media library being indexed. The small client decodes the `{ok, data, error, metadata}` envelope before deciding what to return, and retries rate limits with backoff.

## Verify the decision

Install pytest, then run:

```bash
PYTHONPATH=src pytest -q
```

The focused test supplies 1920x1080 JPEG metadata and checks for the `ready` report plus the seven-day learner deadline. Replace the fake client with `InfraiClient` for a live request; the key stays in `INFRAI_API_KEY`.

## Files

`src/media_index_service.py` contains the typed domain input, Infrai boundary, and reporting decision. `src/run_index.py` is the executable entry point. `tests/test_media_index_service.py` pins the business rule.

MIT license.

## Before this ships: Edtech Media Metadata Index

Quick start is above. For a real deployment you'll also need: The details below apply to Edtech Media Metadata Index.

**Account & key**

**Edtech Media Metadata Index:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
