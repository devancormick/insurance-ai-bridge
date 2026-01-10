# Incident Response Runbook

## Overview

This runbook provides step-by-step procedures for responding to incidents in the Insurance AI Bridge system.

## Incident Classification

### Severity Levels

- **Critical (P1)**: System down, data loss, security breach
  - Response Time: Immediate
  - Resolution Time: < 1 hour

- **High (P2)**: Major functionality degraded, performance issues
  - Response Time: < 15 minutes
  - Resolution Time: < 4 hours

- **Medium (P3)**: Minor functionality issues, non-critical bugs
  - Response Time: < 1 hour
  - Resolution Time: < 24 hours

- **Low (P4)**: Cosmetic issues, minor enhancements
  - Response Time: < 4 hours
  - Resolution Time: Next release

## Incident Response Process

### 1. Detection and Triage

**Detection Sources:**
- Automated alerts (PagerDuty, Prometheus, CloudWatch)
- User reports
- Monitoring dashboards
- Health checks

**Initial Triage:**
1. Assess severity level
2. Determine affected components
3. Check status page for ongoing incidents
4. Identify potential root cause

### 2. Incident Response Team Activation

**On-Call Engineers:**
- Primary: [Contact Information]
- Secondary: [Contact Information]

**Escalation:**
- P1/P2: Immediate escalation to engineering manager
- P3/P4: Next business day escalation

### 3. Communication

**Internal Communication:**
- Slack/Teams: #incident-response channel
- Status Page: Update incident status
- Email: Notify stakeholders

**External Communication:**
- Status Page: Public updates
- Email: Customer notifications (for P1/P2)

### 4. Investigation and Resolution

**Investigation Steps:**
1. Check logs (Kibana, CloudWatch Logs)
2. Review metrics (Grafana, Prometheus)
3. Check recent deployments
4. Review error traces (Jaeger)
5. Check database performance
6. Review cache status

**Resolution Steps:**
1. Implement immediate mitigation
2. Apply permanent fix
3. Verify resolution
4. Monitor for recurrence

### 5. Post-Incident Review

**Post-Mortem Requirements:**
- Timeline of events
- Root cause analysis
- Impact assessment
- Action items and follow-ups
- Prevention measures

## Common Incident Scenarios

### Scenario 1: Database Connection Pool Exhaustion

**Symptoms:**
- Increased database connection errors
- Slow API responses
- Application timeouts

**Investigation:**
```bash
# Check database connections
kubectl exec -it postgres-pod -n insurance-ai-bridge -- psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pooler
kubectl exec -it pgbouncer-pod -n insurance-ai-bridge -- psql -h pgbouncer -p 6432 -c "SHOW POOLS;"
```

**Resolution:**
1. Scale up database connection pooler
2. Kill idle connections
3. Increase connection pool size
4. Investigate connection leaks

### Scenario 2: High API Latency

**Symptoms:**
- API response times > 1s
- User complaints
- Timeout errors

**Investigation:**
```bash
# Check application metrics
kubectl top pods -n insurance-ai-bridge

# Check database query performance
kubectl exec -it postgres-pod -n insurance-ai-bridge -- psql -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check cache hit rates
kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli INFO stats | grep keyspace_hits
```

**Resolution:**
1. Scale up backend instances
2. Optimize slow database queries
3. Warm up cache
4. Check for external service dependencies

### Scenario 3: Region Outage

**Symptoms:**
- Complete region unavailable
- Health checks failing
- User requests failing

**Investigation:**
```bash
# Check region health
curl https://api-us-east.insurance-ai-bridge.com/health
curl https://api-us-west.insurance-ai-bridge.com/health

# Check load balancer status
aws elbv2 describe-target-health --target-group-arn <arn>
```

**Resolution:**
1. Automatic failover to healthy region (if configured)
2. Manual DNS/load balancer routing to healthy region
3. Verify data replication to healthy region
4. Monitor failover completion

### Scenario 4: Security Breach

**Symptoms:**
- Unauthorized access detected
- Unusual authentication patterns
- Data exfiltration alerts

**Investigation:**
```bash
# Review authentication logs
kubectl logs -n insurance-ai-bridge deployment/backend | grep AUTH

# Check access logs
kubectl logs -n insurance-ai-bridge deployment/api-gateway | grep 401

# Review audit logs
aws s3 ls s3://audit-logs/insurance-ai-bridge/
```

**Resolution:**
1. **Immediate**: Isolate affected systems
2. Revoke compromised credentials
3. Rotate all secrets and keys
4. Review and update security policies
5. Notify security team and stakeholders
6. Conduct security audit

### Scenario 5: Data Corruption

**Symptoms:**
- Database integrity errors
- Inconsistent data
- Application errors related to data

**Investigation:**
```bash
# Check database integrity
kubectl exec -it postgres-pod -n insurance-ai-bridge -- psql -c "SELECT * FROM pg_stat_database_conflicts;"

# Review recent changes
kubectl exec -it postgres-pod -n insurance-ai-bridge -- psql -c "SELECT * FROM pg_stat_statements WHERE query LIKE '%UPDATE%' OR query LIKE '%DELETE%';"
```

**Resolution:**
1. Stop affected services
2. Restore from backup
3. Point-in-time recovery if needed
4. Verify data integrity
5. Resume services

## Recovery Procedures

### Database Restoration

```bash
# Full database restore
./scripts/restore_database.sh --backup-id <backup-id>

# Point-in-time recovery
./scripts/point_in_time_recovery.sh --target-time "2024-01-15 14:30:00"
```

### Service Rollback

```bash
# Rollback deployment
kubectl rollout undo deployment/backend -n insurance-ai-bridge

# Rollback to specific revision
kubectl rollout undo deployment/backend -n insurance-ai-bridge --to-revision=<revision>
```

### Cache Clear

```bash
# Clear Redis cache
kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli FLUSHALL

# Clear CDN cache
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

## Monitoring During Incidents

### Key Metrics to Monitor

- **Application**: Response time, error rate, throughput
- **Database**: Connection count, query latency, replication lag
- **Cache**: Hit rate, memory usage, evictions
- **Infrastructure**: CPU, memory, network usage
- **External**: Third-party API response times

### Dashboards

- **Grafana**: Application metrics dashboard
- **Kibana**: Log aggregation dashboard
- **Jaeger**: Distributed tracing dashboard
- **CloudWatch/Azure Monitor**: Infrastructure metrics

## Communication Templates

### Incident Announcement

```
[INCIDENT] P1: Database connection pool exhaustion

Status: Investigating
Impact: API latency increased, some requests timing out
Start Time: 2024-01-15 14:30:00 UTC
Affected: US-East-1 region
Updates: https://status.insurance-ai-bridge.com/incidents/123
```

### Resolution Update

```
[RESOLVED] P1: Database connection pool exhaustion

Status: Resolved
Resolution: Scaled up connection pooler and increased pool size
Duration: 45 minutes
Root Cause: Connection leak in background job processor
Prevention: Implemented connection pool monitoring and alerts
```

## Post-Incident Checklist

- [ ] Incident resolved and verified
- [ ] Post-mortem scheduled
- [ ] Root cause documented
- [ ] Action items created and assigned
- [ ] Monitoring alerts updated
- [ ] Documentation updated
- [ ] Stakeholders notified
- [ ] Status page updated

## Contact Information

### On-Call Engineers
- Primary: [Contact]
- Secondary: [Contact]

### Escalation Contacts
- Engineering Manager: [Contact]
- CTO: [Contact]

### Emergency Contacts
- Security Team: [Contact]
- Database Team: [Contact]
- Infrastructure Team: [Contact]


