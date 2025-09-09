import requests
import sys
from datetime import datetime
import json
import uuid

class ThroneCompanionsAPITester:
    def __init__(self, base_url="https://throne-root.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_companion_id = None
        self.session_id = f"test_session_{uuid.uuid4().hex[:8]}"

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if len(str(response_data)) > 500:
                        print(f"   Response: [Large response - {len(str(response_data))} chars]")
                    else:
                        print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    print(f"   Response: {response.text}")
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error Response: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_status_get(self):
        """Test getting status checks"""
        return self.run_test("Get Status Checks", "GET", "status", 200)

    def test_status_post(self):
        """Test creating a status check"""
        test_data = {
            "client_name": f"test_client_{datetime.now().strftime('%H%M%S')}"
        }
        return self.run_test("Create Status Check", "POST", "status", 200, test_data)

    def test_get_companions(self):
        """Test getting all companions"""
        success, data = self.run_test("Get All Companions", "GET", "companions", 200)
        if success and isinstance(data, list):
            print(f"   Found {len(data)} companions")
            if len(data) > 0:
                print(f"   Sample companion: {data[0].get('name', 'Unknown')}")
        return success, data

    def test_create_companion(self):
        """Test creating a new companion"""
        test_data = {
            "name": f"TestBot_{datetime.now().strftime('%H%M%S')}",
            "short_bio": "A test companion for API testing",
            "long_backstory": "This is a detailed backstory for our test companion. It has been created specifically for testing the API endpoints and ensuring everything works correctly.",
            "traits": ["Helpful", "Testing", "Reliable", "Friendly"]
        }
        success, data = self.run_test("Create New Companion", "POST", "companions", 200, test_data)
        if success and isinstance(data, dict):
            self.created_companion_id = data.get('id')
            print(f"   Created companion with ID: {self.created_companion_id}")
        return success, data

    def test_get_specific_companion(self):
        """Test getting a specific companion by ID"""
        if not self.created_companion_id:
            print("❌ Skipping - No companion ID available")
            return False, {}
        
        return self.run_test("Get Specific Companion", "GET", f"companions/{self.created_companion_id}", 200)

    def test_update_companion(self):
        """Test updating a companion"""
        if not self.created_companion_id:
            print("❌ Skipping - No companion ID available")
            return False, {}
        
        update_data = {
            "short_bio": "Updated test companion for API testing",
            "traits": ["Helpful", "Testing", "Reliable", "Updated"]
        }
        return self.run_test("Update Companion", "PUT", f"companions/{self.created_companion_id}", 200, update_data)

    def test_chat_with_companion(self):
        """Test sending a chat message to a companion"""
        if not self.created_companion_id:
            print("❌ Skipping - No companion ID available")
            return False, {}
        
        chat_data = {
            "companion_id": self.created_companion_id,
            "message": "Hello! This is a test message from the API test suite.",
            "session_id": self.session_id
        }
        return self.run_test("Send Chat Message", "POST", "chat", 200, chat_data)

    def test_get_chat_history(self):
        """Test getting chat history for a companion"""
        if not self.created_companion_id:
            print("❌ Skipping - No companion ID available")
            return False, {}
        
        params = {"session_id": self.session_id}
        success, data = self.run_test("Get Chat History", "GET", f"chat/{self.created_companion_id}", 200, params=params)
        if success and isinstance(data, list):
            print(f"   Found {len(data)} messages in chat history")
        return success, data

    def test_delete_companion(self):
        """Test deleting a companion"""
        if not self.created_companion_id:
            print("❌ Skipping - No companion ID available")
            return False, {}
        
        return self.run_test("Delete Companion", "DELETE", f"companions/{self.created_companion_id}", 200)

    def test_seeded_companions(self):
        """Test that seeded companions exist and are accessible"""
        success, companions = self.test_get_companions()
        if not success:
            return False, {}
        
        expected_names = ["Sophia", "Nova", "Zara"]
        found_names = [c.get('name') for c in companions if isinstance(c, dict)]
        
        print(f"\n🔍 Checking Seeded Companions...")
        for name in expected_names:
            if name in found_names:
                print(f"✅ Found seeded companion: {name}")
            else:
                print(f"❌ Missing seeded companion: {name}")
        
        # Test chatting with a seeded companion if available
        if companions and len(companions) > 0:
            seeded_companion = companions[0]
            seeded_id = seeded_companion.get('id')
            if seeded_id:
                print(f"\n🔍 Testing chat with seeded companion: {seeded_companion.get('name')}")
                chat_data = {
                    "companion_id": seeded_id,
                    "message": "Hello! Testing chat with seeded companion.",
                    "session_id": self.session_id
                }
                self.run_test("Chat with Seeded Companion", "POST", "chat", 200, chat_data)
        
        return True, companions

def main():
    print("🚀 Starting Throne Companions API Tests")
    print("=" * 50)
    
    # Setup
    tester = ThroneCompanionsAPITester()
    
    # Test basic connectivity first
    print(f"Testing API at: {tester.api_url}")
    
    # Run basic tests
    print("\n📋 BASIC API TESTS")
    print("-" * 30)
    tester.test_root_endpoint()
    tester.test_status_get()
    tester.test_status_post()
    
    # Test companion functionality
    print("\n👥 COMPANION API TESTS")
    print("-" * 30)
    tester.test_seeded_companions()
    tester.test_create_companion()
    tester.test_get_specific_companion()
    tester.test_update_companion()
    
    # Test chat functionality
    print("\n💬 CHAT API TESTS")
    print("-" * 30)
    tester.test_chat_with_companion()
    tester.test_get_chat_history()
    
    # Cleanup - delete test companion
    print("\n🧹 CLEANUP TESTS")
    print("-" * 30)
    tester.test_delete_companion()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All API tests passed!")
        return 0
    else:
        print("⚠️  Some API tests failed")
        failed_count = tester.tests_run - tester.tests_passed
        print(f"   {failed_count} test(s) failed out of {tester.tests_run}")
        return 1

if __name__ == "__main__":
    sys.exit(main())