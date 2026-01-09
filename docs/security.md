# Security & HIPAA Compliance

## HIPAA Compliance Checklist

### Access Controls
- [ ] Role-based access control (RBAC) implemented
- [ ] Multi-factor authentication (MFA) for all users
- [ ] Automatic session timeout after 15 minutes
- [ ] Audit logging of all data access
- [ ] Minimum necessary access principle enforced

### Data Encryption
- [ ] Encryption at rest (AES-256)
- [ ] Encryption in transit (TLS 1.3)
- [ ] Secure key management (rotate every 90 days)
- [ ] Database encryption enabled
- [ ] Encrypted backups

### PII Protection
- [x] Zero-retention policy for LLM calls
- [x] PII tokenization before external API calls
- [ ] No PII in logs or error messages
- [ ] Automated PII detection in user inputs
- [ ] Data masking in non-production environments

### Audit & Monitoring
- [ ] Comprehensive audit trail (who, what, when)
- [ ] Real-time monitoring of suspicious activity
- [ ] Automated alerts for security events
- [ ] Regular security scans
- [ ] Incident response plan documented

### Business Associate Agreements
- [ ] BAA signed with OpenAI/Anthropic
- [ ] BAA signed with cloud provider
- [ ] BAA signed with any third-party services
- [ ] Data Processing Agreements in place

### Data Retention & Disposal
- [ ] Retention policy documented (7 years for medical records)
- [ ] Secure data disposal procedures
- [ ] Automated data lifecycle management
- [ ] Regular purging of unnecessary data

## Security Best Practices

1. **Never log PII** - All PII must be masked before logging
2. **Use parameterized queries** - Prevent SQL injection
3. **Validate all inputs** - Use Pydantic for request validation
4. **Environment variables** - Never commit secrets to Git
5. **Rate limiting** - Implement on all endpoints
6. **HTTPS only** - Enforce TLS in production
7. **Regular updates** - Keep dependencies up to date

