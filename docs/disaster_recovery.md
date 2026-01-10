# Disaster Recovery Plan

## Overview

This document outlines the disaster recovery (DR) procedures for the Insurance AI Bridge system. The DR plan ensures business continuity with minimal data loss and downtime.

## Objectives

- **Recovery Point Objective (RPO)**: < 15 minutes (point-in-time recovery)
- **Recovery Time Objective (RTO)**: < 1 hour for critical services
- **Availability Target**: 99.95% uptime (4.38 hours/month downtime)

## Backup Strategy

### Database Backups

#### Hourly Backups (Hot Data)
- **Frequency**: Every hour
- **Retention**: 24 hours
- **Storage**: Cloud storage (S3/Blob) - Standard tier
- **Backup Type**: Incremental snapshots

#### Daily Backups (All Data)
- **Frequency**: Daily at 2:00 AM UTC
- **Retention**: 30 days
- **Storage**: Cloud storage (S3/Blob) - Standard-IA tier
- **Backup Type**: Full database dump

#### Weekly Backups (Archival)
- **Frequency**: Weekly on Sunday
- **Retention**: 52 weeks (1 year)
- **Storage**: Cloud storage (S3/Blob) - Glacier tier
- **Backup Type**: Full database dump

#### Long-Term Backups (Compliance)
- **Frequency**: Monthly
- **Retention**: 84 months (7 years for HIPAA compliance)
- **Storage**: Cloud storage (S3/Blob) - Glacier Deep Archive
- **Backup Type**: Full database dump + encrypted archives

### Continuous WAL Archiving

- **Purpose**: Point-in-time recovery (PITR)
- **Frequency**: Continuous (real-time)
- **Retention**: 7 days of WAL files
- **Storage**: Cloud storage (S3/Blob)
- **Recovery Granularity**: 15-minute intervals

### Backup Verification

- Automated backup verification after each backup
- Monthly restore testing to verify backup integrity
- Automated alerts for backup failures

## Disaster Scenarios

### Scenario 1: Regional Outage

**Impact**: Complete loss of one region (e.g., US-East)

**Recovery Procedure**:
1. Traffic Manager/Global Load Balancer automatically routes to healthy regions
2. Read replicas in other regions become primary
3. RTO: < 5 minutes (automatic failover)
4. RPO: < 1 minute (asynchronous replication)

**Manual Steps** (if automatic failover fails):
```bash
# Promote read replica to primary
./scripts/promote_replica.sh us-west-2

# Update DNS/load balancer configuration
./scripts/update_routing.sh us-west-2

# Verify data consistency
./scripts/verify_replication.sh
```

### Scenario 2: Database Corruption

**Impact**: Database corruption detected

**Recovery Procedure**:
1. Immediate: Isolate affected database instance
2. Promote read replica to primary
3. Restore from most recent backup if needed
4. RTO: < 30 minutes
5. RPO: < 15 minutes (point-in-time recovery)

**Restore Procedure**:
```bash
# Stop application services
kubectl scale deployment backend --replicas=0

# Restore from backup
./scripts/restore_database.sh --backup-id <backup-id>

# Or point-in-time recovery
./scripts/point_in_time_recovery.sh --target-time "2024-01-15 14:30:00"

# Verify data integrity
./scripts/verify_database.sh

# Restart services
kubectl scale deployment backend --replicas=10
```

### Scenario 3: Complete Data Center Loss

**Impact**: Loss of entire data center (cloud or on-premise)

**Recovery Procedure**:
1. Activate disaster recovery site
2. Restore from off-site backups
3. Rebuild infrastructure using Infrastructure as Code
4. Restore databases from backups
5. Update DNS and routing
6. RTO: < 4 hours
7. RPO: < 15 minutes

### Scenario 4: Ransomware/Cyber Attack

**Impact**: System compromised, data encrypted

**Recovery Procedure**:
1. Immediate: Isolate affected systems
2. Notify security team and incident response
3. Assess scope of compromise
4. Restore from known-good backups
5. Rebuild compromised systems
6. Review and update security measures
7. RTO: < 8 hours
8. RPO: < 15 minutes (restore from pre-attack backup)

## Recovery Procedures

### Database Restoration

#### Full Database Restore
```bash
# Restore from full backup
./scripts/restore_database.sh \
  --backup-s3 s3://insurance-ai-bridge-backups/daily/backup-20240115.sql.gz \
  --target-db postgres-primary
```

