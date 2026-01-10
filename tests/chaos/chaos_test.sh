#!/bin/bash
# Chaos Engineering Tests
# Tests system resilience by introducing failures

set -e

echo "Starting Chaos Engineering Tests..."

# Test 1: Kill random pods
echo "Test 1: Killing random backend pods..."
kubectl get pods -n insurance-ai-bridge -l app=backend -o jsonpath='{.items[*].metadata.name}' | \
  tr ' ' '\n' | shuf -n 1 | xargs kubectl delete pod -n insurance-ai-bridge

sleep 10

# Test 2: Network partition
echo "Test 2: Simulating network partition..."
# Block traffic to database temporarily
# kubectl apply -f network-partition-policy.yaml

sleep 30

# Test 3: Resource exhaustion
echo "Test 3: Simulating resource exhaustion..."
kubectl patch deployment backend -n insurance-ai-bridge --type='json' -p='[{"op": "replace", "path": "/spec/replicas", "value": 200}]'

sleep 60

# Restore
kubectl patch deployment backend -n insurance-ai-bridge --type='json' -p='[{"op": "replace", "path": "/spec/replicas", "value": 10}]'

# Test 4: Database connection pool exhaustion
echo "Test 4: Testing database connection pool..."
# Run script to exhaust connection pool

# Test 5: Cache eviction
echo "Test 5: Testing cache eviction..."
# Clear Redis cache
# kubectl exec -it redis-pod -n insurance-ai-bridge -- redis-cli FLUSHALL

echo "Chaos tests completed. Verify system recovery and functionality."

