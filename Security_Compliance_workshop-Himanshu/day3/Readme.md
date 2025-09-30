# My Secure CI/CD Pipeline Project - Day 3 

For this project, I built a complete DevSecOps pipeline from scratch using GitHub Actions. The goal was to automatically scan a Python web application for security flaws every time I pushed new code. I integrated several industry-standard tools to find different kinds of vulnerabilities.

## The Test Application

To make sure my pipeline worked, I started with a simple Python Flask app that I intentionally made insecure. It had a few common problems built right in:

*   **A hardcoded secret key** just sitting in the code.
*   **A command injection vulnerability** using the risky `os.popen` function.
*   **A Cross-Site Scripting (XSS) flaw** where user input wasn't properly cleaned.
*   **An old, vulnerable library** in the `requirements.txt` file.
*   The app was also set to **run in debug mode**, which can leak information.

## My Automated Security Pipeline

The heart of this project is the GitHub Actions workflow file at `.github/workflows/security_scan.yml`. It's set up to run three jobs in parallel every time code is pushed:

1.  **`sast_scans` (Static Analysis):** This job looks at the code without even running it.
    *   **Bandit:** A tool specifically for Python that finds common security mistakes.
    *   **Semgrep:** A more advanced tool that I configured with rules to find deeper bugs like injection flaws and XSS. Its results show up right in GitHub's "Security" tab.

2.  **`secrets_scan` (Secret Scanning):**
    *   **Gitleaks:** This tool is a bloodhound for secrets. I set it up to scan my entire project's history to make sure no passwords or API keys were ever accidentally committed.

3.  **`dast_scan` (Dynamic Analysis):** This is where things get cool. The pipeline actually starts my Flask app on a temporary server.
    *   **OWASP ZAP:** Then, it unleashes ZAP to attack the live application, just like a real hacker would. It checks for runtime issues like missing security headers and server misconfigurations.

## A Closer Look at the Vulnerabilities

### 1. Hardcoded Secret Key
*   **Why it's bad:** If anyone gets a copy of this code, they get the keys to the kingdom. A leaked secret can lead to a total compromise of the application and its data.
*   **The fix:** Simple—never put secrets in code. The right way is to use a secret manager (like GitHub Secrets for a pipeline) and load them as environment variables when the app starts.

### 2. Command Injection
*   **Why it's bad:** This is a classic "game over" vulnerability. It lets an attacker run commands on the server itself. They could steal data, shut down the server, or use it to attack other systems.
*   **The fix:** Never, ever trust user input enough to execute it as a command. If I had to run system commands, I would use Python's `subprocess` module safely, without the `shell=True` option.

## Proof That I Fixed It

Talk is cheap, so I fixed the two biggest issues: the hardcoded secret and the command injection.

1.  **The Fix:** I removed the secret key from the code and replaced the `os.popen` call with safe code.
2.  **The Rerun:** I pushed these changes, and the pipeline automatically ran again.
3.  **The Result:** The new reports showed that my fixes worked.

### Gitleaks Report After Fix
![Gitleaks Report After Fix](./screenshots/gitleaks-after-fix.png)
*   The Gitleaks report is now clean. The secret is gone.

### Semgrep Report After Fix
![Semgrep Report After Fix](./screenshots/semgrep-after-fix.png)
*   The "Command injection" alert in the GitHub Security tab was automatically closed, confirming the fix.

## Answering the Core Questions

### My take on SAST vs. DAST vs. Secrets Scanning...

*   **SAST** is like proofreading my code for security errors before it's even compiled or run.
*   **DAST** is like hiring a friendly hacker to test the doors and windows of my application while it's running.
*   **Secrets Scanning** is like having a security guard who only checks for one thing: making sure I never accidentally leave my keys and passwords lying around in the code.
You need all three because they find different types of problems, giving you a much more complete security picture.

### Why is putting secrets in code a terrible idea?

Because code is meant to be copied, shared, and stored in places like Git. Once a secret is in your Git history, it's very hard to truly delete. If the code ever leaks, the secret leaks with it. The only safe way is to keep secrets completely separate from code, using a vault or environment variables.

### How does this pipeline "Shift Security Left"?

"Shifting left" just means dealing with security as early as possible. My pipeline does this perfectly. I get instant security feedback *while I'm coding*, not weeks later from a security team. This means I can fix bugs when they're cheap and easy to fix, and it helps me learn to write more secure code in the first place.

### What do I do when a scan fails?

1.  **Check the report.** I'd open the failed pipeline run and look at the logs or download the report artifact to see exactly what the problem is.
2.  **Understand the risk.** I'd figure out if it's a real threat or a false positive.
3.  **Fix the code.** I'd write the code to fix the vulnerability.
4.  **Commit and push.** I'd push my fix, which automatically triggers a new scan.
5.  **Confirm the fix.** I'd check the new pipeline results to make sure the alert is gone.