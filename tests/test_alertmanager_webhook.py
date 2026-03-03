#!/usr/bin/env python3
"""
Test script for AlertManager webhook endpoint
Tests the Phase 1 alert ingestion functionality.
"""

import requests
import json
from datetime import datetime, timezone

# Sample AlertManager payload
SAMPLE_ALERTMANAGER_PAYLOAD = {
    "version": "4",
    "groupKey": "{}:{alertname='HighLatency'}",
    "status": "firing",
    "receiver": "sentinelnet",
    "groupLabels": {
        "alertname": "HighLatency"
    },
    "commonLabels": {
        "alertname": "HighLatency",
        "service": "bigquery",
        "cloud_provider": "gcp",
        "region": "us-east1",
        "severity": "warning"
    },
    "commonAnnotations": {
        "summary": "BigQuery High Latency Detected",
        "description": "BigQuery is experiencing high latency (>5s) in us-east1 region",
        "runbook_url": "https://example.com/runbooks/bigquery-high-latency"
    },
    "externalURL": "http://alertmanager:9093",
    "alerts": [
        {
            "status": "firing",
            "labels": {
                "alertname": "HighLatency",
                "service": "bigquery",
                "cloud_provider": "gcp",
                "region": "us-east1",
                "severity": "warning",
                "instance": "bigquery-us-east1",
                "job": "cloud-monitoring"
            },
            "annotations": {
                "summary": "BigQuery High Latency Detected",
                "description": "BigQuery is experiencing high latency (>5s) in us-east1 region. Average query time: 8.2s",
                "runbook_url": "https://example.com/runbooks/bigquery-high-latency",
                "dashboard_url": "https://grafana.example.com/d/bigquery"
            },
            "startsAt": datetime.now(timezone.utc).isoformat(),
            "endsAt": None,
            "generatorURL": "http://prometheus:9090/graph?g0.expr=bigquery_query_latency_seconds%3E5",
            "fingerprint": "abc123def456"
        }
    ]
}

SAMPLE_CRITICAL_ALERT = {
    "version": "4",
    "groupKey": "{}:{alertname='ServiceDown'}",
    "status": "firing",
    "receiver": "sentinelnet",
    "groupLabels": {
        "alertname": "ServiceDown"
    },
    "commonLabels": {
        "alertname": "ServiceDown",
        "service": "vertex-ai",
        "cloud_provider": "gcp",
        "region": "us-central1",
        "severity": "critical"
    },
    "commonAnnotations": {
        "summary": "Vertex AI Prediction Endpoint Down",
        "description": "Vertex AI prediction endpoint is unreachable"
    },
    "externalURL": "http://alertmanager:9093",
    "alerts": [
        {
            "status": "firing",
            "labels": {
                "alertname": "ServiceDown",
                "service": "vertex-ai",
                "cloud_provider": "gcp",
                "region": "us-central1",
                "severity": "critical",
                "instance": "vertex-ai-endpoint-1",
                "job": "cloud-monitoring"
            },
            "annotations": {
                "summary": "Vertex AI Prediction Endpoint Down",
                "description": "Vertex AI prediction endpoint is unreachable. All prediction requests failing."
            },
            "startsAt": datetime.now(timezone.utc).isoformat(),
            "endsAt": None,
            "generatorURL": "http://prometheus:9090/graph",
            "fingerprint": "xyz789ghi012"
        }
    ]
}


def test_webhook(api_url="http://localhost:8000"):
    """Test the AlertManager webhook endpoint"""
    
    print("="*70)
    print("🧪 Testing SentinelNet AlertManager Webhook")
    print("="*70)
    print()
    
    # Test 1: Send warning alert
    print("📨 Test 1: Sending WARNING alert (BigQuery High Latency)...")
    try:
        response = requests.post(
            f"{api_url}/webhooks/alertmanager",
            json=SAMPLE_ALERTMANAGER_PAYLOAD,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Alerts received: {data['alerts_received']}")
            print(f"   Alert IDs: {data['alert_ids']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Send critical alert
    print("📨 Test 2: Sending CRITICAL alert (Vertex AI Down)...")
    try:
        response = requests.post(
            f"{api_url}/webhooks/alertmanager",
            json=SAMPLE_CRITICAL_ALERT,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Alerts received: {data['alerts_received']}")
            print(f"   Alert IDs: {data['alert_ids']}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: Get all alerts
    print("📊 Test 3: Fetching all alerts...")
    try:
        response = requests.get(f"{api_url}/api/alerts")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data['count']} alerts")
            
            for alert in data['alerts']:
                print(f"   - {alert['alertname']}: {alert['status']} ({alert['severity']})")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 4: Get statistics
    print("📈 Test 4: Fetching statistics...")
    try:
        response = requests.get(f"{api_url}/api/stats")
        
        if response.status_code == 200:
            data = response.json()
            stats = data['statistics']
            print(f"✅ Success!")
            print(f"   Total Alerts: {stats['total_alerts']}")
            print(f"   Firing Alerts: {stats['firing_alerts']}")
            print(f"   Total Incidents: {stats['total_incidents']}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("="*70)
    print("🎉 Testing Complete!")
    print("="*70)


if __name__ == "__main__":
    import sys
    
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Testing API at: {api_url}")
    print("Make sure the SentinelNet API is running:")
    print("  conda activate genai && sentinelnet api")
    print()
    
    # input("Press Enter to start tests...")
    
    test_webhook(api_url)
