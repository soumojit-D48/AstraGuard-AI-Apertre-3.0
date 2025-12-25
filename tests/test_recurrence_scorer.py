"""
Unit tests for Recurrence Scorer
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory_engine.recurrence_scorer import RecurrenceScorer


class TestRecurrenceScorer:
    """Test suite for RecurrenceScorer"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.scorer = RecurrenceScorer(resonance_factor=0.3)
    
    def test_initialization(self):
        """Test scorer initializes correctly"""
        assert self.scorer.resonance_factor == 0.3
    
    def test_calculate_resonance_no_recurrence(self):
        """Test resonance with no recurrence"""
        score = self.scorer.calculate_resonance(
            base_importance=0.5,
            recurrence_count=0,
            time_decay=1.0
        )
        
        # Should be close to base_importance
        assert 0.4 < score < 0.6
    
    def test_calculate_resonance_with_recurrence(self):
        """Test resonance increases with recurrence"""
        base = 0.5
        decay = 1.0
        
        score_0 = self.scorer.calculate_resonance(base, 0, decay)
        score_5 = self.scorer.calculate_resonance(base, 5, decay)
        score_10 = self.scorer.calculate_resonance(base, 10, decay)
        
        # Scores should increase with recurrence
        assert score_5 > score_0
        assert score_10 > score_5
    
    def test_calculate_resonance_with_decay(self):
        """Test resonance decreases with time decay"""
        base = 0.5
        recurrence = 5
        
        score_fresh = self.scorer.calculate_resonance(base, recurrence, 1.0)
        score_old = self.scorer.calculate_resonance(base, recurrence, 0.5)
        
        # Fresh events should score higher
        assert score_fresh > score_old
    
    def test_score_event(self):
        """Test scoring an event with similar events"""
        event_metadata = {'severity': 0.7}
        similar_events = [
            {'temporal_weight': 0.9},
            {'temporal_weight': 0.8},
            {'temporal_weight': 0.7}
        ]
        
        score = self.scorer.score_event(event_metadata, similar_events)
        
        assert score > 0
        assert isinstance(score, float)
    
    def test_score_event_no_similar(self):
        """Test scoring event with no similar events"""
        event_metadata = {'severity': 0.5}
        similar_events = []
        
        score = self.scorer.score_event(event_metadata, similar_events)
        
        # Should return base score
        assert 0.4 < score < 0.6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
