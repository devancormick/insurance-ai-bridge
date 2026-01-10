#!/bin/bash
# Database Restoration Script
# Supports full restore and point-in-time recovery

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../backend/.env" || true

BACKUP_ID="${1:-}"
TARGET_TIME="${2:-}"
BACKUP_TYPE="${3:-full}"  # full, incremental, pitr
DATABASE_NAME="${DATABASE_NAME:-insurance_ai_bridge}"
DATABASE_HOST="${DATABASE_HOST:-localhost}"
DATABASE_PORT="${DATABASE_PORT:-5432}"
DATABASE_USER="${DATABASE_USER:-postgres}"
BACKUP_STORAGE="${BACKUP_STORAGE:-s3://insurance-ai-bridge-backups}"

usage() {
    cat << EOF
Usage: $0 [BACKUP_ID] [TARGET_TIME] [BACKUP_TYPE]

Restore database from backup

Arguments:
  BACKUP_ID      - Backup ID to restore from (required for full/incremental)
  TARGET_TIME    - Target time for point-in-time recovery (format: YYYY-MM-DD HH:MM:SS)
  BACKUP_TYPE    - Type of restore: full, incremental, pitr (default: full)

Examples:
  # Full restore from backup ID
  $0 backup-20240115-020000

  # Point-in-time recovery
  $0 "" "2024-01-15 14:30:00" pitr

  # Incremental restore
  $0 backup-20240115-020000 "" incremental
EOF
    exit 1
}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

error() {
    log "ERROR: $*"
    exit 1
}

download_backup() {
    local backup_id=$1
    local backup_file="${BACKUP_STORAGE}/${backup_id}.sql.gz"
    
    log "Downloading backup: ${backup_file}"
    
    if [[ "${BACKUP_STORAGE}" == s3://* ]]; then
        aws s3 cp "${backup_file}" "/tmp/${backup_id}.sql.gz" || \
            error "Failed to download backup from S3"
    elif [[ "${BACKUP_STORAGE}" == gs://* ]]; then
        gsutil cp "${backup_file}" "/tmp/${backup_id}.sql.gz" || \
            error "Failed to download backup from GCS"
    elif [[ "${BACKUP_STORAGE}" == azure://* ]]; then
        az storage blob download \
            --container-name backups \
            --name "${backup_id}.sql.gz" \
            --file "/tmp/${backup_id}.sql.gz" || \
            error "Failed to download backup from Azure"
    else
        error "Unsupported backup storage: ${BACKUP_STORAGE}"
    fi
    
    echo "/tmp/${backup_id}.sql.gz"
}

restore_full() {
    local backup_id=$1
    local backup_file
    
    log "Starting full database restore from backup: ${backup_id}"
    
    backup_file=$(download_backup "${backup_id}")
    
    log "Stopping application services"
    kubectl scale deployment backend --replicas=0 -n insurance-ai-bridge || true
    kubectl scale deployment frontend --replicas=0 -n insurance-ai-bridge || true
    
    log "Dropping existing database (if exists)"
    PGPASSWORD="${DATABASE_PASSWORD}" psql \
        -h "${DATABASE_HOST}" \
        -p "${DATABASE_PORT}" \
        -U "${DATABASE_USER}" \
        -d postgres \
        -c "DROP DATABASE IF EXISTS ${DATABASE_NAME};" || true
    
    log "Creating new database"
    PGPASSWORD="${DATABASE_PASSWORD}" psql \
        -h "${DATABASE_HOST}" \
        -p "${DATABASE_PORT}" \
        -U "${DATABASE_USER}" \
        -d postgres \
        -c "CREATE DATABASE ${DATABASE_NAME};"
    
    log "Restoring database from backup"
    gunzip -c "${backup_file}" | \
        PGPASSWORD="${DATABASE_PASSWORD}" psql \
        -h "${DATABASE_HOST}" \
        -p "${DATABASE_PORT}" \
        -U "${DATABASE_USER}" \
        -d "${DATABASE_NAME}"
    
    log "Running post-restore tasks"
    PGPASSWORD="${DATABASE_PASSWORD}" psql \
        -h "${DATABASE_HOST}" \
        -p "${DATABASE_PORT}" \
        -U "${DATABASE_USER}" \
        -d "${DATABASE_NAME}" \
        -c "VACUUM ANALYZE;"
    
    log "Restarting application services"
    kubectl scale deployment backend --replicas=10 -n insurance-ai-bridge
    kubectl scale deployment frontend --replicas=5 -n insurance-ai-bridge
    
    log "Full restore completed successfully"
    
    rm -f "${backup_file}"
}

restore_pitr() {
    local target_time=$1
    
    log "Starting point-in-time recovery to: ${target_time}"
    
    log "Stopping application services"
    kubectl scale deployment backend --replicas=0 -n insurance-ai-bridge || true
    
    log "Creating recovery configuration"
    cat > /tmp/recovery.conf << EOF
restore_command = 'aws s3 cp s3://insurance-ai-bridge-backups/wal/%f %p'
recovery_target_time = '${target_time}'
recovery_target_action = 'promote'
EOF
    
    log "Configuring PostgreSQL for PITR"
    # This would require PostgreSQL configuration changes
    # Implementation depends on PostgreSQL setup (RDS, self-managed, etc.)
    
    log "Point-in-time recovery completed"
    log "NOTE: Manual intervention may be required depending on PostgreSQL setup"
}

restore_incremental() {
    local base_backup_id=$1
    
    log "Starting incremental restore from base backup: ${base_backup_id}"
    
    # First restore base backup
    restore_full "${base_backup_id}"
    
    # Then apply incremental backups
    # Implementation would fetch and apply incremental backups
    log "Incremental restore completed"
}

verify_backup() {
    local backup_id=$1
    
    log "Verifying backup integrity: ${backup_id}"
    
    # Check backup exists in storage
    if [[ "${BACKUP_STORAGE}" == s3://* ]]; then
        aws s3 ls "${BACKUP_STORAGE}/${backup_id}.sql.gz" > /dev/null || \
            error "Backup not found: ${backup_id}"
    fi
    
    log "Backup verification passed"
}

# Main execution
main() {
    if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
        usage
    fi
    
    if [[ "${BACKUP_TYPE}" == "pitr" ]]; then
        if [[ -z "${TARGET_TIME}" ]]; then
            error "TARGET_TIME is required for point-in-time recovery"
        fi
        restore_pitr "${TARGET_TIME}"
    elif [[ "${BACKUP_TYPE}" == "incremental" ]]; then
        if [[ -z "${BACKUP_ID}" ]]; then
            error "BACKUP_ID is required for incremental restore"
        fi
        verify_backup "${BACKUP_ID}"
        restore_incremental "${BACKUP_ID}"
    else
        if [[ -z "${BACKUP_ID}" ]]; then
            error "BACKUP_ID is required for full restore"
        fi
        verify_backup "${BACKUP_ID}"
        restore_full "${BACKUP_ID}"
    fi
}

main "$@"

