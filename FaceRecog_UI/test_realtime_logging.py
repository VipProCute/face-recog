#!/usr/bin/env python3
"""
Test script để kiểm tra real-time logging
"""

from access_history import AccessHistory
import time

def test_realtime_logging():
    print("=" * 60)
    print("TESTING REAL-TIME ACCESS LOGGING")
    print("=" * 60)
    
    # Khởi tạo AccessHistory với file thật
    access_history = AccessHistory('login_history.json')
    
    print(f"📋 Current history has {len(access_history.get_history())} entries")
    
    # Test case: Simulate recognition của một user
    test_user = "Real Time Test User"
    
    print(f"\n🎯 Simulating recognition for: {test_user}")
    
    # Call log_access như trong app_streamlit.py
    result = access_history.log_access(test_user)
    
    print(f"📊 Log result: {result}")
    
    # Verify ngay lập tức bằng cách đọc lại file
    print(f"\n🔍 Verifying file was saved...")
    
    # Tạo instance mới để đọc từ file
    verify_access = AccessHistory('login_history.json')
    new_history = verify_access.get_history()
    
    print(f"📋 File now contains {len(new_history)} entries")
    
    # Tìm entry vừa thêm
    found = False
    for entry in new_history:
        if test_user in entry:
            print(f"✅ Found entry: {entry}")
            found = True
            break
    
    if not found:
        print(f"❌ Entry not found in file!")
    
    print(f"\n🏁 Test completed!")

if __name__ == "__main__":
    test_realtime_logging()
