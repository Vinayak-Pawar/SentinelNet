"""
Database module for SentinelNet
Simple SQLite-based storage for alerts and incidents.
"""

import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class AlertDatabase:
    """
    SQLite database for storing alerts and incidents.
    
    This is a simple implementation for Phase 1.
    Will be upgraded to PostgreSQL with SQLAlchemy in Phase 2.
    """
    
    def __init__(self, db_path: str = "data/sentinelnet.db"):
        """
        Initialize the alert database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_schema()
        
        logger.info(f"✅ AlertDatabase initialized at {db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_schema(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    alertname TEXT NOT NULL,
                    status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    service TEXT,
                    cloud_provider TEXT,
                    region TEXT,
                    summary TEXT,
                    description TEXT,
                    starts_at TEXT NOT NULL,
                    ends_at TEXT,
                    received_at TEXT NOT NULL,
                    acknowledged_at TEXT,
                    resolved_at TEXT,
                    fingerprint TEXT,
                    generator_url TEXT,
                    labels TEXT,
                    annotations TEXT,
                    enriched INTEGER DEFAULT 0,
                    cloud_context TEXT,
                    incident_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Incidents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    alert_count INTEGER DEFAULT 0,
                    affected_services TEXT,
                    affected_clouds TEXT,
                    affected_regions TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    resolved_at TEXT,
                    impact_analysis TEXT,
                    remediation_plan_id TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_service ON alerts(service)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_incident ON alerts(incident_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)")
            
            logger.info("✅ Database schema initialized")
    
    def store_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Store an alert in the database.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Success status
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO alerts (
                        id, alertname, status, severity, service, cloud_provider, region,
                        summary, description, starts_at, ends_at, received_at,
                        acknowledged_at, resolved_at, fingerprint, generator_url,
                        labels, annotations, enriched, cloud_context, incident_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert['id'],
                    alert['alertname'],
                    alert['status'],
                    alert.get('severity', 'medium'),
                    alert.get('service'),
                    alert.get('cloud_provider'),
                    alert.get('region'),
                    alert.get('summary'),
                    alert.get('description'),
                    alert['starts_at'] if isinstance(alert['starts_at'], str) else alert['starts_at'].isoformat(),
                    alert.get('ends_at').isoformat() if alert.get('ends_at') else None,
                    alert['received_at'] if isinstance(alert['received_at'], str) else alert['received_at'].isoformat(),
                    alert.get('acknowledged_at').isoformat() if alert.get('acknowledged_at') else None,
                    alert.get('resolved_at').isoformat() if alert.get('resolved_at') else None,
                    alert.get('fingerprint'),
                    alert.get('generator_url'),
                    json.dumps(alert.get('labels', {})),
                    json.dumps(alert.get('annotations', {})),
                    1 if alert.get('enriched', False) else 0,
                    json.dumps(alert.get('cloud_context')) if alert.get('cloud_context') else None,
                    alert.get('incident_id')
                ))
                
                logger.info(f"✅ Stored alert: {alert['id']}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to store alert: {e}")
            return False
    
    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an alert by ID.
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            Alert dictionary or None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
                row = cursor.fetchone()
                
                if row:
                    alert = dict(row)
                    # Parse JSON fields
                    alert['labels'] = json.loads(alert['labels']) if alert['labels'] else {}
                    alert['annotations'] = json.loads(alert['annotations']) if alert['annotations'] else {}
                    alert['cloud_context'] = json.loads(alert['cloud_context']) if alert['cloud_context'] else None
                    alert['enriched'] = bool(alert['enriched'])
                    return alert
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get alert: {e}")
            return None
    
    def get_alerts(
        self,
        status: Optional[str] = None,
        service: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with optional filtering.
        
        Args:
            status: Filter by status
            service: Filter by service
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of alerts
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM alerts WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if service:
                    query += " AND service = ?"
                    params.append(service)
                
                query += " ORDER BY received_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                alerts = []
                for row in rows:
                    alert = dict(row)
                    alert['labels'] = json.loads(alert['labels']) if alert['labels'] else {}
                    alert['annotations'] = json.loads(alert['annotations']) if alert['annotations'] else {}
                    alert['cloud_context'] = json.loads(alert['cloud_context']) if alert['cloud_context'] else None
                    alert['enriched'] = bool(alert['enriched'])
                    alerts.append(alert)
                
                return alerts
                
        except Exception as e:
            logger.error(f"❌ Failed to get alerts: {e}")
            return []
    
    def update_alert_status(self, alert_id: str, status: str) -> bool:
        """
        Update alert status.
        
        Args:
            alert_id: Alert identifier
            status: New status
            
        Returns:
            Success status
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                timestamp = datetime.now().isoformat()
                
                if status == 'acknowledged':
                    cursor.execute(
                        "UPDATE alerts SET status = ?, acknowledged_at = ? WHERE id = ?",
                        (status, timestamp, alert_id)
                    )
                elif status == 'resolved':
                    cursor.execute(
                        "UPDATE alerts SET status = ?, resolved_at = ? WHERE id = ?",
                        (status, timestamp, alert_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE alerts SET status = ? WHERE id = ?",
                        (status, alert_id)
                    )
                
                logger.info(f"✅ Updated alert {alert_id} status to {status}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to update alert status: {e}")
            return False
    
    def store_incident(self, incident: Dict[str, Any]) -> bool:
        """
        Store an incident in the database.
        
        Args:
            incident: Incident dictionary
            
        Returns:
            Success status
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO incidents (
                        id, title, status, severity, alert_count,
                        affected_services, affected_clouds, affected_regions,
                        created_at, updated_at, resolved_at,
                        impact_analysis, remediation_plan_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incident['id'],
                    incident['title'],
                    incident['status'],
                    incident['severity'],
                    incident.get('alert_count', 0),
                    json.dumps(incident.get('affected_services', [])),
                    json.dumps(incident.get('affected_clouds', [])),
                    json.dumps(incident.get('affected_regions', [])),
                    incident['created_at'] if isinstance(incident['created_at'], str) else incident['created_at'].isoformat(),
                    incident['updated_at'] if isinstance(incident['updated_at'], str) else incident['updated_at'].isoformat(),
                    incident.get('resolved_at').isoformat() if incident.get('resolved_at') else None,
                    incident.get('impact_analysis'),
                    incident.get('remediation_plan_id')
                ))
                
                logger.info(f"✅ Stored incident: {incident['id']}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to store incident: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) as total FROM alerts")
                total_alerts = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as firing FROM alerts WHERE status = 'firing'")
                firing_alerts = cursor.fetchone()['firing']
                
                cursor.execute("SELECT COUNT(*) as total FROM incidents")
                total_incidents = cursor.fetchone()['total']
                
                return {
                    'total_alerts': total_alerts,
                    'firing_alerts': firing_alerts,
                    'total_incidents': total_incidents
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {}


# Singleton instance
_db_instance: Optional[AlertDatabase] = None


def get_database() -> AlertDatabase:
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = AlertDatabase()
    return _db_instance
