#!/usr/bin/env python3
"""
Simple test script to verify RTL-SDR hardware and basic GNU Radio functionality
"""

import sys
try:
    import osmosdr
    from gnuradio import gr
    print("✓ GNU Radio and osmosdr imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def test_rtlsdr():
    """Test RTL-SDR device detection"""
    try:
        # Create a simple source to test device
        source = osmosdr.source(args="numchan=1")
        source.set_sample_rate(2048000)
        source.set_center_freq(146.52e6)

        print("✓ RTL-SDR device created successfully")
        print(f"  Sample rate: {source.get_sample_rate()}")
        print(f"  Center frequency: {source.get_center_freq() / 1e6:.3f} MHz")

        return True

    except Exception as e:
        print(f"✗ RTL-SDR test failed: {e}")
        return False

def test_qt():
    """Test PyQt5 availability"""
    try:
        from PyQt5 import Qt, QtWidgets
        print("✓ PyQt5 import successful")
        return True
    except ImportError as e:
        print(f"✗ PyQt5 import failed: {e}")
        return False

def main():
    print("Testing FM Repeater Monitor dependencies...")
    print("-" * 40)

    success = True

    # Test RTL-SDR
    if not test_rtlsdr():
        success = False

    # Test PyQt5
    if not test_qt():
        success = False

    print("-" * 40)
    if success:
        print("✓ All tests passed! Hardware and dependencies are ready.")
        print("\nTo run the monitor: python3 repeater_monitor.py")
    else:
        print("✗ Some tests failed. Check installation and hardware.")
        print("\nTroubleshooting:")
        print("1. Ensure RTL-SDR dongle is connected")
        print("2. Install missing dependencies: pip install -r requirements.txt")
        print("3. Install GNU Radio: sudo apt install gnuradio gr-osmosdr")

if __name__ == '__main__':
    main()