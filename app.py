from flask import Flask, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/run-tests', methods=['GET'])
def run_tests():
    try:
        # Run pytest and capture the output, including all tests
        result = subprocess.run(
            [r'C:\Users\ragha\AppData\Roaming\Python\Python312\Scripts\pytest.exe', 'test_period_tracker.py', '--tb=short', '--maxfail=10', '--capture=no'],
            capture_output=True,
            text=True
        )
        
        # Get the full output of the test run
        output = result.stdout + "\n" + result.stderr  # Capture both stdout and stderr
        
        # Initialize the test summary
        test_summary = "📝 Test Summary:\n"
        
        # Regular expression to match the test names and their statuses
        import re
        test_pattern = re.compile(r'^(.*) (PASSED|FAILED|SKIPPED|xfailed)$')
        
        # Process each line from pytest output and look for passed/failed tests
        for line in output.splitlines():
            match = test_pattern.match(line.strip())
            if match:
                test_name, test_status = match.groups()
                if test_status == "PASSED":
                    test_summary += f"✅ {test_name} - Passed\n"
                elif test_status == "FAILED":
                    test_summary += f"❌ {test_name} - Failed\n"
                elif test_status == "SKIPPED":
                    test_summary += f"⚠️ {test_name} - Skipped\n"
                elif test_status == "xfailed":
                    test_summary += f"❌ {test_name} - Expected Fail\n"
        
        # Return the full test report to frontend
        return jsonify({'report': test_summary})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
