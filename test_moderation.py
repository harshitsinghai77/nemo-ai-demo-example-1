#!/usr/bin/env python3
"""
Simple test script to verify moderation functionality is working correctly.
This script tests the core functions without actually deploying to AWS.
"""

import json
import sys
import os
from unittest.mock import Mock, patch

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_detect_moderation_content():
    """Test the moderation detection function."""
    
    # Mock the boto3 rekognition client
    mock_rekognition = Mock()
    mock_rekognition.detect_moderation_labels.return_value = {
        "ModerationLabels": [
            {
                "Confidence": 95.5,
                "Name": "Explicit Nudity",
                "ParentName": "Explicit"
            }
        ]
    }
    
    # Test the function
    with patch('src.image_analyzer.rekognition', mock_rekognition):
        from image_analyzer import detect_moderation_content
        
        result = detect_moderation_content("test-bucket", "test-key")
        
        # Verify the API was called correctly
        mock_rekognition.detect_moderation_labels.assert_called_once_with(
            Image={"S3Object": {"Bucket": "test-bucket", "Name": "test-key"}},
            MinConfidence=60
        )
        
        # Verify the result
        assert len(result) == 1
        assert result[0]["Name"] == "Explicit Nudity"
        assert result[0]["Confidence"] == 95.5
        print("✓ detect_moderation_content test passed")

def test_detect_moderation_content_no_issues():
    """Test the moderation detection function when no issues are found."""
    
    # Mock the boto3 rekognition client
    mock_rekognition = Mock()
    mock_rekognition.detect_moderation_labels.return_value = {
        "ModerationLabels": []
    }
    
    # Test the function
    with patch('src.image_analyzer.rekognition', mock_rekognition):
        from image_analyzer import detect_moderation_content
        
        result = detect_moderation_content("test-bucket", "test-key")
        
        # Verify empty result for clean images
        assert len(result) == 0
        print("✓ detect_moderation_content (no issues) test passed")

def test_detect_moderation_content_error_handling():
    """Test the moderation detection function error handling."""
    
    # Mock the boto3 rekognition client to raise an exception
    mock_rekognition = Mock()
    mock_rekognition.detect_moderation_labels.side_effect = Exception("API Error")
    
    # Test the function
    with patch('src.image_analyzer.rekognition', mock_rekognition):
        from image_analyzer import detect_moderation_content
        
        result = detect_moderation_content("test-bucket", "test-key")
        
        # Verify error is handled gracefully
        assert len(result) == 0
        print("✓ detect_moderation_content error handling test passed")

def test_save_analysis_with_moderation():
    """Test saving analysis with moderation labels."""
    
    # Mock DynamoDB table
    mock_table = Mock()
    
    with patch('src.storage.table', mock_table):
        from storage import save_analysis
        
        labels = [{"Name": "Person", "Confidence": 99.9}]
        summary = "A person in the image"
        moderation_labels = [{"Name": "Explicit Nudity", "Confidence": 95.5}]
        
        save_analysis("test-id", labels, summary, moderation_labels)
        
        # Verify the item was saved correctly
        mock_table.put_item.assert_called_once()
        saved_item = mock_table.put_item.call_args[1]['Item']
        
        assert saved_item['id'] == 'test-id'
        assert saved_item['labels'] == labels
        assert saved_item['summary'] == summary
        assert saved_item['moderation_labels'] == moderation_labels
        print("✓ save_analysis with moderation test passed")

def test_save_analysis_no_moderation():
    """Test saving analysis without moderation labels."""
    
    # Mock DynamoDB table
    mock_table = Mock()
    
    with patch('src.storage.table', mock_table):
        from storage import save_analysis
        
        labels = [{"Name": "Person", "Confidence": 99.9}]
        summary = "A person in the image"
        
        save_analysis("test-id", labels, summary)
        
        # Verify the item was saved correctly without moderation_labels
        mock_table.put_item.assert_called_once()
        saved_item = mock_table.put_item.call_args[1]['Item']
        
        assert saved_item['id'] == 'test-id'
        assert saved_item['labels'] == labels
        assert saved_item['summary'] == summary
        assert 'moderation_labels' not in saved_item
        print("✓ save_analysis without moderation test passed")

def test_get_analysis_backward_compatibility():
    """Test getting analysis with backward compatibility."""
    
    # Mock DynamoDB table
    mock_table = Mock()
    mock_table.get_item.return_value = {
        'Item': {
            'id': 'test-id',
            'labels': [{"Name": "Person", "Confidence": 99.9}],
            'summary': 'A person in the image'
            # No moderation_labels field (old record)
        }
    }
    
    with patch('src.storage.table', mock_table):
        from storage import get_analysis
        
        result = get_analysis("test-id")
        
        # Verify backward compatibility
        assert result['id'] == 'test-id'
        assert result['moderation_labels'] == []
        print("✓ get_analysis backward compatibility test passed")

def test_schemas():
    """Test the updated schemas."""
    from schemas import ImageAnalysisRequest, ImageAnalysisResponse
    
    # Test request schema
    request = ImageAnalysisRequest(bucket="test-bucket", key="test-key")
    assert request.bucket == "test-bucket"
    assert request.key == "test-key"
    
    # Test response schema
    response = ImageAnalysisResponse(
        analysis_id="test-id",
        labels=[{"Name": "Person"}],
        summary="Test summary",
        moderation_labels=[{"Name": "Explicit Nudity"}]
    )
    assert response.analysis_id == "test-id"
    assert response.moderation_labels[0]["Name"] == "Explicit Nudity"
    
    # Test response schema with no moderation labels
    response_clean = ImageAnalysisResponse(
        analysis_id="test-id",
        labels=[{"Name": "Person"}],
        summary="Test summary"
    )
    assert response_clean.moderation_labels is None
    
    print("✓ Schema tests passed")

if __name__ == "__main__":
    """Run all tests."""
    
    # Mock AWS PowerTools components
    with patch('src.image_analyzer.logger'), \
         patch('src.image_analyzer.tracer'), \
         patch('src.storage.logger'), \
         patch('src.storage.tracer'):
        
        try:
            test_detect_moderation_content()
            test_detect_moderation_content_no_issues()
            test_detect_moderation_content_error_handling()
            test_save_analysis_with_moderation()
            test_save_analysis_no_moderation()
            test_get_analysis_backward_compatibility()
            test_schemas()
            
            print("\n🎉 All tests passed! Content moderation functionality is working correctly.")
            print("\nKey features implemented:")
            print("- Content moderation detection using AWS Rekognition")
            print("- 60% confidence threshold for moderation labels")
            print("- Graceful error handling")
            print("- Backward compatibility with existing data")
            print("- Updated schema with moderation_labels field")
            print("- Storage and retrieval of moderation results")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            sys.exit(1)