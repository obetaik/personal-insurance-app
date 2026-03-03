#!/usr/bin/env python
"""
Test runner for backend tests
"""
import pytest
import sys
import os

if __name__ == '__main__':
    # Add the current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with coverage
    args = [
        'tests/',
        '-v',
        '--cov=.',
        '--cov-report=term',
        '--cov-report=html:coverage_report',
        '--cov-config=.coveragerc'
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    sys.exit(pytest.main(args))