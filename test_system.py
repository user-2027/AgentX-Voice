"""Test script for the multi-agent call center system."""
import asyncio
import json
from models import CallCenterRequest
from orchestrator import MultiAgentOrchestrator


async def test_scenarios():
    """Test various scenarios."""
    orchestrator = MultiAgentOrchestrator()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Appointment Status Check",
            "request": CallCenterRequest(
                customer_id="CUST-001",
                inquiry_text="I want to check the status of my appointment"
            )
        },
        {
            "name": "Appointment with ID",
            "request": CallCenterRequest(
                customer_id="CUST-001",
                inquiry_text="What's the status of appointment APT-001?"
            )
        },
        {
            "name": "Insurance Validation",
            "request": CallCenterRequest(
                customer_id="CUST-002",
                inquiry_text="Can you verify my insurance coverage? My member ID is INS-67890"
            )
        },
        {
            "name": "Insurance Status Check",
            "request": CallCenterRequest(
                customer_id="CUST-003",
                inquiry_text="Is my insurance still active?"
            )
        },
        {
            "name": "Lab Report Request",
            "request": CallCenterRequest(
                customer_id="CUST-001",
                inquiry_text="I need my lab results from last week"
            )
        },
        {
            "name": "Billing Statement Request",
            "request": CallCenterRequest(
                customer_id="CUST-004",
                inquiry_text="Can you send me my billing statement?"
            )
        },
        {
            "name": "General Inquiry",
            "request": CallCenterRequest(
                customer_id="CUST-005",
                inquiry_text="What are your operating hours?"
            )
        },
        {
            "name": "Appointment Cancellation",
            "request": CallCenterRequest(
                customer_id="CUST-002",
                inquiry_text="I need to cancel my appointment"
            )
        },
        {
            "name": "Medical History Report",
            "request": CallCenterRequest(
                customer_id="CUST-003",
                inquiry_text="I want to request my medical history report"
            )
        },
        {
            "name": "Insurance Benefits Inquiry",
            "request": CallCenterRequest(
                customer_id="CUST-001",
                inquiry_text="What insurance benefits do I have?"
            )
        }
    ]
    
    print("=" * 80)
    print("Multi-Agent Call Center System - Test Suite")
    print("=" * 80)
    print()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'=' * 80}")
        print(f"Customer ID: {test_case['request'].customer_id}")
        print(f"Inquiry: {test_case['request'].inquiry_text}")
        print()
        
        try:
            response = await orchestrator.process_request(test_case['request'])
            
            # Get confidence from synthesis agent response
            from models import AgentType
            synthesis_response = next(
                (r for r in response.agent_responses if r.agent_type == AgentType.SYNTHESIS),
                None
            )
            confidence = synthesis_response.confidence if synthesis_response else 0.0
            
            print(f"✓ Query Type: {response.query_type.value}")
            print(f"✓ Resolved: {response.resolved}")
            print(f"✓ Confidence: {confidence:.2%}")
            print(f"✓ Execution Time: {response.execution_time_ms:.2f}ms")
            print(f"✓ Agents Involved: {', '.join(response.metadata.get('agents_invoked', []))}")
            print()
            print("Response:")
            print("-" * 80)
            print(response.response_text)
            print("-" * 80)
            
            # Show agent responses summary
            print("\nAgent Responses Summary:")
            for agent_resp in response.agent_responses:
                print(f"  • {agent_resp.agent_type.value}: confidence={agent_resp.confidence:.2%}")
            
            results.append({
                "test_case": test_case['name'],
                "success": True,
                "resolved": response.resolved,
                "confidence": confidence,
                "execution_time_ms": response.execution_time_ms
            })
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results.append({
                "test_case": test_case['name'],
                "success": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    successful = sum(1 for r in results if r.get("success", False))
    resolved = sum(1 for r in results if r.get("resolved", False))
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Successful: {successful}/{total}")
    print(f"Resolved: {resolved}/{total}")
    
    if resolved > 0:
        avg_confidence = sum(r["confidence"] for r in results if r.get("resolved", False)) / resolved
        avg_time = sum(r["execution_time_ms"] for r in results if r.get("resolved", False)) / resolved
        print(f"Average Confidence: {avg_confidence:.2%}")
        print(f"Average Execution Time: {avg_time:.2f}ms")
    
    print("\n" + "=" * 80)


async def test_performance():
    """Test system performance with multiple requests."""
    orchestrator = MultiAgentOrchestrator()
    
    requests = [
        CallCenterRequest(
            customer_id=f"CUST-{i % 5 + 1:03d}",
            inquiry_text=inquiry
        )
        for i, inquiry in enumerate([
            "Check my appointment status",
            "Verify my insurance",
            "I need lab results",
            "What's my appointment time?",
            "Is my insurance active?",
            "Request billing statement",
            "Cancel my appointment",
            "Get my medical history",
            "Check insurance coverage",
            "When is my next appointment?"
        ])
    ]
    
    print("\n" + "=" * 80)
    print("Performance Test - Batch Processing")
    print("=" * 80)
    print(f"Processing {len(requests)} requests...")
    
    import time
    start_time = time.time()
    
    responses = await orchestrator.process_batch(requests)
    
    total_time = (time.time() - start_time) * 1000
    avg_time = sum(r.execution_time_ms for r in responses) / len(responses)
    resolved_count = sum(1 for r in responses if r.resolved)
    
    print(f"\nResults:")
    print(f"  Total Requests: {len(requests)}")
    print(f"  Resolved: {resolved_count}/{len(requests)}")
    print(f"  Total Time: {total_time:.2f}ms")
    print(f"  Average per Request: {avg_time:.2f}ms")
    print(f"  Throughput: {len(requests) / (total_time / 1000):.2f} requests/second")


if __name__ == "__main__":
    print("Starting test suite...")
    asyncio.run(test_scenarios())
    asyncio.run(test_performance())

