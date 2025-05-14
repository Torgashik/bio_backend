import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def generate_test_dashboard(test_results: Dict[str, Any], output_dir: str = "test_reports") -> str:
    """
    Generate an HTML dashboard for test results.
    
    Args:
        test_results: Dictionary containing test results
        output_dir: Directory to save the dashboard
    
    Returns:
        Path to the generated HTML file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate timestamp for the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"test_dashboard_{timestamp}.html"
    
    # Calculate statistics
    total_tests = len(test_results.get("tests", []))
    passed_tests = sum(1 for test in test_results.get("tests", []) if test.get("status") == "passed")
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Results Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold text-gray-800 mb-8">Test Results Dashboard</h1>
            
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-gray-600">Total Tests</h3>
                    <p class="text-3xl font-bold text-gray-800">{total_tests}</p>
                </div>
                <div class="bg-green-100 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-green-600">Passed Tests</h3>
                    <p class="text-3xl font-bold text-green-800">{passed_tests}</p>
                </div>
                <div class="bg-red-100 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-red-600">Failed Tests</h3>
                    <p class="text-3xl font-bold text-red-800">{failed_tests}</p>
                </div>
                <div class="bg-blue-100 rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold text-blue-600">Pass Rate</h3>
                    <p class="text-3xl font-bold text-blue-800">{pass_rate:.1f}%</p>
                </div>
            </div>
            
            <!-- Chart -->
            <div class="bg-white rounded-lg shadow p-6 mb-8">
                <canvas id="testResultsChart" width="400" height="200"></canvas>
            </div>
            
            <!-- Test Results Table -->
            <div class="bg-white rounded-lg shadow overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Test Name</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {generate_test_rows(test_results.get("tests", []))}
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            // Initialize chart
            const ctx = document.getElementById('testResultsChart').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Passed', 'Failed'],
                    datasets: [{{
                        data: [{passed_tests}, {failed_tests}],
                        backgroundColor: ['#10B981', '#EF4444'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Write HTML content to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return str(output_file)

def generate_test_rows(tests: List[Dict[str, Any]]) -> str:
    """Generate HTML rows for test results table."""
    rows = []
    for test in tests:
        status_class = "text-green-600" if test.get("status") == "passed" else "text-red-600"
        status_text = "Passed" if test.get("status") == "passed" else "Failed"
        
        row = f"""
        <tr>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{test.get("name", "")}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm {status_class}">{status_text}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{test.get("duration", "0.00")}s</td>
            <td class="px-6 py-4 text-sm text-gray-500">
                {format_test_details(test)}
            </td>
        </tr>
        """
        rows.append(row)
    
    return "\n".join(rows)

def format_test_details(test: Dict[str, Any]) -> str:
    """Format test details for display."""
    details = []
    
    if test.get("error"):
        details.append(f'<div class="text-red-600">{test["error"]}</div>')
    
    if test.get("warnings"):
        details.append('<div class="text-yellow-600">')
        for warning in test["warnings"]:
            details.append(f'<div>{warning}</div>')
        details.append('</div>')
    
    return "\n".join(details) if details else "No additional details" 