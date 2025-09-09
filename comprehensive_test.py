import requests
import json
from datetime import datetime
import time

class ComprehensiveThroneTester:
    def __init__(self, base_url="https://companions-api.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.companion_ids = []
        self.test_results = {
            'backend_api': {},
            'memory_system': {},
            'fallback_responses': {},
            'session_isolation': {}
        }
        
    def log_result(self, category, test_name, passed, details=""):
        """Log test result"""
        self.test_results[category][test_name] = {
            'passed': passed,
            'details': details
        }
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}: {details}")
    
    def test_backend_apis(self):
        """Test all backend API endpoints"""
        print("\n🔧 TESTING BACKEND APIs")
        print("=" * 40)
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                passed = 'ok' in data and data['ok'] is True
                self.log_result('backend_api', 'Health Endpoint', passed, 
                              f"Status: {response.status_code}, Response: {data}")
            else:
                self.log_result('backend_api', 'Health Endpoint', False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result('backend_api', 'Health Endpoint', False, f"Error: {str(e)}")
        
        # Test companions endpoint
        try:
            response = requests.get(f"{self.api_url}/companions", timeout=10)
            if response.status_code == 200:
                companions = response.json()
                expected_names = ["Sophia", "Aurora", "Vanessa"]
                found_names = [c.get('name') for c in companions]
                
                passed = (len(companions) == 3 and 
                         all(name in found_names for name in expected_names))
                
                if passed:
                    self.companion_ids = [c.get('_id') for c in companions]
                
                self.log_result('backend_api', 'Get Companions', passed,
                              f"Found {len(companions)} companions: {found_names}")
            else:
                self.log_result('backend_api', 'Get Companions', False,
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result('backend_api', 'Get Companions', False, f"Error: {str(e)}")
        
        # Test single companion endpoint
        if self.companion_ids:
            try:
                companion_id = self.companion_ids[0]
                response = requests.get(f"{self.api_url}/companions/{companion_id}", timeout=10)
                passed = response.status_code == 200
                details = f"Status: {response.status_code}"
                if passed:
                    data = response.json()
                    details += f", Name: {data.get('name')}"
                
                self.log_result('backend_api', 'Get Single Companion', passed, details)
            except Exception as e:
                self.log_result('backend_api', 'Get Single Companion', False, f"Error: {str(e)}")
    
    def test_chat_functionality(self):
        """Test chat endpoint and fallback responses"""
        print("\n💬 TESTING CHAT FUNCTIONALITY")
        print("=" * 40)
        
        if not self.companion_ids:
            self.log_result('fallback_responses', 'Chat Test', False, "No companion IDs available")
            return
        
        companion_id = self.companion_ids[0]
        session_id = f"test_{datetime.now().strftime('%H%M%S')}"
        
        # Test basic chat
        try:
            chat_data = {
                "companion_id": companion_id,
                "message": "Hello, how are you?",
                "session_id": session_id
            }
            
            response = requests.post(f"{self.api_url}/chat", json=chat_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')
                thread = data.get('thread', [])
                
                # Check for fallback message (since no API key is set)
                fallback_indicators = [
                    "deeper voice isn't unlocked",
                    "I'm here, but my deeper voice",
                    "Ask me anything"
                ]
                
                has_fallback = any(indicator in reply for indicator in fallback_indicators)
                
                self.log_result('fallback_responses', 'Fallback Message', has_fallback,
                              f"Reply: {reply[:100]}...")
                
                # Check thread structure
                thread_valid = (len(thread) >= 2 and 
                              any(msg.get('role') == 'user' for msg in thread) and
                              any(msg.get('role') == 'assistant' for msg in thread))
                
                self.log_result('backend_api', 'Chat Response Structure', thread_valid,
                              f"Thread length: {len(thread)}, Has user/assistant roles: {thread_valid}")
                
            else:
                self.log_result('fallback_responses', 'Chat Request', False,
                              f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result('fallback_responses', 'Chat Request', False, f"Error: {str(e)}")
    
    def test_memory_system(self):
        """Test conversation memory functionality"""
        print("\n🧠 TESTING MEMORY SYSTEM")
        print("=" * 40)
        
        if not self.companion_ids:
            self.log_result('memory_system', 'Memory Test', False, "No companion IDs available")
            return
        
        companion_id = self.companion_ids[0]
        session_id = f"memory_{datetime.now().strftime('%H%M%S')}"
        
        # Send multiple messages to test memory
        messages = [
            "My name is Alice",
            "I work as a teacher",
            "I love reading books",
            "What's my name?",
            "What do I do for work?"
        ]
        
        thread_lengths = []
        
        try:
            for i, message in enumerate(messages, 1):
                chat_data = {
                    "companion_id": companion_id,
                    "message": message,
                    "session_id": session_id
                }
                
                response = requests.post(f"{self.api_url}/chat", json=chat_data, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    thread = data.get('thread', [])
                    thread_lengths.append(len(thread))
                    
                    print(f"   Message {i}: Thread length = {len(thread)}")
                    time.sleep(1)  # Small delay between messages
                else:
                    self.log_result('memory_system', f'Message {i}', False,
                                  f"Status: {response.status_code}")
                    return
            
            # Check if thread is growing correctly
            memory_working = all(thread_lengths[i] > thread_lengths[i-1] 
                               for i in range(1, len(thread_lengths)))
            
            self.log_result('memory_system', 'Thread Growth', memory_working,
                          f"Thread lengths: {thread_lengths}")
            
            # Check final thread length
            final_length = thread_lengths[-1] if thread_lengths else 0
            expected_length = len(messages) * 2  # Each exchange = user + assistant message
            
            self.log_result('memory_system', 'Final Thread Length', 
                          final_length == expected_length,
                          f"Expected: {expected_length}, Got: {final_length}")
            
        except Exception as e:
            self.log_result('memory_system', 'Memory Test', False, f"Error: {str(e)}")
    
    def test_session_isolation(self):
        """Test that different sessions don't share memory"""
        print("\n🔒 TESTING SESSION ISOLATION")
        print("=" * 40)
        
        if not self.companion_ids:
            self.log_result('session_isolation', 'Session Test', False, "No companion IDs available")
            return
        
        companion_id = self.companion_ids[0]
        
        try:
            # Session 1
            session1 = f"session1_{datetime.now().strftime('%H%M%S')}"
            chat_data1 = {
                "companion_id": companion_id,
                "message": "My favorite color is red",
                "session_id": session1
            }
            
            response1 = requests.post(f"{self.api_url}/chat", json=chat_data1, timeout=15)
            
            if response1.status_code != 200:
                self.log_result('session_isolation', 'Session 1', False, 
                              f"Status: {response1.status_code}")
                return
            
            thread1_length = len(response1.json().get('thread', []))
            
            time.sleep(1)
            
            # Session 2 - should not know about red color
            session2 = f"session2_{datetime.now().strftime('%H%M%S')}"
            chat_data2 = {
                "companion_id": companion_id,
                "message": "What's my favorite color?",
                "session_id": session2
            }
            
            response2 = requests.post(f"{self.api_url}/chat", json=chat_data2, timeout=15)
            
            if response2.status_code == 200:
                thread2_length = len(response2.json().get('thread', []))
                
                # Session 2 should have fresh thread (only 2 messages)
                isolation_working = thread2_length == 2
                
                self.log_result('session_isolation', 'Different Sessions', isolation_working,
                              f"Session1 thread: {thread1_length}, Session2 thread: {thread2_length}")
            else:
                self.log_result('session_isolation', 'Session 2', False,
                              f"Status: {response2.status_code}")
                
        except Exception as e:
            self.log_result('session_isolation', 'Session Isolation', False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            print(f"\n🔸 {category.upper().replace('_', ' ')}:")
            for test_name, result in tests.items():
                total_tests += 1
                if result['passed']:
                    passed_tests += 1
                    print(f"   ✅ {test_name}")
                else:
                    print(f"   ❌ {test_name}: {result['details']}")
        
        print(f"\n📈 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! The Throne Companions upgrade is working perfectly!")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Review needed.")
        
        return passed_tests, total_tests

def main():
    print("🚀 COMPREHENSIVE THRONE COMPANIONS TESTING")
    print("Testing upgraded LLM-ready chat system with memory functionality")
    print("=" * 60)
    
    tester = ComprehensiveThroneTester()
    
    # Run all test suites
    tester.test_backend_apis()
    tester.test_chat_functionality()
    tester.test_memory_system()
    tester.test_session_isolation()
    
    # Print summary
    passed, total = tester.print_summary()
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())