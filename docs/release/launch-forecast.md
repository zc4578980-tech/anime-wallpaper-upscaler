# v0.2.0 Launch Forecast

**Status: Blocked pending evidence**

The release gate uses a deliberately conservative ceiling of 3%:

```text
forecast Stars = floor(included qualified visits * conversionRate)
```

The launch plan must show at least 1,000 qualified visits, at least three independent
channels, and at least 30 forecast Stars. `conversionRate` must be greater than zero and
cannot exceed `0.03`.

Only a source that is confirmed, unpaid, non-artificial, and unrelated to Bilibili
recommendation traffic may count. Every included source must have a non-empty evidence URL
or repository path. Unconfirmed placements, paid traffic, artificial Stars, Bilibili
recommendation traffic, and unsupported estimates are excluded from both visits and channel
counts.

Run the gate from the repository root:

```powershell
python scripts/validate_launch_readiness.py docs/release/launch-plan.json
```

The checked-in plan is intentionally empty and blocking. Change this status only after real
evidence has been added to `launch-plan.json` and the exact command above exits successfully.
