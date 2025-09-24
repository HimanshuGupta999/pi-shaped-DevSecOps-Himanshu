# Day 1: Code Security & Shift-Left Practices ( Aman )

This is my write-up for the Day 1 assignment. I'll walk you through how I set up a security scan, found hardcoded secrets, completely removed them from my project's history, and then got the application running securely in a Docker container.

---

## 1. Setting Up and Running Gitleaks

My first step was to scan the repository for secrets. Since I'm on a Linux machine, I couldn't use Homebrew, so I installed the Gitleaks binary directly.

Once it was installed, I ran it from the root of my project with the `--verbose` flag to get all the details:

```bash
gitleaks detect --verbose
```
As expected, it immediately found the hardcoded GitHub token and database details I had placed in the `app.py` file.

---

## 2. The Cleanup Process: Removing Secrets for Good

Once Gitleaks found the secrets, the real work began. Just deleting them wasn't enough; I had to wipe them from the Git history.

My process was:
1.  **Fix the Code**: First, I edited `app.py` to pull the secrets from environment variables instead of having them hardcoded.
2.  **Clean the History**: This was the tricky part. I used the `git-filter-repo` tool to go through every commit and remove the secrets. I had to create a `replacements.txt` file to tell the tool what to find and replace.
3.  **An Unexpected Discovery**: After cleaning the history, I ran Gitleaks again to be sure. It found *more* secrets! This was a huge lesson for me: I had accidentally committed some example keys inside my README file. I had to repeat the `git-filter-repo` process a second time to sanitize my documentation.
4.  **Final Verification**: The third Gitleaks scan finally came back clean, confirming the repository was secure.

---

## 3. Deploying the Secure Application with Docker

To prove that the application still worked after my changes, I deployed it locally using Docker. I created a `Dockerfile` to package the app, built the image, and then ran the container.

The most important part was launching the container securely. I injected the secrets as environment variables using the `-e` flag in the `docker run` command. The app started up perfectly, proving that you don't need to hardcode secrets to make things work.

---

## 4. My Screenshots: Before, After, and Deployed

Here are the screenshots that show the whole process from start to finish.

#### **Before:** Gitleaks Finding the Initial Secrets
*(Here you can see the first scan lighting up with the hardcoded secrets in `app.py`.)*

![Initial Secrets](screenshots/image.png)

---
#### **After:** The Clean Scan
*(This is the result I got after running the history cleanup twice. Gitleaks confirms no leaks were found.)*

![after scan](screenshots/image-1.png)

---
#### **Deployed:** The Application Running in Docker
*(Here is the final application running in my browser, served from the secure Docker container.)*

![Localhost by a docker](screenshots/image-2.png)

---

## 5. Challenges I Overcame

I ran into several real-world issues during this exercise, which were great learning experiences:

*   **Tooling and Environment Mismatch**: The initial instructions suggested using `brew`, which is a package manager for macOS. Since I was working on a Linux system, the command failed. This was a classic environment-specific issue that I solved by finding and following the correct installation instructions for my operating system (downloading the Gitleaks binary directly). It was a good reminder that documentation often needs to be adapted to your specific setup.

*   **Connecting to GitHub:** My local repository wasn't linked to my remote on GitHub, causing all my `git push` commands to fail. I had to diagnose the issue by checking my remote configuration with `git remote -v` and then fix the incorrect URL using `git remote set-url origin <URL>` before I could push my code.

*   **Understanding Powerful Tools:** `git-filter-repo` is not a simple command. My first attempts failed because the arguments were wrong. I learned that I needed to use `--replace-text` and that the tool has a built-in safety feature that prevents it from running on a "dirty" repository. I had to use the `--force` flag to override this and proceed with rewriting the history.

---

Of course. Here is the full "Core Concepts" section, rewritten in a more personal, "in my own words" style. Each answer explains the concept and is followed by a clear, real-world use case, just as you requested.

---
## 6. My Understanding of the Core Concepts

### Explain the concept of shift-left security and why it is important in DevSecOps.

