import subprocess
import sys


def main():
    print("--- Step 1: Running System Checks ---")
    # sys.executable ensures it uses your exact (teacareai) virtual environment
    check_process = subprocess.run([sys.executable, "check_constraints.py"])

    # If check_constraints.py exits with sys.exit(1), stop everything.
    if check_process.returncode != 0:
        print("\n[ERROR] Pre-flight checks failed. Halting startup.")
        sys.exit(1)

    print("\n--- Step 2: Starting TeaCareAI Server ---")
    # If checks pass, start the Flask app
    subprocess.run([sys.executable, "app.py"])


if __name__ == "__main__":
    main()