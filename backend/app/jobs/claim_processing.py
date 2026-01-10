"""
Asynchronous Claim Processing Jobs
Processes claims asynchronously using task queue
"""

from typing import Dict, Any, Optional
import logging

from app.core.task_queue import get_task_queue, TaskQueue


logger = logging.getLogger(__name__)


class ClaimProcessingJob:
    """Asynchronous claim processing job"""
    
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
    
    async def process_claim_async(self, claim_id: str, priority: int = 5) -> str:
        """
        Process a claim asynchronously
        
        Args:
            claim_id: ID of the claim to process
            priority: Task priority (1-10, higher = more urgent)
        
        Returns:
            Task ID for tracking
        """
        task_id = await self.task_queue.enqueue_task(
            task_name="process_claim",
            args=(claim_id,),
            priority=priority,
            queue="claims"
        )
        
        logger.info(f"Enqueued claim processing task: {task_id} for claim: {claim_id}")
        return task_id
    
    async def batch_process_claims(self, claim_ids: list[str], priority: int = 5) -> list[str]:
        """
        Batch process multiple claims
        
        Args:
            claim_ids: List of claim IDs to process
            priority: Task priority
        
        Returns:
            List of task IDs
        """
        task_ids = []
        
        for claim_id in claim_ids:
            task_id = await self.process_claim_async(claim_id, priority)
            task_ids.append(task_id)
        
        logger.info(f"Enqueued {len(task_ids)} claim processing tasks")
        return task_ids
    
    async def process_claim_analysis(self, claim_id: str, llm_provider: str = "openai") -> str:
        """
        Process claim analysis with LLM asynchronously
        
        Args:
            claim_id: ID of the claim to analyze
            llm_provider: LLM provider to use
        
        Returns:
            Task ID
        """
        task_id = await self.task_queue.enqueue_task(
            task_name="analyze_claim_with_llm",
            kwargs={"claim_id": claim_id, "llm_provider": llm_provider},
            priority=7,  # Higher priority for analysis
            queue="llm_processing"
        )
        
        logger.info(f"Enqueued claim analysis task: {task_id} for claim: {claim_id}")
        return task_id


def get_claim_processing_job() -> ClaimProcessingJob:
    """Get claim processing job instance"""
    task_queue = get_task_queue()
    return ClaimProcessingJob(task_queue)

