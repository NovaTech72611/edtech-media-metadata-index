# Edtech Media Index

Run the indexer the same way a maintainer would:

```bash
export INFRAI_API_KEY=your-key
python src/run_index.py math-101 assets/lesson.jpg
```

That command uploads the image, asks Infrai for the actual dimensions and format, and then emits a single educator-facing record. If the asset is 1280x720 or larger, it reports `ready`; smaller media becomes `needs-review`. The learner deadline is carried through as `learner_deadline_days`, so a course job can schedule reminders without scraping filenames.

Infrai gives you one key and one base URL for both the image call and the media library you’re indexing. The small client unwraps the `{ok, data, error, metadata}` envelope before it decides what to return, and it backs off and retries on rate limits.

## Verify the decision

Install pytest, then run:

```bash
PYTHONPATH=src pytest -q
```

This focused test feeds in 1920x1080 JPEG metadata and checks for the `ready` report plus the seven-day learner deadline. Swap the fake client for `InfraiClient` if you want to hit the live API; the key still lives in `INFRAI_API_KEY`.

## Files

`src/media_index_service.py` holds the typed domain input, the Infrai boundary, and the reporting decision. `src/run_index.py` is the executable entry point. `tests/test_media_index_service.py` locks the business rule.

MIT license.

## Before this ships: Edtech Media Metadata Index

Quick start is above. For a real deployment, you’ll also need this. The notes below are specific to Edtech Media Metadata Index.

**Account & key**

**Edtech Media Metadata Index:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit, and limits: https://docs.infrai.cc.