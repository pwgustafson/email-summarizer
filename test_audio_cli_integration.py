#!/usr/bin/env python3
"""
Test script for audio CLI integration functionality.
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    return result

def test_audio_cli_integration():
    """Test the audio CLI integration."""
    print("=" * 60)
    print("TESTING AUDIO CLI INTEGRATION")
    print("=" * 60)
    
    # Test 1: Help command should show audio options
    print("\n1. Testing help command shows audio options...")
    result = run_command("python main.py --help")
    if "--generate-audio" in result.stdout and "--audio-date" in result.stdout:
        print("✓ Audio options are present in help")
    else:
        print("✗ Audio options missing from help")
        return False
    
    # Test 2: Test audio generation for existing transcript
    print("\n2. Testing audio generation for existing transcript...")
    result = run_command("python main.py --audio-date 2025-09-27")
    if result.returncode == 0:
        print("✓ Audio generation succeeded")
        
        # Check if audio file was created
        if os.path.exists("audio_summaries/2025-09-27.mp3"):
            print("✓ Audio file was created")
            file_size = os.path.getsize("audio_summaries/2025-09-27.mp3")
            print(f"✓ Audio file size: {file_size} bytes")
        else:
            print("✗ Audio file was not created")
            return False
    else:
        print("✗ Audio generation failed")
        return False
    
    # Test 3: Test error handling for non-existent transcript
    print("\n3. Testing error handling for non-existent transcript...")
    result = run_command("python main.py --audio-date 2025-01-01")
    if result.returncode == 1 and "Transcript file not found" in result.stderr:
        print("✓ Error handling works correctly")
    else:
        print("✗ Error handling failed")
        return False
    
    # Test 4: Test --generate-audio (today's date)
    print("\n4. Testing --generate-audio command...")
    result = run_command("python main.py --generate-audio")
    if result.returncode == 0:
        print("✓ --generate-audio command succeeded")
    else:
        print("✗ --generate-audio command failed")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("Audio CLI integration is working correctly.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_audio_cli_integration()
    sys.exit(0 if success else 1)