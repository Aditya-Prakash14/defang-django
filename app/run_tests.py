#!/usr/bin/env python3
"""
Comprehensive test runner for the E-learning Platform
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'defang_sample.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test suites
    test_suites = [
        'users.tests',
        'courses.tests', 
        'quizzes.tests',
        'certificates.tests'
    ]
    
    print("🚀 Running E-learning Platform Test Suite")
    print("=" * 50)
    
    total_failures = 0
    
    for suite in test_suites:
        print(f"\n📋 Running {suite}...")
        failures = test_runner.run_tests([suite])
        total_failures += failures
        
        if failures == 0:
            print(f"✅ {suite} - All tests passed!")
        else:
            print(f"❌ {suite} - {failures} test(s) failed!")
    
    print("\n" + "=" * 50)
    if total_failures == 0:
        print("🎉 All tests passed! The E-learning Platform is ready!")
    else:
        print(f"⚠️  {total_failures} test(s) failed. Please review and fix.")
    
    sys.exit(total_failures)