To me, "shift-left" means dealing with security right from the very beginning, instead of saving it for the end. Think of a timeline where "left" is the start of a project (coding) and "right" is the end (deployment). Instead of having a security team parachute in at the last minute to find problems, you make security a normal part of every developer's daily job. This is a huge deal because finding and fixing a vulnerability while you're still writing the code is incredibly easy and cheap. Finding that same vulnerability when the application is live in production can be a nightmare—expensive, stressful, and dangerous.

*   **My Use Case Example**: I have a tool called a "pre-commit hook" set up on my own computer. Before I can even commit my code, this hook automatically runs a Gitleaks scan on the files I've changed. If I accidentally left an API key in the code, the hook will block the commit and show me an error right in my terminal. I can fix it in seconds. The secret never even makes it into my project's history, let alone the main repository. That's shifting security all the way to the left.

### How does detecting secrets early in the CI/CD pipeline prevent production vulnerabilities?

I think of the CI/CD pipeline as the automated assembly line for our code. Putting a secret scanner in the pipeline is like installing a quality control checkpoint on that assembly line. Every time a developer tries to merge new code, the scanner's job is to inspect it for secrets. If it finds one, it slams on the brakes—it fails the build and blocks the merge. This is a critical safety net. If a secret can't get past this checkpoint, it can't get into our main branch. If it's not in the main branch, it can't be packaged into a release and deployed to production where a real attacker could find it.

*   **My Use Case Example**: A teammate is in a rush and forgets to use our secrets manager, committing a database password directly into their feature branch. They create a Pull Request to merge it. Our automated system (like GitHub Actions) immediately kicks off. The Gitleaks scan runs, finds the password, and the pipeline fails with a big red "X". The Pull Request is automatically blocked from being merged, and a notification is sent to our team's Slack channel. The problem is contained and fixed before it ever posed a real threat.

### What strategies can be used to store secrets securely instead of hardcoding them?

The golden rule is to get secrets out of your code entirely. Your code is for logic, not for confidential data. The right way to do it is to use a system designed specifically for handling secrets. The main strategies I learned are:

1.  **Secrets Managers**: These are like digital vaults (e.g., HashiCorp Vault, AWS Secrets Manager). You store your secrets in this highly secure, encrypted service, and your application is given permission to ask for the secret when it needs it.
2.  **Environment Variables**: This is the method I used in this exercise. The application is built to read sensitive data from the environment it's running in. When we run the app (like in a Docker container), we securely inject the secret into that environment.

*   **My Use Case Example**: Our application is deployed in a Kubernetes cluster. The password for our payment provider's API is stored as a "Kubernetes Secret," which is an encrypted object managed by the cluster itself. When our application's container starts, our deployment configuration tells Kubernetes to mount that secret as an environment variable called `PAYMENT_API_KEY`. The application code just reads that variable at runtime. The key was never in the code, never in the Docker image, and is managed securely by the platform.

### Describe a situation where a secret could still be exposed even after scanning, and how to prevent it.

A scanner can definitely be tricked. Most scanners look for specific patterns or random-looking strings. If a developer intentionally tries to hide a secret from the scanner, they can often succeed. This is called "obfuscation." The scanner isn't smart enough to understand the *intent* of the code; it just reads the text.

*   **My Use Case Example**: To get around a scanner, a developer splits a key into pieces inside the code, knowing the scanner won't recognize the individual parts. It might look like this:
    ```python
    # The developer hides the key from the scanner by splitting it
    user = "ghp_part1_of_a_very_long_"
    token = "secret_key_part2_for_github"
    full_key = user + token
    ```
    A Gitleaks scan would likely miss this because `user` and `token` on their own don't look like a valid key. But when the code runs, it combines them into a perfectly valid—and exposed—secret.

*   **How to Prevent It (You need multiple layers)**:
    1.  **Smarter Tools**: Use more advanced SAST (Static Application Security Testing) tools that analyze the code's logic and data flow. A SAST tool could see that two strings are being combined and then used in a sensitive way (like an API header) and flag it.
    2.  **Human Review**: This is the most important defense. A mandatory code review process by another teammate would immediately catch this. A person would see this strange code and ask, "Why are you building a key from strings? This needs to come from our secrets vault." A human can spot suspicious intent that a tool might miss.
