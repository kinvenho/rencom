#!/usr/bin/env python3
"""Test Click's built-in completion"""

import os
import sys
from cli.main import cli

def test_completion():
    # Test if Click's completion works
    os.environ['_RENCOM_COMPLETE'] = 'bash_complete'
    os.environ['COMP_WORDS'] = 'rencom '
    os.environ['COMP_CWORD'] = '1'
    
    # Capture output
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            cli()
    except SystemExit as e:
        pass
    
    stdout_output = stdout_capture.getvalue()
    stderr_output = stderr_capture.getvalue()
    
    print("STDOUT:", repr(stdout_output))
    print("STDERR:", repr(stderr_output))
    
    # Clean up environment
    del os.environ['_RENCOM_COMPLETE']
    del os.environ['COMP_WORDS']
    del os.environ['COMP_CWORD']

if __name__ == '__main__':
    test_completion()