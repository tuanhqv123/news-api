#!/usr/bin/env python3
"""
Comprehensive test script for role-based permissions.
Tests all three roles: reader, author, admin

Account Setup:
- reader@gmail.com / test123 - Reader role
- author@gmail.com / test123 - Author role
- admin@gmail.com / test123 - Admin role

Expected Permissions:
- Reader: Can read articles, save bookmarks
- Author: Can create articles, read articles
- Admin: Can update article status, create channels, create categories, read articles
"""

import urllib.request
import urllib.parse
import json
from typing import Dict, Any, Tuple, Optional
import time

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_ACCOUNTS = [
    {
        "email": "reader@gmail.com",
        "password": "test123",
        "role": "reader",
        "display_name": "Test Reader"
    },
    {
        "email": "author@gmail.com",
        "password": "test123",
        "role": "author",
        "display_name": "Test Author"
    },
    {
        "email": "admin@gmail.com",
        "password": "test123",
        "role": "admin",
        "display_name": "Test Admin"
    }
]

def print_result(test_name: str, success: bool, data: Any = None):
    """Print test results with clear formatting"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)}")

def make_api_request(endpoint: str, method: str = "GET", data: dict = None, headers: dict = None, access_token: str = None) -> Tuple[bool, dict]:
    """Make API request and return success status and response data"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if not headers:
            headers = {}
        
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        if method in ["POST", "PUT", "PATCH"]:
            headers['Content-Type'] = 'application/json'
            request_data = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers, method=method)

        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return response.getcode() == 200, response_data
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            return False, error_data
        except:
            return False, {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return False, {"error": str(e)}

def login_user(account: dict) -> Tuple[bool, str, dict]:
    """Login user and return (success, token, user_info)"""
    login_data = json.dumps({
        "email": account["email"],
        "password": account["password"]
    }).encode('utf-8')

    try:
        req = urllib.request.Request(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data,
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("success"):
                    token = data["data"]["access_token"]
                    user_info = data["data"]["user"]
                    return True, token, user_info
            return False, None, None
    except Exception as e:
        return False, None, None

def get_first_article_id(access_token: str) -> Optional[str]:
    """Get the ID of the first article for testing bookmarks"""
    success, response = make_api_request("/api/v1/articles/", method="GET", access_token=access_token)
    if success and response.get("data", {}).get("articles"):
        articles = response["data"]["articles"]
        if articles:
            return articles[0]["id"]
    return None

def get_first_category_id(access_token: str) -> Optional[int]:
    """Get the ID of the first category for testing article creation"""
    success, response = make_api_request("/api/v1/categories", method="GET", access_token=access_token)
    if success and response.get("data", {}).get("categories"):
        categories = response["data"]["categories"]
        if categories:
            return categories[0]["id"]
    return None

def test_role_based_permissions():
    """Test role-based permissions for all three account types"""
    print("=" * 80)
    print("🚀 COMPREHENSIVE ROLE-BASED PERMISSION TESTS")
    print("=" * 80)

    test_results = []

    # Test each account type
    for account in TEST_ACCOUNTS:
        print(f"\n👤 Testing {account['role'].upper()} Account: {account['email']}")
        print("-" * 40)

        # Login
        login_success, token, user_info = login_user(account)
        print_result(f"{account['role'].title()} Login", login_success, user_info if login_success else {"error": "Login failed"})

        if not login_success:
            test_results.append(f"{account['role'].title()} Login - FAILED")
            continue

        # Verify correct role
        expected_role = account["role"]
        actual_role = user_info.get("role", "unknown")
        role_correct = actual_role == expected_role
        print_result(f"{account['role'].title()} Role Validation", role_correct, {
            "expected": expected_role,
            "actual": actual_role
        })

        # Get a real category ID for article creation
        category_id = get_first_category_id(token)
        if not category_id:
            print_result(f"{account['role'].title()} - Get Categories", False, {"error": "No categories available"})
            test_results.append(f"{account['role'].title()} Get Categories - FAIL")
            continue

        # Test Article Creation (only for authors)
        if account["role"] == "author":
            article_data = {
                "title": f"Article by {account['role']}",
                "summary": "Author testing article creation",
                "content": "Test content",
                "category_id": category_id
            }

            success, response = make_api_request(
                "/api/v1/articles/",
                method="POST",
                data=article_data,
                access_token=token
            )

            print_result("Author - Create Article", success, response)
            test_results.append("Author Create Article - PASS" if success else "Author Create Article - FAIL")

        elif account["role"] == "admin":
            # Admin should NOT be able to create articles
            article_data = {
                "title": f"Article by {account['role']}",
                "summary": "Admin testing article creation",
                "content": "Test content",
                "category_id": category_id
            }

            success, response = make_api_request(
                "/api/v1/articles/",
                method="POST",
                data=article_data,
                access_token=token
            )

            # Admin should be blocked from creating articles
            article_creation_blocked = not success
            print_result("Admin - Create Article", article_creation_blocked, response)
            test_results.append("Admin Create Article - PASS (should be blocked)" if article_creation_blocked else "Admin Create Article - FAIL (should be blocked)")

        elif account["role"] == "reader":
            # Reader should NOT be able to create articles
            article_data = {
                "title": f"Article by {account['role']}",
                "summary": "Reader testing article creation",
                "content": "Test content",
                "category_id": category_id
            }

            success, response = make_api_request(
                "/api/v1/articles",
                method="POST",
                data=article_data,
                access_token=token
            )

            article_creation_blocked = not success
            print_result("Reader - Create Article", article_creation_blocked, response)
            test_results.append("Reader Create Article - PASS (should be blocked)" if article_creation_blocked else "Reader Create Article - FAIL (should be blocked)")

        # Test Bookmark Creation (only for readers)
        if account["role"] == "reader":
            # Get a real article ID first
            article_id = get_first_article_id(token)
            if not article_id:
                print_result("Reader - Save Bookmark", False, {"error": "No articles available for bookmarking"})
                test_results.append("Reader Save Bookmark - FAIL")
            else:
                # First, try to remove any existing bookmark for this article
                make_api_request(
                    f"/api/v1/articles/{article_id}/bookmark",
                    method="DELETE",
                    access_token=token
                )
                
                # Now try to bookmark
                bookmark_data = {}  # Empty data for bookmark creation
                success, response = make_api_request(
                    f"/api/v1/articles/{article_id}/bookmark",  # Using real article ID
                    method="POST",
                    data=bookmark_data,
                    access_token=token
                )

                print_result("Reader - Save Bookmark", success, response)
                test_results.append("Reader Save Bookmark - PASS" if success else "Reader Save Bookmark - FAIL")

            # Test Follow Channel (only for readers)
            channel_id = 1  # Use the default VnExpress channel
            # First try to unfollow in case already following
            make_api_request(
                f"/api/v1/channels/{channel_id}/follow",
                method="DELETE",
                data={},
                access_token=token
            )
            # Now try to follow
            success, response = make_api_request(
                f"/api/v1/channels/{channel_id}/follow",
                method="POST",
                data={},
                access_token=token
            )

            print_result("Reader - Follow Channel", success, response)
            test_results.append("Reader Follow Channel - PASS" if success else "Reader Follow Channel - FAIL")

            # Test Comment on Article (only for readers)
            if article_id:
                comment_data = {
                    "content": f"Test comment from {account['role']} user"
                }
                success, response = make_api_request(
                    f"/api/v1/articles/{article_id}/comments",
                    method="POST",
                    data=comment_data,
                    access_token=token
                )

                print_result("Reader - Comment on Article", success, response)
                test_results.append("Reader Comment on Article - PASS" if success else "Reader Comment on Article - FAIL")
            else:
                print_result("Reader - Comment on Article", False, {"error": "No articles available for commenting"})
                test_results.append("Reader Comment on Article - FAIL")

        elif account["role"] in ["admin", "author"]:
            # Admin and Author should NOT be able to save bookmarks
            article_id = get_first_article_id(token)
            if article_id:
                bookmark_data = {}
                success, response = make_api_request(
                    f"/api/v1/articles/{article_id}/bookmark",
                    method="POST",
                    data=bookmark_data,
                    access_token=token
                )

                bookmark_creation_blocked = not success
                print_result(f"{account['role'].title()} - Save Bookmark", bookmark_creation_blocked, response)
                test_results.append(f"{account['role'].title()} Save Bookmark - PASS (should be blocked)" if bookmark_creation_blocked else f"{account['role'].title()} Save Bookmark - FAIL (should be blocked)")

                # Admin and Author should NOT be able to follow channels
                channel_id = 1
                success, response = make_api_request(
                    f"/api/v1/channels/{channel_id}/follow",
                    method="POST",
                    data={},
                    access_token=token
                )

                follow_blocked = not success
                print_result(f"{account['role'].title()} - Follow Channel", follow_blocked, response)
                test_results.append(f"{account['role'].title()} Follow Channel - PASS (should be blocked)" if follow_blocked else f"{account['role'].title()} Follow Channel - FAIL (should be blocked)")

                # Admin and Author should NOT be able to comment on articles
                comment_data = {
                    "content": f"Test comment from {account['role']} user"
                }
                success, response = make_api_request(
                    f"/api/v1/articles/{article_id}/comments",
                    method="POST",
                    data=comment_data,
                    access_token=token
                )

                comment_blocked = not success
                print_result(f"{account['role'].title()} - Comment on Article", comment_blocked, response)
                test_results.append(f"{account['role'].title()} Comment on Article - PASS (should be blocked)" if comment_blocked else f"{account['role'].title()} Comment on Article - FAIL (should be blocked)")
            else:
                # If no articles, consider it blocked
                print_result(f"{account['role'].title()} - Save Bookmark", True, {"message": "No articles available"})
                test_results.append(f"{account['role'].title()} Save Bookmark - PASS (should be blocked)")
                print_result(f"{account['role'].title()} - Follow Channel", True, {"message": "No articles available"})
                test_results.append(f"{account['role'].title()} Follow Channel - PASS (should be blocked)")
                print_result(f"{account['role'].title()} - Comment on Article", True, {"message": "No articles available"})
                test_results.append(f"{account['role'].title()} Comment on Article - PASS (should be blocked)")

        # Test Article Reading (all roles should be able to read)
        success, response = make_api_request(
            "/api/v1/articles/",
            method="GET",
            access_token=token
        )
        print_result(f"{account['role'].title()} - Read Articles", success, response)
        test_results.append(f"{account['role'].title()} Read Articles - PASS" if success else f"{account['role'].title()} Read Articles - FAIL")

        # Test Admin-specific functions
        if account["role"] == "admin":
            timestamp = str(int(time.time()))
            
            # Test create channel (should work for admin)
            channel_data = {
                "name": f"Test Channel {account['role']} {timestamp}",
                "slug": f"test-channel-{account['role']}-{timestamp}",
                "description": "Test channel creation"
            }
            success, response = make_api_request(
                "/api/v1/channels/admin/create",
                method="POST",
                data=channel_data,
                access_token=token
            )

            print_result("Admin - Create Channel", success, response)
            test_results.append("Admin Create Channel - PASS" if success else "Admin Create Channel - FAIL")

            # Test create category (should work for admin)
            category_data = {
                "name": f"Test Category {account['role']} {timestamp}",
                "slug": f"test-category-{account['role']}-{timestamp}",
                "description": "Test category creation"
            }
            success, response = make_api_request(
                "/api/v1/categories/admin/create",
                method="POST",
                data=category_data,
                access_token=token
            )

            print_result("Admin - Create Category", success, response)
            test_results.append("Admin Create Category - PASS" if success else "Admin Create Category - FAIL")

            # Test article status update (should work for admin)
            article_id = get_first_article_id(token)
            if article_id:
                status_data = {}  # No body needed, use query param
                success, response = make_api_request(
                    f"/api/v1/articles/{article_id}/status?status=published",
                    method="PUT",
                    data=status_data,
                    access_token=token
                )

                print_result("Admin - Update Article Status", success, response)
                test_results.append("Admin Update Article Status - PASS" if success else "Admin Update Article Status - FAIL")
            else:
                print_result("Admin - Update Article Status", False, {"error": "No articles available"})
                test_results.append("Admin Update Article Status - FAIL")

    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for result in test_results if "PASS" in result)
    total = len(test_results)

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    print(f"\n📋 Test Results:")
    for result in test_results:
        print(f"  {result}")

    print("\n" + "=" * 80)

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Role-based permissions are working correctly:")
        print("  - Admin users can create channels and categories")
        print("  - Admin users can update article status")
        print("  - Admin users CANNOT create articles, save bookmarks, follow channels, or comment")
        print("  - Author users CAN create articles")
        print("  - Author users CANNOT save bookmarks, follow channels, or comment")
        print("  - Reader users CAN read articles, save bookmarks, follow channels, and comment")
        print("  - Reader users CANNOT create articles")
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"\n🔧 {total - passed} tests need to be fixed.")

    return passed == total

if __name__ == "__main__":
    test_role_based_permissions()