#!/usr/bin/env python
"""
Automated Issue Reporter
Collects system information and error logs for troubleshooting
"""
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime

def collect_system_info():
    """Collect system information"""
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Python Version": sys.version,
        "Platform": platform.platform(),
        "Architecture": platform.machine(),
    }

    # Check Git
    try:
        git_version = subprocess.check_output(["git", "--version"], text=True).strip()
        info["Git"] = git_version
    except:
        info["Git"] = "Not found"

    # Check Node
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        info["Node.js"] = node_version
    except:
        info["Node.js"] = "Not found"

    # Check npm
    try:
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        info["npm"] = npm_version
    except:
        info["npm"] = "Not found"

    return info

def collect_setup_status():
    """Check setup status"""
    status = {}

    # Check venv
    venv_path = Path("venv")
    status["Virtual Environment"] = "Exists" if venv_path.exists() else "Not created"

    # Check node_modules
    node_modules = Path("node_modules")
    status["Node Modules"] = "Installed" if node_modules.exists() else "Not installed"

    # Check .env
    env_file = Path(".env")
    status[".env File"] = "Exists" if env_file.exists() else "Not created"

    # Check data directories
    data_dirs = ["data/uploads", "data/iate", "backups/sqlite", "backups/neo4j"]
    missing_dirs = [d for d in data_dirs if not Path(d).exists()]
    status["Data Directories"] = "All present" if not missing_dirs else f"Missing: {', '.join(missing_dirs)}"

    return status

def collect_python_packages():
    """List installed Python packages"""
    try:
        if Path("venv").exists():
            pip_path = "venv/Scripts/pip" if platform.system() == "Windows" else "venv/bin/pip"
            packages = subprocess.check_output([pip_path, "list"], text=True)
            return packages
        else:
            return "Virtual environment not created"
    except Exception as e:
        return f"Error collecting packages: {e}"

def collect_error_logs():
    """Collect recent error logs if any"""
    logs = []

    # Check for npm error logs
    npm_log = Path("npm-debug.log")
    if npm_log.exists():
        logs.append(("npm-debug.log", npm_log.read_text()[:1000]))

    # Check for Python error logs
    # Add more log locations as needed

    return logs

def generate_issue_report():
    """Generate a comprehensive issue report"""
    report = []

    report.append("# Issue Report")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Repository**: https://github.com/developer-hhiotsystems/terminology-extraction")

    # System Information
    report.append("\n## System Information\n")
    system_info = collect_system_info()
    for key, value in system_info.items():
        report.append(f"- **{key}**: {value}")

    # Setup Status
    report.append("\n## Setup Status\n")
    setup_status = collect_setup_status()
    for key, value in setup_status.items():
        report.append(f"- **{key}**: {value}")

    # Python Packages
    report.append("\n## Installed Python Packages\n")
    report.append("```")
    report.append(collect_python_packages())
    report.append("```")

    # Error Logs
    error_logs = collect_error_logs()
    if error_logs:
        report.append("\n## Error Logs\n")
        for log_name, log_content in error_logs:
            report.append(f"\n### {log_name}\n")
            report.append("```")
            report.append(log_content)
            report.append("```")

    # Instructions
    report.append("\n## Steps to Reproduce\n")
    report.append("1. [Describe what you were trying to do]")
    report.append("2. [Describe what command you ran]")
    report.append("3. [Describe what error you got]")

    report.append("\n## Expected Behavior\n")
    report.append("[Describe what you expected to happen]")

    report.append("\n## Actual Behavior\n")
    report.append("[Describe what actually happened]")

    report.append("\n## Additional Context\n")
    report.append("[Add any other context about the problem]")

    return "\n".join(report)

def main():
    print("\n" + "="*70)
    print("  Issue Reporter - Terminology Extraction")
    print("="*70 + "\n")

    print("Collecting system information...")
    report = generate_issue_report()

    # Save to file
    report_file = Path("issue-report.md")
    report_file.write_text(report)

    print(f"\n[OK] Issue report saved to: {report_file.absolute()}")
    print("\n" + "="*70)
    print("Next Steps:")
    print("="*70)
    print("\n1. Review the report: issue-report.md")
    print("2. Add details about your issue:")
    print("   - Steps to reproduce")
    print("   - Expected vs actual behavior")
    print("   - Any error messages")
    print("\n3. Submit to GitHub:")
    print("   - Go to: https://github.com/developer-hhiotsystems/terminology-extraction/issues/new")
    print("   - Copy content from issue-report.md")
    print("   - Add a descriptive title")
    print("   - Click 'Submit new issue'")
    print("\n" + "="*70)
    print("\nOr email the report to your development team.\n")

if __name__ == "__main__":
    main()
