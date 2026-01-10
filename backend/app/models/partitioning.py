"""
Database Partitioning Strategies
Implements date-based partitioning for claims table
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import text, inspect
from sqlalchemy.ext.declarative import declarative_base

from app.core.database import get_db_session
from app.models.claim import Claim


Base = declarative_base()


class PartitionManager:
    """Manages database table partitioning"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def create_monthly_partition(self, table_name: str, partition_date: date, schema: str = "public"):
        """
        Create a monthly partition for a table
        
        Args:
            table_name: Name of the partitioned table
            partition_date: Date for the partition (used to determine month)
            schema: Database schema name
        """
        partition_name = f"{table_name}_{partition_date.strftime('%Y_%m')}"
        start_date = date(partition_date.year, partition_date.month, 1)
        
        if partition_date.month == 12:
            end_date = date(partition_date.year + 1, 1, 1)
        else:
            end_date = date(partition_date.year, partition_date.month + 1, 1)
        
        # Create partition using PostgreSQL's native partitioning
        query = text(f"""
            CREATE TABLE IF NOT EXISTS {schema}.{partition_name}
            PARTITION OF {schema}.{table_name}
            FOR VALUES FROM ('{start_date}') TO ('{end_date}');
        """)
        
        await self.db_session.execute(query)
        await self.db_session.commit()
        
        return partition_name
    
    async def create_initial_partitions(
        self,
        table_name: str,
        start_date: date,
        months_ahead: int = 12,
        schema: str = "public"
    ) -> List[str]:
        """
        Create initial partitions for a table
        
        Args:
            table_name: Name of the partitioned table
            start_date: Starting date for partitions
            months_ahead: Number of months to create partitions for
            schema: Database schema name
        
        Returns:
            List of created partition names
        """
        created_partitions = []
        
        for i in range(months_ahead):
            partition_date = date(
                start_date.year + (start_date.month + i - 1) // 12,
                ((start_date.month + i - 1) % 12) + 1,
                1
            )
            
            partition_name = await self.create_monthly_partition(
                table_name,
                partition_date,
                schema
            )
            created_partitions.append(partition_name)
        
        return created_partitions
    
    async def create_future_partitions(self, table_name: str, months_ahead: int = 3, schema: str = "public"):
        """
        Create future partitions proactively
        
        Args:
            table_name: Name of the partitioned table
            months_ahead: Number of months ahead to create partitions
            schema: Database schema name
        """
        today = date.today()
        current_month = date(today.year, today.month, 1)
        
        await self.create_initial_partitions(
            table_name,
            current_month,
            months_ahead,
            schema
        )
    
    async def drop_old_partition(self, table_name: str, partition_date: date, schema: str = "public"):
        """
        Drop an old partition (for archival purposes)
        
        Args:
            table_name: Name of the partitioned table
            partition_date: Date of the partition to drop
            schema: Database schema name
        """
        partition_name = f"{table_name}_{partition_date.strftime('%Y_%m')}"
        
        query = text(f"""
            DROP TABLE IF EXISTS {schema}.{partition_name};
        """)
        
        await self.db_session.execute(query)
        await self.db_session.commit()
    
    async def archive_partition(self, table_name: str, partition_date: date, archive_location: str, schema: str = "public"):
        """
        Archive a partition to cold storage
        
        Args:
            table_name: Name of the partitioned table
            partition_date: Date of the partition to archive
            archive_location: Location to archive to
            schema: Database schema name
        """
        partition_name = f"{table_name}_{partition_date.strftime('%Y_%m')}"
        
        # Export partition data to archive location
        query = text(f"""
            COPY {schema}.{partition_name} TO '{archive_location}/{partition_name}.csv'
            WITH (FORMAT CSV, HEADER);
        """)
        
        await self.db_session.execute(query)
        await self.db_session.commit()
        
        # After successful archive, drop the partition
        await self.drop_old_partition(table_name, partition_date, schema)
    
    async def get_partition_info(self, table_name: str, schema: str = "public") -> List[dict]:
        """
        Get information about all partitions for a table
        
        Args:
            table_name: Name of the partitioned table
            schema: Database schema name
        
        Returns:
            List of partition information dictionaries
        """
        query = text("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables
            WHERE tablename LIKE :pattern
            ORDER BY tablename;
        """)
        
        result = await self.db_session.execute(
            query,
            {"pattern": f"{table_name}_%"}
        )
        
        partitions = []
        for row in result:
            partitions.append({
                "schema": row.schemaname,
                "name": row.tablename,
                "size": row.size
            })
        
        return partitions
    
    async def optimize_partition(self, partition_name: str, schema: str = "public"):
        """
        Optimize a partition (VACUUM ANALYZE)
        
        Args:
            partition_name: Name of the partition to optimize
            schema: Database schema name
        """
        query = text(f"VACUUM ANALYZE {schema}.{partition_name};")
        await self.db_session.execute(query)
        await self.db_session.commit()


async def setup_claim_partitioning(db_session, start_date: Optional[date] = None):
    """
    Setup partitioning for claims table
    
    Args:
        db_session: Database session
        start_date: Starting date for partitions (defaults to 1 year ago)
    """
    if start_date is None:
        start_date = date.today().replace(day=1)
        # Go back 12 months
        if start_date.month == 1:
            start_date = start_date.replace(year=start_date.year - 1, month=12)
        else:
            start_date = start_date.replace(month=start_date.month - 1)
    
    partition_manager = PartitionManager(db_session)
    
    # Create table as partitioned table if it doesn't exist
    query = text("""
        CREATE TABLE IF NOT EXISTS public.claims (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            claim_number VARCHAR(255) NOT NULL,
            member_id UUID NOT NULL,
            claim_date DATE NOT NULL,
            amount DECIMAL(10, 2),
            status VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        ) PARTITION BY RANGE (claim_date);
    """)
    
    await db_session.execute(query)
    await db_session.commit()
    
    # Create initial partitions
    await partition_manager.create_initial_partitions("claims", start_date, months_ahead=24)
    
    # Create future partitions
    await partition_manager.create_future_partitions("claims", months_ahead=6)

