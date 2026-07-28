#!/usr/bin/env python3
"""Test script for AI fallback mechanism"""

import sys
sys.path.insert(0, '.')

from aperion.ai_summarizer import generate_summary_with_fallback, FALLBACK_PROVIDERS

# Test data
test_results = [
    {
        'title': 'Test Result 1',
        'content': 'This is a test result content for testing the AI fallback mechanism.',
        'url': 'https://example.com/test1'
    },
    {
        'title': 'Test Result 2',
        'content': 'Another test result to verify the fallback functionality works correctly.',
        'url': 'https://example.com/test2'
    }
]

test_query = "What is AI fallback testing?"

print("Testing AI fallback mechanism...")
print(f"Number of fallback providers configured: {len(FALLBACK_PROVIDERS)}")
print("\nFallback providers:")
for i, provider in enumerate(FALLBACK_PROVIDERS, 1):
    print(f"{i}. {provider['provider']}: {provider['model']}")

print("\n" + "="*60)
print("Testing with invalid primary provider (should trigger fallback)")
print("="*60)

# Test with invalid primary provider to trigger fallback
result = generate_summary_with_fallback(
    results=test_results,
    query=test_query,
    endpoint="https://invalid-endpoint.example.com",
    model="invalid-model",
    provider="custom",
    api_key="invalid-key",
    timeout=30,
    max_tokens=200,
)

print("\nResult:")
print(f"Success: {result.get('success')}")
print(f"Error: {result.get('error')}")
print(f"Model used: {result.get('model')}")
print(f"Summary: {result.get('summary')[:200] if result.get('summary') else 'None'}...")
