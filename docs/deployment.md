# Deployment Guide

## Production Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificates obtained
- [ ] Monitoring configured

### Deployment Steps

1. **Environment Setup**
   ```bash
   export NODE_ENV=production
   export API_URL=https://api.yourcompany.com
   export DATABASE_URL=postgresql://user:pass@prod-db:5432/insurance_bridge
   ```

2. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   npm run start
   ```

3. **Run Database Migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Start Backend**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

5. **Configure Nginx**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/insurance-bridge
   sudo ln -s /etc/nginx/sites-available/insurance-bridge /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

6. **Setup SSL**
   ```bash
   sudo certbot --nginx -d api.yourcompany.com
   sudo certbot --nginx -d app.yourcompany.com
   ```

## Docker Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

- Prometheus metrics: `http://localhost:9090`
- Grafana dashboards: `http://localhost:3001`
- Health check: `http://api.yourcompany.com/health`

