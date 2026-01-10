# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: High Database Connection Errors

**Symptoms:**
- `psycopg2.OperationalError: FATAL: remaining connection slots are reserved`
- `too many clients already`
- Application timeouts

**Causes:**
- Connection pool exhausted
- Connection leaks
- Insufficient connection pool size

**Solutions:**
1. **Check current connections:**
   ```bash
   kubectl exec -it postgres-pod -n insurance-ai-bridge -- psql -c "SELECT count(*) FROM pg_stat_activity;"
   ```

2. **Kill idle connections:**
   ```sql
   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '10 minutes';
   ```

3. **Scale up connection pooler:**
   ```bash
   kubectl scale deployment/pgbouncer -n insurance-ai-bridge --replicas=3
   ```

4. **Increase connection pool size:**
   - Update PgBouncer configuration
   - Increase `max_client_conn` and `default_pool_size`

5. **Fix connection leaks:**
   - Review application code for unclosed connections
   - Use connection context managers
   - Implement connection pool monitoring

### Issue 2: Slow API Responses

**Symptoms:**
- API response times > 1s
- User complaints about slow performance
- Timeout errors

**Causes:**
- Slow database queries
- High cache miss rate
- External service dependencies
- Resource constraints

**Solutions:**
1. **Check slow queries:**
   ```sql
   SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
   ```

2. **Optimize queries:**
   - Add missing indexes
   - Rewrite inefficient queries
   - Use query result caching

3. **Check cache hit rate:**
   ```bash
   kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli INFO stats | grep keyspace_hits
   ```

4. **Warm up cache:**
   ```bash
   ./scripts/warm_cache.sh
   ```

5. **Scale up resources:**
   ```bash
   kubectl scale deployment/backend -n insurance-ai-bridge --replicas=20
   ```

6. **Check external dependencies:**
   - Verify third-party API response times
   - Implement circuit breakers
   - Add request timeouts

### Issue 3: High Memory Usage

**Symptoms:**
- OOM (Out of Memory) errors
- Pod restarts
- High memory utilization in Grafana

**Causes:**
- Memory leaks
- Inefficient data processing
- Insufficient memory limits

**Solutions:**
1. **Check memory usage:**
   ```bash
   kubectl top pods -n insurance-ai-bridge
   ```

2. **Review memory limits:**
   ```bash
   kubectl describe pod <pod-name> -n insurance-ai-bridge | grep -A 5 "Limits:"
   ```

3. **Increase memory limits:**
   ```yaml
   resources:
     limits:
       memory: "4Gi"  # Increase from 2Gi
   ```

4. **Fix memory leaks:**
   - Review application code
   - Use memory profilers (memory_profiler, py-spy)
   - Implement garbage collection tuning

5. **Optimize data processing:**
   - Process data in batches
   - Use streaming instead of loading all data
   - Clear unused variables and objects

### Issue 4: Cache Invalidation Issues

**Symptoms:**
- Stale data being served
- Inconsistent cache state
- High cache miss rate after updates

**Causes:**
- Missing cache invalidation
- Incorrect dependency tracking
- Cache key collisions

**Solutions:**
1. **Manual cache invalidation:**
   ```bash
   kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli DEL <cache-key>
   ```

2. **Invalidate related keys:**
   ```bash
   kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli --scan --pattern "prefix:*" | xargs redis-cli DEL
   ```

3. **Review cache invalidation logic:**
   - Check dependency tracking
   - Verify cascade invalidation
   - Review cache key generation

4. **Update cache strategy:**
   - Use versioned cache keys
   - Implement cache tagging
   - Add cache expiration policies

### Issue 5: Authentication/Authorization Failures

**Symptoms:**
- 401 Unauthorized errors
- 403 Forbidden errors
- SSO login failures

**Causes:**
- Expired tokens
- Incorrect credentials
- Permission misconfigurations
- SSO provider issues

**Solutions:**
1. **Check authentication logs:**
   ```bash
   kubectl logs -n insurance-ai-bridge deployment/backend | grep AUTH
   ```

2. **Verify token validity:**
   - Check token expiration
   - Validate token signature
   - Verify issuer and audience

3. **Check user permissions:**
   ```sql
   SELECT * FROM user_roles WHERE user_id = '<user-id>';
   SELECT * FROM role_permissions WHERE role_id = '<role-id>';
   ```

4. **Verify SSO configuration:**
   - Check SAML/OAuth2 provider settings
   - Verify certificate validity
   - Test SSO flow manually

