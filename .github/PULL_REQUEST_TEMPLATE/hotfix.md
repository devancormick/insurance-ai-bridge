# Hotfix: <!-- Critical Issue Title -->

## Description

<!-- Provide a clear and concise description of the critical issue being fixed -->

## Related Issue

Fixes #<!-- issue number -->
Closes #<!-- issue number -->

## Type of Change

- [x] Hotfix (critical fix for production)

## Urgency

**Severity Level:** <!-- Critical / High / Medium -->

**Impact:**
<!-- Describe the impact on production -->

- Affected users:
- Affected functionality:
- Business impact:

## Problem

<!-- Describe the critical issue in detail -->

### Symptoms
- 
- 

### Root Cause
<!-- Explain what caused the critical issue -->

## Solution

<!-- Describe the fix and why it resolves the issue -->

### Changes Made
- 
- 

### Files Modified
- 
- 

## Testing

### Test Coverage
- [ ] Critical path tests added/updated
- [ ] Regression tests run
- [ ] Manual testing in staging (if applicable)
- [ ] Smoke tests completed

### Test Scenarios

1. **Critical Path Verification:**
   - Steps:
   - Expected result:
   - Actual result:

2. **Regression Testing:**
   - Features tested:
   - Results:

### Test Results
```bash
# Critical tests
# [Add test commands and results]

# Regression tests
pytest tests/ -v
# Results: X passed, Y failed
```

## Deployment Plan

### Pre-Deployment
- [ ] Code reviewed and approved
- [ ] Tests passing
- [ ] Rollback plan prepared
- [ ] Deployment window scheduled (if applicable)
- [ ] Stakeholders notified

### Deployment Steps
1. 
2. 
3. 

### Post-Deployment
- [ ] Smoke tests executed
- [ ] Monitoring active
- [ ] Rollback plan ready
- [ ] Team on standby

### Rollback Plan
<!-- Describe how to rollback if issues occur -->
1. 
2. 
3. 

## Monitoring

<!-- What should be monitored after deployment -->

- Metrics to watch:
- Alerts to check:
- Duration to monitor:

## Checklist

- [ ] Critical issue verified and understood
- [ ] Fix is minimal and focused
- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented explaining the critical fix
- [ ] All critical tests passing
- [ ] Regression tests run
- [ ] Rollback plan prepared
- [ ] Deployment plan documented
- [ ] Stakeholders notified
- [ ] No merge conflicts
- [ ] PR description is clear and complete

## Breaking Changes

- [ ] This hotfix introduces breaking changes
- [ ] Breaking changes are documented (if applicable)
- [ ] Mitigation plan for breaking changes (if applicable)

## Follow-Up Tasks

<!-- Tasks to be completed after hotfix is deployed -->

- [ ] Create follow-up issue for proper fix (if this is a temporary fix)
- [ ] Update documentation
- [ ] Add comprehensive tests
- [ ] Post-mortem scheduled (if applicable)
- [ ] Root cause analysis (if needed)

## Additional Context

<!-- Add any other context, timeline, or critical information about the hotfix -->

## Approval

<!-- Hotfixes may require emergency approval -->

- [ ] Emergency approval obtained
- [ ] Approvers notified
- [ ] Deployment window confirmed

