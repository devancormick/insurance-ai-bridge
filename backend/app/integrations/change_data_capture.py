"""
Change Data Capture (CDC) Implementation
Captures and streams database changes from on-premise to cloud
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
import logging
import json

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Type of database change"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


class ChangeEvent:
    """Represents a database change event"""
    
    def __init__(
        self,
        table_name: str,
        change_type: ChangeType,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.table_name = table_name
        self.change_type = change_type
        self.old_values = old_values or {}
        self.new_values = new_values or {}
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "table_name": self.table_name,
            "change_type": self.change_type.value,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChangeEvent":
        """Create from dictionary"""
        return cls(
            table_name=data["table_name"],
            change_type=ChangeType(data["change_type"]),
            old_values=data.get("old_values"),
            new_values=data.get("new_values"),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class ChangeDataCapture:
    """Change Data Capture implementation using PostgreSQL logical replication"""
    
    def __init__(self, source_db_url: str, target_db_url: str, config: Dict[str, Any]):
        self.source_db_url = source_db_url
        self.target_db_url = target_db_url
        self.config = config
        self.source_engine = create_async_engine(source_db_url)
        self.target_engine = create_async_engine(target_db_url)
        self.running = False
        self.replication_slot = config.get("replication_slot", "insurance_ai_bridge_cdc")
        self.publication_name = config.get("publication_name", "insurance_ai_bridge_publication")
        self.subscribed_tables = config.get("tables", ["claims", "members", "policies"])
        self.event_handlers: List[Callable[[ChangeEvent], None]] = []
    
    async def initialize(self):
        """Initialize CDC setup (create replication slot, publication, etc.)"""
        async with self.source_engine.begin() as conn:
            # Create replication slot
            await conn.execute(
                text(f"""
                    SELECT pg_create_logical_replication_slot(
                        '{self.replication_slot}',
                        'pgoutput'
                    ) WHERE NOT EXISTS (
                        SELECT 1 FROM pg_replication_slots WHERE slot_name = '{self.replication_slot}'
                    );
                """)
            )
            
            # Create publication
            await conn.execute(
                text(f"""
                    CREATE PUBLICATION IF NOT EXISTS {self.publication_name}
                    FOR TABLE {', '.join(self.subscribed_tables)};
                """)
            )
            
            logger.info(f"CDC initialized: replication slot '{self.replication_slot}', publication '{self.publication_name}'")
    
    async def start_capture(self):
        """Start capturing changes"""
        if self.running:
            logger.warning("CDC is already running")
            return
        
        self.running = True
        logger.info("Starting Change Data Capture")
        
        # Start background task to process changes
        asyncio.create_task(self._capture_loop())
    
    async def stop_capture(self):
        """Stop capturing changes"""
        self.running = False
        logger.info("Stopped Change Data Capture")
    
    async def _capture_loop(self):
        """Main loop for capturing and processing changes"""
        while self.running:
            try:
                # Poll for changes using logical replication
                changes = await self._poll_changes()
                
                for change in changes:
                    await self._process_change(change)
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
            
            except Exception as e:
                logger.error(f"Error in CDC capture loop: {e}", exc_info=True)
                await asyncio.sleep(1)  # Back off on error
    
    async def _poll_changes(self) -> List[ChangeEvent]:
        """Poll for database changes using logical replication"""
        # This is a simplified implementation
        # Real implementation would use pgoutput plugin and WAL decoding
        changes = []
        
        async with self.source_engine.begin() as conn:
            # Query WAL for changes (simplified - real implementation uses logical decoding)
            result = await conn.execute(
                text("""
                    SELECT * FROM pg_logical_slot_get_changes(
                        :slot_name,
                        NULL,
                        NULL
                    );
                """),
                {"slot_name": self.replication_slot}
            )
            
            # Process WAL changes into ChangeEvent objects
            # (This would require WAL decoding in real implementation)
        
        return changes
    
    async def _process_change(self, change: ChangeEvent):
        """Process a single change event"""
        try:
            # Apply to target database
            await self._apply_to_target(change)
            
            # Trigger event handlers
            for handler in self.event_handlers:
                try:
                    await handler(change) if asyncio.iscoroutinefunction(handler) else handler(change)
                except Exception as e:
                    logger.error(f"Error in change event handler: {e}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Error processing change event: {e}", exc_info=True)
    
    async def _apply_to_target(self, change: ChangeEvent):
        """Apply change to target database"""
        async with self.target_engine.begin() as conn:
            if change.change_type == ChangeType.INSERT:
                await self._apply_insert(conn, change)
            elif change.change_type == ChangeType.UPDATE:
                await self._apply_update(conn, change)
            elif change.change_type == ChangeType.DELETE:
                await self._apply_delete(conn, change)
    
    async def _apply_insert(self, conn, change: ChangeEvent):
        """Apply INSERT change"""
        table = change.table_name
        values = change.new_values
        
        columns = ", ".join(values.keys())
        placeholders = ", ".join([f":{key}" for key in values.keys()])
        
        query = text(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})")
        await conn.execute(query, values)
    
    async def _apply_update(self, conn, change: ChangeEvent):
        """Apply UPDATE change"""
        table = change.table_name
        values = change.new_values
        old_values = change.old_values
        
        # Use primary key from old_values to identify row
        pk_column = "id"  # Assume 'id' is primary key
        pk_value = old_values.get(pk_column)
        
        if not pk_value:
            logger.warning(f"No primary key found for UPDATE on {table}")
            return
        
        set_clause = ", ".join([f"{key} = :{key}" for key in values.keys()])
        query = text(f"UPDATE {table} SET {set_clause} WHERE {pk_column} = :pk_value")
        
        params = {**values, "pk_value": pk_value}
        await conn.execute(query, params)
    
    async def _apply_delete(self, conn, change: ChangeEvent):
        """Apply DELETE change"""
        table = change.table_name
        old_values = change.old_values
        
        # Use primary key from old_values to identify row
        pk_column = "id"
        pk_value = old_values.get(pk_column)
        
        if not pk_value:
            logger.warning(f"No primary key found for DELETE on {table}")
            return
        
        query = text(f"DELETE FROM {table} WHERE {pk_column} = :pk_value")
        await conn.execute(query, {"pk_value": pk_value})
    
    def register_handler(self, handler: Callable[[ChangeEvent], None]):
        """Register a handler for change events"""
        self.event_handlers.append(handler)
        logger.info(f"Registered change event handler: {handler.__name__}")
    
    def unregister_handler(self, handler: Callable[[ChangeEvent], None]):
        """Unregister a change event handler"""
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
            logger.info(f"Unregistered change event handler: {handler.__name__}")
    
    async def cleanup(self):
        """Cleanup CDC resources"""
        await self.stop_capture()
        
        # Drop replication slot (optional - usually kept for recovery)
        if self.config.get("drop_slot_on_cleanup", False):
            async with self.source_engine.begin() as conn:
                await conn.execute(
                    text(f"SELECT pg_drop_replication_slot('{self.replication_slot}');")
                )
        
        await self.source_engine.dispose()
        await self.target_engine.dispose()


# Global CDC instance
cdc_instance: Optional[ChangeDataCapture] = None


def get_cdc_instance() -> Optional[ChangeDataCapture]:
    """Get the global CDC instance"""
    return cdc_instance


def initialize_cdc(source_db_url: str, target_db_url: str, config: Dict[str, Any]):
    """Initialize global CDC instance"""
    global cdc_instance
    cdc_instance = ChangeDataCapture(source_db_url, target_db_url, config)
    return cdc_instance