5. **Reset user credentials:**
   - Reset password
   - Regenerate tokens
   - Reassign roles if needed

### Issue 6: Database Replication Lag

**Symptoms:**
- Read replicas returning stale data
- Replication lag warnings
- Inconsistent data across regions

**Causes:**
- High write load
- Network issues
- Replica processing delays

**Solutions:**
1. **Check replication lag:**
   ```sql
   SELECT NOW() - pg_last_xact_replay_timestamp() AS replication_lag;
   ```

2. **Monitor replication status:**
   ```sql
   SELECT * FROM pg_stat_replication;
   ```

3. **Optimize write operations:**
   - Batch writes
   - Optimize slow queries
   - Reduce write frequency

4. **Scale up replicas:**
   ```bash
   # Add more read replicas
   kubectl scale statefulset/postgres-replica -n insurance-ai-bridge --replicas=5
   ```

5. **Check network connectivity:**
   ```bash
   kubectl exec -it postgres-primary -n insurance-ai-bridge -- ping postgres-replica
   ```

### Issue 7: Task Queue Backlog

**Symptoms:**
- Tasks not processing
- Growing queue size
- Task timeouts

**Causes:**
- Worker capacity insufficient
- Slow task processing
- Worker failures

**Solutions:**
1. **Check queue size:**
   ```bash
   # For Celery
   celery -A app inspect active
   celery -A app inspect reserved
   
   # For RQ
   rq info
   ```

2. **Scale up workers:**
   ```bash
   kubectl scale deployment/worker -n insurance-ai-bridge --replicas=10
   ```

3. **Review task processing:**
   - Check for slow tasks
   - Optimize task code
   - Add task prioritization

4. **Check worker health:**
   ```bash
   kubectl logs -n insurance-ai-bridge deployment/worker | grep ERROR
   ```

5. **Clear dead letter queue:**
   - Review failed tasks
   - Fix task errors
   - Retry or discard failed tasks

### Issue 8: CDN Cache Issues

**Symptoms:**
- Stale content being served
- Missing static assets
- High origin requests

**Causes:**
- Incorrect cache headers
- Missing cache invalidation
- CDN configuration issues

**Solutions:**
1. **Invalidate CDN cache:**
   ```bash
   # CloudFront
   aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
   
   # Azure CDN
   az cdn endpoint purge --resource-group <rg> --profile-name <profile> --name <endpoint> --content-paths "/*"
   ```

2. **Check cache headers:**
   ```bash
   curl -I https://app.insurance-ai-bridge.com/static/app.js
   ```

3. **Update cache headers:**
   - Set appropriate Cache-Control headers
   - Use ETags for conditional requests
   - Configure cache expiration

4. **Review CDN configuration:**
   - Check cache behaviors
   - Verify origin settings
   - Review compression settings

## Diagnostic Commands

### Application Health
```bash
# Check pod status
kubectl get pods -n insurance-ai-bridge

# Check pod logs
kubectl logs -f deployment/backend -n insurance-ai-bridge

# Check resource usage
kubectl top pods -n insurance-ai-bridge

# Check pod events
kubectl describe pod <pod-name> -n insurance-ai-bridge
```

### Database Health
```bash
# Check database connections
kubectl exec -it postgres-pod -n insurance-ai-bridge -- psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check database size
kubectl exec -it postgres-pod -n insurance-ai-bridge -- psql -c "SELECT pg_size_pretty(pg_database_size('insurance_ai_bridge'));"

# Check replication lag
kubectl exec -it postgres-pod -n insurance-ai-bridge -- psql -c "SELECT * FROM pg_stat_replication;"
```

### Cache Health
```bash
# Check Redis status
kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli PING

# Check Redis info
kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli INFO

# Check cache keys
kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli --scan --pattern "claim:*"
```

### Network Health
```bash
# Check service endpoints
kubectl get endpoints -n insurance-ai-bridge

# Test connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://backend-service:8000/health

# Check ingress status
kubectl describe ingress insurance-ai-bridge-ingress -n insurance-ai-bridge
```

## Getting Help

If these solutions don't resolve your issue:

1. **Check logs:** Review application, database, and infrastructure logs
2. **Review metrics:** Check Grafana dashboards for anomalies
3. **Check documentation:** Review architecture and runbook documentation
4. **Contact support:** Reach out to on-call engineers or open a support ticket

## Contact

For additional troubleshooting assistance:
- **On-Call Engineers**: [Contact Information]
- **Engineering Team**: [Contact Information]
- **Documentation**: See `docs/` directory for more guides


