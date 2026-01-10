"""
Data Synchronization Orchestrator
Coordinates data synchronization between cloud and on-premise tiers
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import logging

from app.core.data_tiering import DataTier, DataTieringManager
from app.integrations.change_data_capture import ChangeDataCapture, ChangeEvent
from app.integrations.data_replication import DataReplicator, ReplicationDirection, ConflictResolutionStrategy

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncJob:
    """Represents a data synchronization job"""
    
    def __init__(
        self,
        job_id: str,
        source_tier: DataTier,
        target_tier: DataTier,
        data_ids: List[str],
        direction: ReplicationDirection,
        priority: int = 0
    ):
        self.job_id = job_id
        self.source_tier = source_tier
        self.target_tier = target_tier
        self.data_ids = data_ids
        self.direction = direction
        self.priority = priority
        self.status = SyncStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.progress: float = 0.0
        self.items_synced: int = 0
        self.items_total: int = len(data_ids)


class DataSyncOrchestrator:
    """Orchestrates data synchronization between tiers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tiering_manager = DataTieringManager(config.get("tiering_config", {}))
        self.replicator = DataReplicator(config.get("replication_config", {}))
        self.cdc: Optional[ChangeDataCapture] = None
        self.sync_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.active_jobs: Dict[str, SyncJob] = {}
        self.sync_history: List[SyncJob] = []
        self.running = False
    
    async def initialize(self):
        """Initialize the orchestrator"""
        # Initialize CDC if configured
        if self.config.get("cdc_enabled", True):
            cdc_config = self.config.get("cdc_config", {})
            source_db_url = cdc_config.get("source_db_url")
            target_db_url = cdc_config.get("target_db_url")
            
            if source_db_url and target_db_url:
                from app.integrations.change_data_capture import initialize_cdc
                self.cdc = initialize_cdc(source_db_url, target_db_url, cdc_config)
                await self.cdc.initialize()
                
                # Register CDC handler
                self.cdc.register_handler(self._on_cdc_change)
        
        # Start sync queue processor
        self.running = True
        asyncio.create_task(self._process_sync_queue())
        
        logger.info("Data synchronization orchestrator initialized")
    
    async def schedule_sync(
        self,
        source_tier: DataTier,
        target_tier: DataTier,
        data_ids: List[str],
        direction: ReplicationDirection = ReplicationDirection.BIDIRECTIONAL,
        priority: int = 0
    ) -> str:
        """
        Schedule a data synchronization job
        
        Args:
            source_tier: Source data tier
            target_tier: Target data tier
            data_ids: List of data IDs to synchronize
            direction: Replication direction
            priority: Job priority (higher = more important)
        
        Returns:
            Job ID
        """
        job_id = f"sync-{datetime.utcnow().timestamp()}-{len(self.active_jobs)}"
        
        job = SyncJob(
            job_id=job_id,
            source_tier=source_tier,
            target_tier=target_tier,
            data_ids=data_ids,
            direction=direction,
            priority=priority
        )
        
        # Add to priority queue (negative priority for max-heap behavior)
        await self.sync_queue.put((-priority, job))
        self.active_jobs[job_id] = job
        
        logger.info(f"Scheduled sync job {job_id}: {len(data_ids)} items from {source_tier.value} to {target_tier.value}")
        
        return job_id
    
    async def sync_by_tier(
        self,
        tier: DataTier,
        target_tier: Optional[DataTier] = None,
        age_days: Optional[int] = None
    ) -> str:
        """
        Synchronize all data in a tier
        
        Args:
            tier: Source tier
            target_tier: Target tier (if None, uses tiering rules)
            age_days: Optional age filter (only sync data older than this)
        
        Returns:
            Job ID
        """
        # Get candidates for sync based on tier and age
        # This would query the database
        data_ids = await self._get_sync_candidates(tier, age_days)
        
        if not target_tier:
            # Determine target tier based on tiering rules
            if tier == DataTier.HOT:
                target_tier = DataTier.WARM
            elif tier == DataTier.WARM:
                target_tier = DataTier.COLD
            else:
                logger.warning(f"No target tier specified for {tier.value} tier sync")
                return ""
        
        direction = ReplicationDirection.BIDIRECTIONAL if self.tiering_manager.should_replicate(tier) else ReplicationDirection.CLOUD_TO_ONPREM
        
        return await self.schedule_sync(tier, target_tier, data_ids, direction)
    
    async def _get_sync_candidates(self, tier: DataTier, age_days: Optional[int] = None) -> List[str]:
        """Get candidates for synchronization"""
        # This would query the database based on tier and age
        # Placeholder implementation
        cutoff_date = datetime.utcnow() - timedelta(days=age_days) if age_days else None
        # Query would filter by tier and created_at < cutoff_date
        return []  # Would return actual data IDs
    
    async def _process_sync_queue(self):
        """Process sync queue (background task)"""
        while self.running:
            try:
                # Get job from queue (with timeout)
                priority, job = await asyncio.wait_for(
                    self.sync_queue.get(),
                    timeout=1.0
                )
                
                # Execute sync job
                asyncio.create_task(self._execute_sync_job(job))
            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing sync queue: {e}", exc_info=True)
    
    async def _execute_sync_job(self, job: SyncJob):
        """Execute a sync job"""
        job.status = SyncStatus.IN_PROGRESS
        job.started_at = datetime.utcnow()
        
        logger.info(f"Executing sync job {job.job_id}")
        
        try:
            total_items = len(job.data_ids)
            items_synced = 0
            
            for data_id in job.data_ids:
                try:
                    # Replicate each data item
                    replication_id = await self.replicator.replicate_data(
                        data_id=data_id,
                        source_tier=job.source_tier,
                        target_tier=job.target_tier,
                        direction=job.direction,
                        conflict_strategy=ConflictResolutionStrategy.LAST_WRITE_WINS
                    )
                    
                    # Wait for replication to complete (simplified - would poll status)
                    await asyncio.sleep(0.1)
                    
                    items_synced += 1
                    job.items_synced = items_synced
                    job.progress = items_synced / total_items * 100
                    
                except Exception as e:
                    logger.error(f"Error syncing data {data_id} in job {job.job_id}: {e}")
                    # Continue with next item
            
            job.status = SyncStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.progress = 100.0
            
            logger.info(f"Sync job {job.job_id} completed: {items_synced}/{total_items} items")
        
        except Exception as e:
            job.status = SyncStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            logger.error(f"Sync job {job.job_id} failed: {e}", exc_info=True)
        
        finally:
            # Move to history and remove from active
            self.sync_history.append(job)
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
    
    def _on_cdc_change(self, change: ChangeEvent):
        """Handle CDC change event"""
        # Determine if change should trigger sync
        # This would check tiering rules and schedule sync if needed
        logger.debug(f"CDC change detected: {change.table_name} - {change.change_type.value}")
        
        # Schedule sync for changed data (would extract data_id from change)
        # asyncio.create_task(self._sync_cdc_change(change))
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a sync job"""
        job = self.active_jobs.get(job_id)
        if not job:
            # Check history
            for hist_job in self.sync_history:
                if hist_job.job_id == job_id:
                    job = hist_job
                    break
        
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "source_tier": job.source_tier.value,
            "target_tier": job.target_tier.value,
            "direction": job.direction.value,
            "progress": job.progress,
            "items_synced": job.items_synced,
            "items_total": job.items_total,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error": job.error
        }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a sync job"""
        job = self.active_jobs.get(job_id)
        if job and job.status == SyncStatus.PENDING:
            job.status = SyncStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            return True
        return False
    
    async def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        active_count = len(self.active_jobs)
        completed_count = len([j for j in self.sync_history if j.status == SyncStatus.COMPLETED])
        failed_count = len([j for j in self.sync_history if j.status == SyncStatus.FAILED])
        
        total_items_synced = sum(j.items_synced for j in self.sync_history)
        
        return {
            "active_jobs": active_count,
            "completed_jobs": completed_count,
            "failed_jobs": failed_count,
            "total_items_synced": total_items_synced,
            "queue_size": self.sync_queue.qsize()
        }
    
    async def shutdown(self):
        """Shutdown the orchestrator"""
        self.running = False
        
        if self.cdc:
            await self.cdc.cleanup()
        
        logger.info("Data synchronization orchestrator shut down")


# Global instance
data_sync_orchestrator: Optional[DataSyncOrchestrator] = None


def get_sync_orchestrator() -> DataSyncOrchestrator:
    """Get the global data sync orchestrator instance"""
    global data_sync_orchestrator
    if data_sync_orchestrator is None:
        from app.config import settings
        data_sync_orchestrator = DataSyncOrchestrator(settings.data_sync_config)
    return data_sync_orchestrator