#### Point-in-Time Recovery
```bash
# Restore to specific point in time
./scripts/point_in_time_recovery.sh \
  --target-time "2024-01-15 14:30:00" \
  --wal-archive s3://insurance-ai-bridge-backups/wal-archive
```

#### Single Table Restore
```bash
# Restore specific table
./scripts/restore_table.sh \
  --table claims \
  --backup-id backup-20240115 \
  --target-db postgres-primary
```

### Infrastructure Restoration

#### Cloud Infrastructure
```bash
# Restore infrastructure using Terraform
cd infrastructure/cloud/terraform/aws
terraform init
terraform plan -out=restore.tfplan
terraform apply restore.tfplan
```

#### Kubernetes Resources
```bash
# Restore Kubernetes resources
kubectl apply -f infrastructure/k8s/ -R

# Restore ConfigMaps and Secrets
kubectl apply -f infrastructure/k8s/secrets/
kubectl apply -f infrastructure/k8s/configmaps/
```

### Application Restoration

```bash
# Deploy application from CI/CD pipeline
./scripts/deploy.sh --environment production --region us-east-1

# Verify application health
./scripts/health_check.sh

# Monitor for issues
kubectl logs -f deployment/backend
```

## Testing Procedures

### Monthly DR Testing

1. **Backup Verification**
   - Verify all backups are accessible
   - Test restore from each backup tier
   - Validate backup integrity

2. **Failover Testing**
   - Simulate regional outage
   - Test automatic failover
   - Verify data consistency after failover

3. **Restore Testing**
   - Restore database in test environment
   - Verify data integrity
   - Test application functionality

4. **Communication Testing**
   - Test incident notification procedures
   - Verify escalation paths
   - Test stakeholder communication

### Quarterly DR Drills

Full disaster recovery simulation including:
- Complete infrastructure rebuild
- Database restoration from backups
- Application deployment
- End-to-end functionality testing
- Documentation of lessons learned

## Monitoring and Alerts

### Backup Monitoring

- Backup completion status (automated alerts on failure)
- Backup storage usage and retention
- Backup verification results

### Disaster Detection

- Regional health checks (automated)
- Database replication lag monitoring
- Infrastructure health monitoring
- Security incident detection

### Alert Escalation

1. **Level 1**: Automated system responses (auto-failover, auto-scaling)
2. **Level 2**: On-call engineer notification (< 5 minutes)
3. **Level 3**: Incident response team activation (< 15 minutes)
4. **Level 4**: Executive notification (< 30 minutes)

## Recovery Checklist

### Immediate Response (< 15 minutes)

- [ ] Assess situation and impact
- [ ] Activate incident response team
- [ ] Notify stakeholders
- [ ] Document incident details

### Short-term Recovery (< 1 hour)

- [ ] Execute failover procedures if applicable
- [ ] Restore critical services
- [ ] Verify data integrity
- [ ] Monitor system health

### Long-term Recovery (< 4 hours)

- [ ] Complete infrastructure restoration
- [ ] Full application deployment
- [ ] Data validation and verification
- [ ] Post-incident review preparation

### Post-Recovery (< 24 hours)

- [ ] Complete post-incident review
- [ ] Document lessons learned
- [ ] Update DR procedures
- [ ] Update monitoring and alerting
- [ ] Communicate recovery status to stakeholders

## Contact Information

### On-Call Engineers
- Primary: [Contact Information]
- Secondary: [Contact Information]

### Incident Response Team
- Lead: [Contact Information]
- Security: [Contact Information]
- Database: [Contact Information]
- Infrastructure: [Contact Information]

### Escalation Contacts
- CTO: [Contact Information]
- CEO: [Contact Information]

## Appendix

### Backup Locations

- **Primary**: AWS S3 (us-east-1)
- **Secondary**: AWS S3 (us-west-2)
- **Tertiary**: Azure Blob Storage (westeurope)

### DR Site Locations

- **Primary DR Site**: us-west-2
- **Secondary DR Site**: eu-west-1
- **On-Premise DR Site**: [Location]

### Recovery Scripts

All recovery scripts are located in `scripts/dr/`:
- `restore_database.sh` - Database restoration
- `point_in_time_recovery.sh` - PITR procedures
- `failover.sh` - Automated failover
- `verify_replication.sh` - Replication verification
- `test_dr.sh` - DR testing automation

