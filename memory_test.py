import requests
import json
from datetime import datetime
import time

class MemoryTester:
    def __init__(self, base_url="https://companions-api.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.companion_id = None
        
    def get_companion_id(self):
        """Get the first companion ID"""
        response = requests.get(f"{self.api_url}/companions")
        if response.status_code == 200:
            companions = response.json()
            if companions:
                self.companion_id = companions[0]['_id']
                print(f"Using companion: {companions[0]['name']} (ID: {self.companion_id})")
                return True
        return False
    
    def send_message(self, message, session_id):
        """Send a message and return the response"""
        data = {
            "companion_id": self.companion_id,
            "message": message,
            "session_id": session_id
        }
        
        response = requests.post(f"{self.api_url}/chat", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error sending message: {response.status_code}")
            return None
    
    def test_memory_functionality(self):
        """Test that memory works across multiple messages"""
        print("\n🧠 Testing Memory Functionality")
        print("=" * 40)
        
        if not self.get_companion_id():
            print("❌ Failed to get companion ID")
            return False
        
        session_id = f"memory_test_{datetime.now().strftime('%H%M%S')}"
        print(f"Session ID: {session_id}")
        
        # Send multiple messages to build conversation history
        messages = [
            "Hello, my name is John",
            "I like reading books",
            "What's my name?",
            "What do I like to do?",
            "Tell me about our conversation so far"
        ]
        
        thread_lengths = []
        
        for i, message in enumerate(messages, 1):
            print(f"\n📝 Message {i}: {message}")
            
            response = self.send_message(message, session_id)
            if response:
                reply = response.get('reply', '')
                thread = response.get('thread', [])
                thread_lengths.append(len(thread))
                
                print(f"   Reply: {reply}")
                print(f"   Thread length: {len(thread)} messages")
                
                # Verify thread is growing
                if len(thread) == i * 2:  # Each exchange adds 2 messages (user + assistant)
                    print(f"   ✅ Thread length correct ({len(thread)} messages)")
                else:
                    print(f"   ❌ Expected {i * 2} messages, got {len(thread)}")
                
                # Small delay between messages
                time.sleep(1)
            else:
                print("   ❌ Failed to get response")
                return False
        
        print(f"\n📊 Thread growth: {thread_lengths}")
        return True
    
    def test_session_isolation(self):
        """Test that different sessions don't share memory"""
        print("\n🔒 Testing Session Isolation")
        print("=" * 40)
        
        if not self.companion_id:
            if not self.get_companion_id():
                print("❌ Failed to get companion ID")
                return False
        
        # Session 1
        session1 = f"session1_{datetime.now().strftime('%H%M%S')}"
        print(f"Session 1 ID: {session1}")
        
        response1 = self.send_message("My favorite color is blue", session1)
        if response1:
            print(f"Session 1 reply: {response1.get('reply', '')}")
            print(f"Session 1 thread length: {len(response1.get('thread', []))}")
        
        time.sleep(1)
        
        # Session 2 - should not know about blue color
        session2 = f"session2_{datetime.now().strftime('%H%M%S')}"
        print(f"\nSession 2 ID: {session2}")
        
        response2 = self.send_message("What's my favorite color?", session2)
        if response2:
            print(f"Session 2 reply: {response2.get('reply', '')}")
            print(f"Session 2 thread length: {len(response2.get('thread', []))}")
            
            # Session 2 should only have 2 messages (user question + assistant reply)
            if len(response2.get('thread', [])) == 2:
                print("✅ Session isolation working - new session has fresh thread")
                return True
            else:
                print("❌ Session isolation failed - thread has unexpected length")
                return False
        
        return False
    
    def test_20_message_limit(self):
        """Test that memory is limited to 20 messages"""
        print("\n📏 Testing 20-Message Memory Limit")
        print("=" * 40)
        
        if not self.companion_id:
            if not self.get_companion_id():
                print("❌ Failed to get companion ID")
                return False
        
        session_id = f"limit_test_{datetime.now().strftime('%H%M%S')}"
        print(f"Session ID: {session_id}")
        
        # Send 12 messages (24 total with replies) to exceed 20 message limit
        for i in range(1, 13):
            message = f"This is message number {i}"
            print(f"Sending message {i}...")
            
            response = self.send_message(message, session_id)
            if response:
                thread = response.get('thread', [])
                print(f"   Thread length: {len(thread)}")
                
                # After 10 exchanges (20 messages), it should stay at 20
                if i >= 10 and len(thread) > 20:
                    print(f"   ❌ Thread exceeded 20 messages: {len(thread)}")
                    return False
            else:
                print(f"   ❌ Failed to send message {i}")
                return False
            
            time.sleep(0.5)  # Small delay
        
        print("✅ Memory limit test completed")
        return True

def main():
    print("🧠 Starting Memory System Tests")
    print("=" * 50)
    
    tester = MemoryTester()
    
    # Run memory tests
    tests = [
        tester.test_memory_functionality,
        tester.test_session_isolation,
        tester.test_20_message_limit,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Memory Tests Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All memory tests passed!")
        return 0
    else:
        print("❌ Some memory tests failed!")
        return 1

if __name__ == "__main__":
    main()