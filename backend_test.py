import requests
import sys
import json
from datetime import datetime

class ThroneCompanionsAPITester:
    def __init__(self, base_url="https://companions-api.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.companion_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        if success:
            if 'ok' in response and response['ok'] is True and 'time' in response:
                print("   ✅ Health endpoint returns correct format")
                return True
            else:
                print("   ❌ Health endpoint missing 'ok' or 'time' fields")
                return False
        return False

    def test_get_companions(self):
        """Test getting companions list"""
        success, response = self.run_test(
            "Get Companions",
            "GET",
            "companions",
            200
        )
        if success:
            if isinstance(response, list):
                print(f"   Found {len(response)} companions")
                expected_names = ["Sophia", "Aurora", "Vanessa"]
                found_names = [comp.get('name') for comp in response]
                
                if len(response) == 3:
                    print("   ✅ Correct number of companions (3)")
                else:
                    print(f"   ❌ Expected 3 companions, found {len(response)}")
                    return False
                
                for name in expected_names:
                    if name in found_names:
                        print(f"   ✅ Found companion: {name}")
                    else:
                        print(f"   ❌ Missing companion: {name}")
                        return False
                
                # Store companion IDs for chat testing
                self.companion_ids = [comp.get('_id') for comp in response if comp.get('_id')]
                print(f"   Stored companion IDs: {self.companion_ids}")
                return True
            else:
                print("   ❌ Response is not a list")
                return False
        return False

    def test_get_single_companion(self):
        """Test getting a single companion"""
        if not self.companion_ids:
            print("   ❌ No companion IDs available for testing")
            return False
        
        companion_id = self.companion_ids[0]
        success, response = self.run_test(
            f"Get Single Companion ({companion_id})",
            "GET",
            f"companions/{companion_id}",
            200
        )
        if success:
            required_fields = ['_id', 'name', 'slug', 'short_bio']
            for field in required_fields:
                if field in response:
                    print(f"   ✅ Has required field: {field}")
                else:
                    print(f"   ❌ Missing required field: {field}")
                    return False
            return True
        return False

    def test_chat_functionality(self):
        """Test chat functionality"""
        if not self.companion_ids:
            print("   ❌ No companion IDs available for testing")
            return False
        
        companion_id = self.companion_ids[0]
        session_id = f"test_session_{datetime.now().strftime('%H%M%S')}"
        test_message = "Hello, how are you today?"
        
        chat_data = {
            "companion_id": companion_id,
            "message": test_message,
            "session_id": session_id
        }
        
        success, response = self.run_test(
            "Chat with Companion",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        
        if success:
            if 'reply' in response and 'thread' in response:
                print("   ✅ Chat response has 'reply' and 'thread' fields")
                
                thread = response.get('thread', [])
                if len(thread) >= 2:  # Should have user message + assistant reply
                    print(f"   ✅ Thread has {len(thread)} messages")
                    
                    # Check if thread has user and assistant messages
                    roles = [msg.get('role') for msg in thread]
                    if 'user' in roles and 'assistant' in roles:
                        print("   ✅ Thread contains both user and assistant messages")
                        return True
                    else:
                        print(f"   ❌ Thread missing user/assistant roles: {roles}")
                        return False
                else:
                    print(f"   ❌ Thread too short: {len(thread)} messages")
                    return False
            else:
                print("   ❌ Chat response missing 'reply' or 'thread' fields")
                return False
        return False

    def test_invalid_companion_chat(self):
        """Test chat with invalid companion ID"""
        invalid_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but non-existent
        session_id = f"test_session_{datetime.now().strftime('%H%M%S')}"
        
        chat_data = {
            "companion_id": invalid_id,
            "message": "Hello",
            "session_id": session_id
        }
        
        success, response = self.run_test(
            "Chat with Invalid Companion",
            "POST",
            "chat",
            404,
            data=chat_data
        )
        return success

    def test_invalid_companion_id_format(self):
        """Test with invalid ObjectId format"""
        success, response = self.run_test(
            "Get Companion with Invalid ID Format",
            "GET",
            "companions/invalid_id",
            400
        )
        return success

def main():
    print("🚀 Starting Throne Companions API Tests")
    print("=" * 50)
    
    # Setup
    tester = ThroneCompanionsAPITester()
    
    # Run all tests
    tests = [
        tester.test_health_endpoint,
        tester.test_get_companions,
        tester.test_get_single_companion,
        tester.test_chat_functionality,
        tester.test_invalid_companion_chat,
        tester.test_invalid_companion_id_format,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())