# Runbook: Payments DB – CPU Saturation and Query Latency

## Service
payments-db (PostgreSQL cluster backing payments-service)

## Symptoms

- CPU utilization on primary DB node > 85–90% for > 10 minutes
- Increased query latency for `payments-service`
- Dynatrace / monitoring shows:
  - slow queries on `payments.transactions` table
  - connection pool saturation in `payments-service`

## Preconditions / When to Use

- Alert: "Payments DB CPU Saturation" or "Payments DB High Latency"
- Environment: production
- No ongoing maintenance window / known load test

---

## Diagnostic Steps

1. **Confirm DB health**
   - Check primary instance metrics:
     - CPU, memory
     - read/write IOPS
     - connections and connection errors.

2. **Identify slow queries**
   - Use DB performance views (pg_stat_statements or equivalent).
   - Sort by:
     - total time
     - mean time
     - calls in last 15 minutes.
   - Look for:
     - full table scans
     - missing indexes
     - sudden increase in calls from `payments-service`.

3. **Check connection pool usage**
   - From application side (`payments-service`):
     - max connections
     - active vs idle connections
     - any connection timeout / exhaustion errors.

4. **Correlate with traffic**
   - Check if overall request volume is higher than normal.
   - Identify any new batch jobs, backfills, or promotions (e.g. marketing campaigns).

---

## Triage Recommendation

- If **one or two specific queries** are responsible for the majority of CPU and latency:
  - Treat this as a *query-level optimization issue*.
  - Short-term mitigate via:
    - limiting concurrency
    - adding missing indexes (if safe and approved)
    - temporarily disabling expensive features.

- If **overall load has increased** (e.g. event or campaign):
  - Treat this as a *capacity issue*.
  - Short-term mitigate via:
    - horizontal scaling (read replicas if applicable)
    - tightening rate limits for non-critical operations.

---

## Remediation Steps (Query Hotspot)

1. **Throttle or pause non-critical jobs**
   - Identify any background jobs hitting `payments.transactions`.
   - Pause or throttle them if they are non-critical.

2. **Apply application-level mitigations**
   - Reduce concurrency limits in `payments-service` for heavy endpoints.
   - Introduce caching or batching if already supported by code.

3. **Index changes (if safe and pre-approved)**
   - If runbook or DBA playbook includes a specific index for the hotspot query:
     - create the index during off-peak if possible.
     - monitor CPU/latency while index is building.

4. **Monitor**
   - Check CPU and query latency for at least 15–30 minutes after changes.

---

## Remediation Steps (Capacity Issue)

1. **Scale DB (if allowed)**
   - Increase instance size or provision IOPS according to DBA guidelines.
   - Alternatively, add read replicas and redirect read-heavy traffic.

2. **Rate limit non-critical traffic**
   - Apply or tighten rate limits for:
     - reporting APIs
     - bulk exports
     - reconciliation jobs.

3. **Review long-term capacity**
   - Open follow-up ticket for capacity planning and index review.

---

## Rollback Plan

- If index change or DB scaling does not help or makes it worse:
  - Roll back to previous instance size or configuration.
  - Re-enable only the minimal necessary features.

- Keep a log of:
  - all DB-level changes
  - timestamps
  - observed metric changes.

---

## Safety Notes

- Do **not** run ad-hoc heavy queries on production during an ongoing incident.
- All schema/index changes must follow DBA / change-management policy.
- For P1 incidents, involve a DBA or platform engineer early.