"""
Performance and load testing for the AI Travel Planner backend.
Tests AI generation performance, database query optimization, and concurrent user scenarios.
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import threading


class TestAIGenerationPerformance:
    """Test AI generation performance and response times."""
    
    def test_ai_generation_response_time(self, client: TestClient):
        """Test that AI generation completes within acceptable time limits."""
        
        trip_request = {
            "destination": "Paris",
            "days": 5,
            "budget": "moderate",
            "travelers": "couple"
        }
        
        # Mock AI service to simulate realistic response times
        with patch('app.services.ai_service.AIService.generate_itinerary') as mock_ai:
            # Simulate AI processing time (should be under 10 seconds)
            def mock_generate(*args, **kwargs):
                time.sleep(0.5)  # Simulate 500ms AI processing
                return {
                    "daily_plans": [
                        {
                            "day_number": i + 1,
                            "activities": [
                                {
                                    "name": f"Activity {i + 1}",
                                    "description": "Test activity",
                                    "duration": 120,
                                    "cost": 50.0,
                                    "category": "sightseeing"
                                }
                            ],
                            "transport": [
                                {
                                    "type": "metro",
                                    "provider": "Local Metro",
                                    "cost": 2.50,
                                    "duration": 15,
                                    "route": "Test route"
                                }
                            ],
                            "estimated_cost": 52.50
                        }
                        for i in range(5)
                    ],
                    "total_budget": 262.50
                }
            
            mock_ai.side_effect = mock_generate
            
            # Measure response time
            start_time = time.time()
            response = client.post("/api/v1/plan-trip", json=trip_request)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Performance assertions
            assert response_time < 10.0, f"AI generation took too long: {response_time:.2f}s"
            
            if response.status_code == 200:
                assert response_time < 5.0, f"Successful response should be under 5s: {response_time:.2f}s"
                
                # Verify response structure is complete
                data = response.json()
                assert "daily_plans" in data
                assert len(data["daily_plans"]) == 5
                assert "total_budget" in data
    
    def test_multiple_ai_requests_performance(self, client: TestClient):
        """Test performance with multiple sequential AI requests."""
        
        trip_requests = [
            {
                "destination": f"City{i}",
                "days": 3,
                "budget": "moderate",
                "travelers": "couple"
            }
            for i in range(5)
        ]
        
        with patch('app.services.ai_service.AIService.generate_itinerary') as mock_ai:
            # Mock consistent response time
            def mock_generate(*args, **kwargs):
                time.sleep(0.3)  # 300ms per request
                return {
                    "daily_plans": [
                        {
                            "day_number": 1,
                            "activities": [
                                {
                                    "name": "Test Activity",
                                    "description": "Test description",
                                    "duration": 120,
                                    "cost": 30.0,
                                    "category": "sightseeing"
                                }
                            ],
                            "transport": [
                                {
                                    "type": "bus",
                                    "provider": "Local Bus",
                                    "cost": 2.0,
                                    "duration": 20,
                                    "route": "Test route"
                                }
                            ],
                            "estimated_cost": 32.0
                        }
                        for _ in range(3)
                    ],
                    "total_budget": 96.0
                }
            
            mock_ai.side_effect = mock_generate
            
            response_times = []
            
            for request in trip_requests:
                start_time = time.time()
                response = client.post("/api/v1/plan-trip", json=request)
                end_time = time.time()
                
                response_times.append(end_time - start_time)
                
                # Each request should complete reasonably quickly
                assert response_times[-1] < 5.0
            
            # Performance statistics
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time:.2f}s"
            assert max_response_time < 3.0, f"Max response time too high: {max_response_time:.2f}s"
    
    def test_ai_error_handling_performance(self, client: TestClient):
        """Test that error handling doesn't cause performance degradation."""
        
        invalid_request = {
            "destination": "",  # Invalid destination
            "days": 5,
            "budget": "moderate",
            "travelers": "couple"
        }
        
        # Measure error response time
        start_time = time.time()
        response = client.post("/api/v1/plan-trip", json=invalid_request)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Error responses should be fast
        assert response_time < 1.0, f"Error response took too long: {response_time:.2f}s"
        assert response.status_code in [400, 422, 503]  # Expected error codes


