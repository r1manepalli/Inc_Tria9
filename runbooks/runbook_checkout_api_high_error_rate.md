# Runbook: Checkout API – High Error Rate (HTTP 5xx)

## Service
checkout-api

## Symptoms

- Elevated HTTP 5xx error rate (> 2% over 5 minutes)
- Spikes in latency on /checkout and /place-order endpoints
- Dynatrace marks service as "Problem" with dependency to `payments-service`

## Preconditions / When to Use

- Dynatrace or alert manager fires an alert:
  - Name: "High 5xx on checkout-api"
  - Severity: P1 or P2
- Affected environment: production
- Error rate sustained longer than 3–5 minutes

---

## Diagnostic Steps

1. **Check Dynatrace problem card**
   - Confirm: affected service `checkout-api`, environment `prod`.
   - Note any correlated deployment events in the last 30 minutes.

2. **Check recent deployments**
   - Use CI/CD dashboard or deployment history.
   - If a deployment occurred in the last 30 minutes, capture:
     - version / build ID
     - commit hash
     - feature flags changed

3. **Inspect logs**
   - Filter application logs for `checkout-api` by:
     - `level >= ERROR`
     - Time window: last 15 minutes
   - Look for:
     - DB connection errors
     - timeouts to `payments-service`
     - configuration / secrets issues

4. **Check downstream dependencies**
   - Confirm `payments-service` and `inventory-service` health:
     - error rate
     - latency
     - CPU / memory saturation

5. **Check infrastructure**
   - Verify pod / task health:
     - any frequent restarts
     - OOMKilled events
   - Confirm autoscaling events in the same window.

---

## Triage Recommendation

- If **there was a recent deploy** to `checkout-api` and the error spike started immediately after it:
  - Treat this as a *deployment-related regression*.
  - Prefer rollback over ad-hoc hotfix in production.

- If **downstream services are unhealthy** (`payments-service`, `inventory-service`):
  - Treat `checkout-api` as a *symptom*, not the root cause.
  - Escalate to ownership team of the failing downstream service.

---

## Remediation Steps (Deployment Regression)

1. **Freeze further changes**
   - Pause new production deployments to `checkout-api` until stabilized.

2. **Roll back the last deployment**
   - Use standard pipeline to redeploy the previous known-good version.
   - Confirm:
     - deployment succeeded
     - pods are healthy and passing readiness probes.

3. **Verify**
   - Monitor:
     - 5xx error rate on `checkout-api`
     - latency on /checkout and /place-order
   - Time window: at least 10–15 minutes post-rollback.

4. **Communicate**
   - Post in incident channel:
     - cause: suspected bad release
     - action: rollback performed
     - current status.

---

## Remediation Steps (Downstream Failure)

1. **Escalate**
   - Identify failing downstream service from Dynatrace topology (e.g. `payments-service`).
   - Notify that service’s on-call SRE / owning squad.

2. **Apply temporary mitigations (if documented)**
   - Enable feature flags for:
     - reduced external calls
     - graceful degradation (e.g. disable non-essential payment methods).
   - Reduce concurrency or rate limit from `checkout-api` if needed.

3. **Monitor**
   - Continue watching error rate and latency on both `checkout-api` and downstream service.

---

## Rollback Plan

- If rollback resolves the issue:
  - Mark current prod version as *bad* in release notes.
  - Open a follow-up ticket to:
    - root-cause the regression
    - add tests or safeguards.

- If rollback does **not** resolve the issue:
  - Re-deploy previous version only if clearly safe.
  - Escalate to senior SRE / principal for deeper investigation.

---

## Safety Notes

- Do **not** apply manual config changes directly in production unless:
  - they are documented in an approved runbook, or
  - a senior SRE has explicitly approved them.
- Always verify error rate and latency for at least 10 minutes after rollback before closing the incident.
- For P1 incidents, ensure comms to incident channel and relevant leadership are active.