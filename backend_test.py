import requests
import sys
import json
from datetime import datetime

class AICompanionsAPITester:
    def __init__(self, base_url="https://avatar-refresh.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_companions = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
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
                    if isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: Found {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

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
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_get_companions(self):
        """Test getting all companions"""
        success, response = self.run_test(
            "Get All Companions",
            "GET",
            "companions",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} companions")
            for companion in response:
                print(f"   - {companion.get('name', 'Unknown')} ({companion.get('slug', 'no-slug')})")
            self.test_companions = response
            
            # Check if we have the expected companions
            expected_companions = ['sophia', 'aurora', 'vanessa']
            found_slugs = [c.get('slug') for c in response]
            missing = [slug for slug in expected_companions if slug not in found_slugs]
            if missing:
                print(f"   ⚠️  Missing expected companions: {missing}")
            else:
                print(f"   ✅ All expected companions found")
        
        return success

    def test_get_individual_companions(self):
        """Test getting individual companions"""
        test_slugs = ['sophia', 'aurora', 'vanessa']
        all_passed = True
        
        for slug in test_slugs:
            success, response = self.run_test(
                f"Get Companion: {slug}",
                "GET",
                f"companions/{slug}",
                200
            )
            if success and isinstance(response, dict):
                print(f"   Name: {response.get('name')}")
                print(f"   Bio: {response.get('short_bio', '')[:50]}...")
                print(f"   Traits: {response.get('traits', [])}")
            all_passed = all_passed and success
        
        return all_passed

    def test_invalid_companion(self):
        """Test getting a non-existent companion"""
        success, response = self.run_test(
            "Get Invalid Companion",
            "GET",
            "companions/nonexistent",
            404
        )
        return success

    def test_chat_functionality(self):
        """Test chat functionality with each companion"""
        test_slugs = ['sophia', 'aurora', 'vanessa']
        all_passed = True
        
        for slug in test_slugs:
            success, response = self.run_test(
                f"Chat with {slug}",
                "POST",
                f"chat/{slug}",
                200,
                data={"message": f"Hello {slug}, how are you today?"}
            )
            
            if success and isinstance(response, dict):
                print(f"   User message: {response.get('user_message', '')[:50]}...")
                print(f"   Companion response: {response.get('companion_response', '')[:100]}...")
                print(f"   Message ID: {response.get('id')}")
            
            all_passed = all_passed and success
        
        return all_passed

    def test_chat_invalid_companion(self):
        """Test chat with non-existent companion"""
        success, response = self.run_test(
            "Chat with Invalid Companion",
            "POST",
            "chat/nonexistent",
            404,
            data={"message": "Hello"}
        )
        return success

    def test_create_companion(self):
        """Test creating a new companion"""
        test_companion = {
            "name": "TestBot",
            "slug": "testbot",
            "short_bio": "A test companion for API testing",
            "long_backstory": "This is a test companion created during API testing to verify CRUD operations work correctly.",
            "traits": ["helpful", "testing", "temporary"],
            "avatar_path": "/avatars/testbot.jpg"
        }
        
        success, response = self.run_test(
            "Create New Companion",
            "POST",
            "companions",
            200,
            data=test_companion
        )
        
        if success:
            print(f"   Created companion: {response.get('name')} with slug: {response.get('slug')}")
        
        return success

    def test_update_companion(self):
        """Test updating a companion"""
        update_data = {
            "short_bio": "Updated test companion bio",
            "traits": ["helpful", "testing", "updated"]
        }
        
        success, response = self.run_test(
            "Update Companion",
            "PUT",
            "companions/testbot",
            200,
            data=update_data
        )
        
        if success:
            print(f"   Updated bio: {response.get('short_bio')}")
            print(f"   Updated traits: {response.get('traits')}")
        
        return success

    def test_delete_companion(self):
        """Test deleting a companion"""
        success, response = self.run_test(
            "Delete Test Companion",
            "DELETE",
            "companions/testbot",
            200
        )
        
        if success:
            print(f"   Delete response: {response.get('message')}")
        
        return success

def main():
    print("🚀 Starting AI Companions API Testing...")
    print("=" * 60)
    
    tester = AICompanionsAPITester()
    
    # Test sequence
    tests = [
        ("Root API Endpoint", tester.test_root_endpoint),
        ("Get All Companions", tester.test_get_companions),
        ("Get Individual Companions", tester.test_get_individual_companions),
        ("Get Invalid Companion (404)", tester.test_invalid_companion),
        ("Chat Functionality", tester.test_chat_functionality),
        ("Chat Invalid Companion (404)", tester.test_chat_invalid_companion),
        ("Create New Companion", tester.test_create_companion),
        ("Update Companion", tester.test_update_companion),
        ("Delete Companion", tester.test_delete_companion),
    ]
    
    print(f"\n📋 Running {len(tests)} test categories...")
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test category failed with exception: {str(e)}")
    
    # Print final results
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())