class TestDatabasePerformance:
    """Test database query optimization and performance."""
    
    @pytest.mark.asyncio
    async def test_trip_storage_performance(self):
        """Test trip storage performance with database operations."""
        
        from app.services.database_service import DatabaseService
        from app.models.trip_models import TripItinerary, DayPlan, Activity, TransportOption
        
        # Create test database service (will use testing mode)
        db_service = DatabaseService(testing_mode=True)
        
        # Create a sample trip for performance testing
        sample_trip = TripItinerary(
            trip_id="perf-test-trip",
            destination="Performance Test City",
            total_days=5,
            daily_plans=[
                DayPlan(
                    day_number=i + 1,
                    activities=[
                        Activity(
                            name=f"Activity {i + 1}",
                            description="Performance test activity",
                            duration=120,
                            cost=50.0,
                            category="sightseeing"
                        )
                    ],
                    transport=[
                        TransportOption(
                            type="metro",
                            provider="Test Metro",
                            cost=2.50,
                            duration=15,
                            route="Test route"
                        )
                    ],
                    estimated_cost=52.50
                )
                for i in range(5)
            ],
            total_budget=262.50
        )
        
        # Test storage performance (should complete quickly even in testing mode)
        start_time = time.time()
        
        try:
            # This will fail in testing mode, but we're measuring the time to failure
            await db_service.save_trip(sample_trip)
        except RuntimeError:
            # Expected in testing mode
            pass
        
        end_time = time.time()
        operation_time = end_time - start_time
        
        # Database operations should be fast (even failures)
        assert operation_time < 0.1, f"Database operation took too long: {operation_time:.3f}s"
    
    def test_multiple_database_operations_performance(self):
        """Test performance with multiple database operations."""
        
        from app.services.database_service import DatabaseService
        
        # Create multiple database service instances
        db_services = [DatabaseService(testing_mode=True) for _ in range(10)]
        
        start_time = time.time()
        
        # Test multiple instantiations (should be fast)
        for db_service in db_services:
            assert db_service.backend_type == "testing"
        
        end_time = time.time()
        operation_time = end_time - start_time
        
        # Multiple instantiations should be fast
        assert operation_time < 0.5, f"Multiple DB instantiations took too long: {operation_time:.3f}s"


