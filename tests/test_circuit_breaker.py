"""
Comprehensive tests for Circuit Breaker pattern implementation.

Tests all state transitions, edge cases, and recovery scenarios.
Ensures production-grade reliability.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

from core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitOpenError,
    CircuitState,
    register_circuit_breaker,
    get_circuit_breaker,
)


class TestCircuitBreakerStateTransitions:
    """Test state machine transitions"""
    
    @pytest.mark.asyncio
    async def test_closed_state_initial(self):
        """Circuit starts in CLOSED state"""
        cb = CircuitBreaker(name="test_closed_initial")
        assert cb.is_closed
        assert cb.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_closed_state_success(self):
        """Successful calls keep circuit CLOSED"""
        cb = CircuitBreaker(name="test_closed_success")
        
        async def success_func():
            return "success"
        
        result = await cb.call(success_func)
        assert result == "success"
        assert cb.is_closed
        assert cb.metrics.successes_total == 1
    
    @pytest.mark.asyncio
    async def test_closed_to_open_transition(self):
        """Circuit transitions CLOSED → OPEN after failure threshold"""
        cb = CircuitBreaker(
            name="test_closed_to_open",
            failure_threshold=3
        )
        
        async def failing_func():
            raise Exception("Test failure")
        
        # Fail 3 times to trigger OPEN
        for i in range(3):
            with pytest.raises(Exception):
                await cb.call(failing_func)
        
        assert cb.is_open
        assert cb.metrics.trips_total == 1
        assert cb.metrics.consecutive_failures == 3
    
    @pytest.mark.asyncio
    async def test_open_state_fails_fast(self):
        """Circuit in OPEN state fails fast without calling function"""
        cb = CircuitBreaker(
            name="test_open_fails_fast",
            failure_threshold=1
        )
        
        call_count = 0
        
        async def tracked_func():
            nonlocal call_count
            call_count += 1
            raise Exception("Test")
        
        # Trigger open
        with pytest.raises(Exception):
            await cb.call(tracked_func)
        
        assert call_count == 1
        assert cb.is_open
        
        # Next call should fail fast without incrementing call_count
        with pytest.raises(CircuitOpenError):
            await cb.call(tracked_func)
        
        assert call_count == 1  # Function not called
    
    @pytest.mark.asyncio
    async def test_open_to_half_open_transition(self):
        """Circuit transitions OPEN → HALF_OPEN after recovery timeout"""
        cb = CircuitBreaker(
            name="test_open_to_half_open",
            failure_threshold=1,
            recovery_timeout=1
        )
        
        async def failing_func():
            raise Exception("Test")
        
        # Trigger OPEN
        with pytest.raises(Exception):
            await cb.call(failing_func)
        
        assert cb.is_open
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        async def success_func():
            return "recovered"
        
        # Should transition to HALF_OPEN and attempt call
        result = await cb.call(success_func)
        assert result == "recovered"
        assert cb.is_half_open
    
    @pytest.mark.asyncio
    async def test_circuit_recovery_attempt(self):
        """Circuit attempts recovery after timeout"""
        cb = CircuitBreaker(
            name="test_recovery_attempt",
            failure_threshold=2,
            recovery_timeout=1
        )
        
        async def failing_func():
            raise Exception("Test")
        
        # Trigger OPEN with 2 failures
        for _ in range(2):
            with pytest.raises(Exception):
                await cb.call(failing_func)
        
        assert cb.is_open
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Now should transition to HALF_OPEN on next attempt
        async def success_func():
            return "ok"
        
        result = await cb.call(success_func)
        assert result == "ok"
        assert cb.is_half_open


class TestCircuitBreakerMetrics:
    """Test metrics collection"""
    
    @pytest.mark.asyncio
    async def test_success_count_tracking(self):
        """Track successful calls"""
        cb = CircuitBreaker(name="test_success_tracking")
        
        async def success_func():
            return "ok"
        
        for _ in range(5):
            await cb.call(success_func)
        
        assert cb.metrics.successes_total == 5
    
    @pytest.mark.asyncio
    async def test_failure_count_tracking(self):
        """Track failed calls"""
        cb = CircuitBreaker(name="test_failure_tracking", failure_threshold=10)
        
        async def failing_func():
            raise Exception("Test")
        
        for _ in range(5):
            with pytest.raises(Exception):
                await cb.call(failing_func)
        
        assert cb.metrics.failures_total == 5
        assert cb.metrics.consecutive_failures == 5
    
    @pytest.mark.asyncio
    async def test_trips_count_tracking(self):
        """Track circuit trips"""
        cb1 = CircuitBreaker(name="test_trips_tracking_1", failure_threshold=2)
        cb2 = CircuitBreaker(name="test_trips_tracking_2", failure_threshold=2)
        
        async def failing_func():
            raise Exception("Test")
        
        # First breaker: trigger trip
        for _ in range(2):
            with pytest.raises(Exception):
                await cb1.call(failing_func)
        assert cb1.metrics.trips_total >= 1
        
        # Second breaker: should have separate trip count
        for _ in range(2):
            with pytest.raises(Exception):
                await cb2.call(failing_func)
        assert cb2.metrics.trips_total >= 1

    
    @pytest.mark.asyncio
    async def test_metrics_snapshot(self):
        """Get metrics snapshot without locks"""
        cb = CircuitBreaker(name="test_metrics_snapshot")
        
        async def success_func():
            return "ok"
        
        await cb.call(success_func)
        
        metrics = cb.get_metrics()
        assert metrics.state == CircuitState.CLOSED
        assert metrics.successes_total == 1


class TestCircuitBreakerFallback:
    """Test fallback functionality"""
    
    @pytest.mark.asyncio
    async def test_fallback_on_open(self):
        """Use fallback function when circuit is open"""
        cb = CircuitBreaker(name="test_fallback", failure_threshold=1)
        
        async def failing_func():
            raise Exception("Test")
        
        async def fallback_func():
            return "fallback_result"
        
        # Trigger OPEN
        with pytest.raises(Exception):
            await cb.call(failing_func)
        
        # Use fallback
        result = await cb.call(failing_func, fallback=fallback_func)
        assert result == "fallback_result"
    
    @pytest.mark.asyncio
    async def test_no_fallback_raises_error(self):
        """Raise error when circuit is open and no fallback"""
        cb = CircuitBreaker(name="test_no_fallback", failure_threshold=1)
        
        async def failing_func():
            raise Exception("Test")
        
        # Trigger OPEN
        with pytest.raises(Exception):
            await cb.call(failing_func)
        
        # Should raise CircuitOpenError
        with pytest.raises(CircuitOpenError):
            await cb.call(failing_func)


class TestCircuitBreakerEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_selective_exception_handling(self):
        """Only count expected exceptions as failures"""
        cb = CircuitBreaker(
            name="test_selective_exceptions",
            expected_exceptions=(ValueError,),
            failure_threshold=3
        )
        
        async def raises_unexpected():
            raise RuntimeError("Not tracked")
        
        # RuntimeError not in expected_exceptions, should propagate
        with pytest.raises(RuntimeError):
            await cb.call(raises_unexpected)
        
        # Circuit should still be closed (not counting RuntimeError)
        assert cb.is_closed
        assert cb.metrics.failures_total == 0
    
    @pytest.mark.asyncio
    async def test_function_with_args_and_kwargs(self):
        """Pass arguments through circuit breaker"""
        cb = CircuitBreaker(name="test_args_kwargs")
        
        async def func_with_args(a, b, c=None):
            return a + b + (c or 0)
        
        result = await cb.call(func_with_args, 1, 2, c=3)
        assert result == 6
    
    @pytest.mark.asyncio
    async def test_reset_circuit(self):
        """Manually reset circuit to CLOSED"""
        cb = CircuitBreaker(name="test_reset", failure_threshold=1)
        
        async def failing_func():
            raise Exception("Test")
        
        # Trigger OPEN
        with pytest.raises(Exception):
            await cb.call(failing_func)
        
        assert cb.is_open
        
        # Reset
        cb.reset()
        
        assert cb.is_closed
        assert cb.metrics.failures_total == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_calls(self):
        """Handle concurrent calls safely"""
        cb = CircuitBreaker(name="test_concurrent")
        
        async def success_func(delay=0.01):
            await asyncio.sleep(delay)
            return "ok"
        
        # Run 10 concurrent calls
        tasks = [cb.call(success_func) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(r == "ok" for r in results)
        assert cb.metrics.successes_total == 10


class TestCircuitBreakerRegistry:
    """Test circuit breaker registry"""
    
    def test_register_and_retrieve(self):
        """Register and retrieve circuit breaker"""
        cb = CircuitBreaker(name="test_registry_cb")
        registry = CircuitBreakerRegistry()
        
        registry.register(cb)
        retrieved = registry.get("test_registry_cb")
        
        assert retrieved is cb
    
    def test_get_all_breakers(self):
        """Retrieve all registered breakers"""
        registry = CircuitBreakerRegistry()
        
        cb1 = CircuitBreaker(name="cb1")
        cb2 = CircuitBreaker(name="cb2")
        
        registry.register(cb1)
        registry.register(cb2)
        
        all_cbs = registry.get_all()
        assert len(all_cbs) == 2
        assert "cb1" in all_cbs
        assert "cb2" in all_cbs
    
    def test_global_registration(self):
        """Test global registry functions"""
        cb = CircuitBreaker(name="test_global_cb")
        
        # Register globally
        registered = register_circuit_breaker(cb)
        assert registered is cb
        
        # Retrieve globally
        retrieved = get_circuit_breaker("test_global_cb")
        assert retrieved is cb


class TestCircuitBreakerIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_realistic_scenario(self):
        """Test realistic failure and recovery scenario"""
        cb = CircuitBreaker(
            name="test_realistic",
            failure_threshold=3,
            recovery_timeout=2,
            success_threshold=2
        )
        
        call_count = 0
        
        async def flaky_service():
            nonlocal call_count
            call_count += 1
            
            # Fail first 3 times, then succeed
            if call_count <= 3:
                raise Exception("Service error")
            return f"Success #{call_count}"
        
        # Make 3 failing calls
        for _ in range(3):
            with pytest.raises(Exception):
                await cb.call(flaky_service)
        
        assert cb.is_open
        
        # Try to call while open - should fail fast
        with pytest.raises(CircuitOpenError):
            await cb.call(flaky_service)
        
        # Wait for recovery timeout
        await asyncio.sleep(2.1)
        
        # Now should transition to HALF_OPEN and attempt
        result1 = await cb.call(flaky_service)
        assert "Success" in result1
        assert cb.is_half_open
        
        # Another success should close circuit
        result2 = await cb.call(flaky_service)
        assert "Success" in result2
        assert cb.is_closed


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
