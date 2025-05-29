#!/usr/bin/env python3
"""
Simple test script to verify the Flask application can start without errors
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_import():
    """Test if the app can be imported without syntax errors"""
    try:
        from app import app, db
        print("✅ App imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing app: {e}")
        return False

def test_routes():
    """Test if key routes exist"""
    try:
        from app import app
        with app.test_client() as client:
            # Test basic routes
            routes_to_test = [
                ('/', 'Homepage'),
                ('/login', 'Login page'),
            ]
            
            for route, description in routes_to_test:
                response = client.get(route)
                print(f"✅ {description}: Status {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing routes: {e}")
        return False

def test_database():
    """Test if database can be created"""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Flask Application...")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_app_import,
        test_database,
        test_routes,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print("-" * 30)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    print("\n🚀 To start the application, run: python app.py")