class TestConcurrentUserScenarios:
    """Test concurrent user scenarios and system load handling."""
    
    def test_concurrent_health_checks(self, client: TestClient):
        """Test system performance under concurrent health check requests."""
        
        def make_health_request():
            """Make a single health check request and return response time."""
            start_time = time.time()
            response = client.get("/api/v1/health")
            end_time = time.time()
            return {
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
        
        # Test with 20 concurrent health checks
        num_concurrent_requests = 20
        
        with ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
            # Submit all requests concurrently
            futures = [executor.submit(make_health_request) for _ in range(num_concurrent_requests)]
            
            # Collect results
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze performance
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Performance assertions
        assert success_count >= num_concurrent_requests * 0.9, "At least 90% of requests should succeed"
        assert avg_response_time < 1.0, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 2.0, f"Max response time too high: {max_response_time:.3f}s"
    
    def test_concurrent_trip_planning_requests(self, client: TestClient):
        """Test concurrent trip planning requests (with mocked AI)."""
        
        def make_trip_request(request_id: int):
            """Make a single trip planning request."""
            trip_request = {
                "destination": f"TestCity{request_id}",
                "days": 3,
                "budget": "moderate",
                "travelers": "couple"
            }
            
            start_time = time.time()
            response = client.post("/api/v1/plan-trip", json=trip_request)
            end_time = time.time()
            
            return {
                "request_id": request_id,
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
        
        # Mock AI service for consistent testing
        with patch('app.services.ai_service.AIService.generate_itinerary') as mock_ai:
            def mock_generate(*args, **kwargs):
                # Simulate variable AI processing time
                time.sleep(0.1 + (threading.current_thread().ident % 3) * 0.1)
                return {
                    "daily_plans": [
                        {
                            "day_number": 1,
                            "activities": [
                                {
                                    "name": "Concurrent Test Activity",
                                    "description": "Test activity for concurrent requests",
                                    "duration": 120,
                                    "cost": 40.0,
                                    "category": "sightseeing"
                                }
                            ],
                            "transport": [
                                {
                                    "type": "taxi",
                                    "provider": "Test Taxi",
                                    "cost": 15.0,
                                    "duration": 20,
                                    "route": "Test route"
                                }
                            ],
                            "estimated_cost": 55.0
                        }
                        for _ in range(3)
                    ],
                    "total_budget": 165.0
                }
            
            mock_ai.side_effect = mock_generate
            
            # Test with 10 concurrent trip planning requests
            num_concurrent_requests = 10
            
            with ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
                # Submit all requests concurrently
                futures = [
                    executor.submit(make_trip_request, i) 
                    for i in range(num_concurrent_requests)
                ]
                
                # Collect results
                results = []
                for future in as_completed(futures):
                    try:
                        results.append(future.result())
                    except Exception as e:
                        # Handle any exceptions from concurrent requests
                        results.append({
                            "request_id": -1,
                            "response_time": 10.0,  # Max time for failed requests
                            "status_code": 500,
                            "success": False,
                            "error": str(e)
                        })
            
            # Analyze concurrent performance
            response_times = [r["response_time"] for r in results]
            success_count = sum(1 for r in results if r["success"])
            
            if response_times:  # Only analyze if we have results
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                
                # Concurrent performance assertions (more lenient than single requests)
                assert avg_response_time < 5.0, f"Concurrent avg response time too high: {avg_response_time:.3f}s"
                assert max_response_time < 10.0, f"Concurrent max response time too high: {max_response_time:.3f}s"
                
                # At least some requests should succeed (system shouldn't completely fail)
                assert success_count >= 1, "At least one concurrent request should succeed"
    
    def test_memory_usage_under_load(self, client: TestClient):
        """Test that memory usage remains reasonable under load."""
        
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make multiple requests to test memory usage
        for i in range(50):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
        
        # Check memory usage after load
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for health checks)
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase:.2f}MB"
    
    def test_response_time_consistency(self, client: TestClient):
        """Test that response times remain consistent under repeated load."""
        
        response_times = []
        
        # Make 30 sequential requests
        for i in range(30):
            start_time = time.time()
            response = client.get("/api/v1/health")
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == 200
        
        # Analyze consistency
        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        
        # Response times should be consistent (low standard deviation)
        assert avg_time < 0.5, f"Average response time too high: {avg_time:.3f}s"
        assert std_dev < 0.2, f"Response time too inconsistent (std dev: {std_dev:.3f}s)"


class TestResourceUtilization:
    """Test resource utilization and optimization."""
    
    def test_cpu_usage_under_load(self, client: TestClient):
        """Test CPU usage remains reasonable under load."""
        
        import psutil
        
        # Measure CPU usage during load test
        cpu_percentages = []
        
        def measure_cpu():
            """Measure CPU usage in background."""
            for _ in range(10):
                cpu_percentages.append(psutil.cpu_percent(interval=0.1))
        
        # Start CPU monitoring in background
        import threading
        cpu_thread = threading.Thread(target=measure_cpu)
        cpu_thread.start()
        
        # Generate load
        for i in range(20):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
        
        # Wait for CPU monitoring to complete
        cpu_thread.join()
        
        if cpu_percentages:
            avg_cpu = statistics.mean(cpu_percentages)
            max_cpu = max(cpu_percentages)
            
            # CPU usage should be reasonable (these are lenient limits for testing)
            assert avg_cpu < 80, f"Average CPU usage too high: {avg_cpu:.1f}%"
            assert max_cpu < 95, f"Peak CPU usage too high: {max_cpu:.1f}%"
    
    def test_error_rate_under_load(self, client: TestClient):
        """Test that error rates remain low under load."""
        
        total_requests = 100
        error_count = 0
        
        for i in range(total_requests):
            try:
                response = client.get("/api/v1/health")
                if response.status_code >= 400:
                    error_count += 1
            except Exception:
                error_count += 1
        
        error_rate = error_count / total_requests
        
        # Error rate should be very low for health checks
        assert error_rate < 0.05, f"Error rate too high: {error_rate:.2%}"