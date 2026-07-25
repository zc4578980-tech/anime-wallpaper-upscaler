# v0.2.0 First-Month Star Goal

**Status: Ready to measure after release**

The public success target is at least 30 net new GitHub Stars in the first 30 calendar days
after the v0.2.0 Release. This is a post-release outcome target, not a claim that Stars can be
guaranteed and not a pre-release traffic gate.

```text
net new Stars = Stars at the 30-day checkpoint - Stars at the release-day baseline
```

The target is met when net new Stars are at least 30. Organic community interest is required;
paid, artificial, or undisclosed Star acquisition is not acceptable evidence for an internship
portfolio or project report.

## Pre-Release Readiness

The release candidate is technically verified and is available in Draft PR #1. A public release
can be authorized on technical and review evidence without inventing pre-launch visits. It still
requires an explicit release decision; this document does not authorize a tag, GitHub Release,
or announcement by itself.

There is no reliable pre-release forecast in the checked-in data. The former 1,000-visit and
three-channel forecast was removed because it required the very public launch activity it
prohibited, making formal release impossible to reach honestly.

## Measurement Contract

Before publishing v0.2.0, update `docs/release/launch-plan.json` from `planned` to `released`
and record:

- `release.date`: the ISO release date;
- `release.baselineStars`: the public GitHub Star count immediately before release; and
- `release.baselineEvidence`: a URL or repository path showing that baseline.

Record the public GitHub repository metrics on days 0, 1, 3, 7, 14, and 30 in
`docs/release/measurement.csv`. Preserve a timestamped URL or screenshot path for every
checkpoint. At the 30-day checkpoint, evaluate the goal with:

```powershell
python scripts/validate_launch_readiness.py docs/release/launch-plan.json `
  --as-of YYYY-MM-DD `
  --current-stars NUMBER
```

Before day 30 the validator reports progress and does not treat a missing current Star count as
a failure. On or after day 30 it reports whether the measured net-new Star target is met.

## Evidence Standards

Use actual public repository data and attributable placement records. Keep source URLs, dates,
referrers when available, and a concise note about what was posted. Do not count paid traffic,
artificial engagement, unsupported estimates, or duplicated traffic as proof of organic demand.

The target supports an internship portfolio only when its evidence is reproducible: reviewers
should be able to see the repository, the release baseline, the 30-day checkpoint, and the
project work that produced the result.
