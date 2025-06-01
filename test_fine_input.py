#!/usr/bin/env python3
"""
Test script to verify fine input sanitization works correctly
"""

def sanitize_fine_input(denda_raw):
    """Test function to sanitize denda input"""
    denda_raw = denda_raw.strip()
    if not denda_raw:
        raise ValueError("Jumlah denda tidak boleh kosong")
    
    # Remove common thousands separators (dots and commas)
    denda_cleaned = denda_raw.replace('.', '').replace(',', '')
    
    # Validate that the cleaned string contains only digits
    if not denda_cleaned.isdigit():
        raise ValueError("Format denda tidak valid. Masukkan hanya angka.")
    
    denda = int(denda_cleaned)
    
    # Additional validation
    if denda < 0:
        raise ValueError("Denda tidak boleh negatif")
    
    return denda

def test_fine_input_sanitization():
    """Test various input formats"""
    test_cases = [
        # (input, expected_output, should_fail)
        ("10000", 10000, False),
        ("10.000", 10000, False),
        ("10,000", 10000, False),
        ("1.000.000", 1000000, False),
        ("1,000,000", 1000000, False),
        ("5000", 5000, False),
        ("", None, True),  # Empty string should fail
        ("   ", None, True),  # Whitespace only should fail
        ("abc", None, True),  # Non-numeric should fail
        ("10.000abc", None, True),  # Mixed should fail
        ("-5000", None, True),  # Negative should fail (caught by second validation)
        ("0", 0, False),  # Zero should be valid
        ("1", 1, False),  # Single digit should be valid
    ]
    
    print("Testing fine input sanitization...")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for input_val, expected, should_fail in test_cases:
        try:
            result = sanitize_fine_input(input_val)
            if should_fail:
                print(f"❌ FAIL: '{input_val}' should have failed but got {result}")
                failed += 1
            elif result == expected:
                print(f"✅ PASS: '{input_val}' → {result}")
                passed += 1
            else:
                print(f"❌ FAIL: '{input_val}' expected {expected} but got {result}")
                failed += 1
        except Exception as e:
            if should_fail:
                print(f"✅ PASS: '{input_val}' correctly failed with: {e}")
                passed += 1
            else:
                print(f"❌ FAIL: '{input_val}' should not have failed but got: {e}")
                failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Total tests: {len(test_cases)}")
    
    return failed == 0

if __name__ == '__main__':
    success = test_fine_input_sanitization()
    exit(0 if success else 1)
