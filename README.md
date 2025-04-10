# keylogger-monitor
Keylogger written in Python for monitoring purposes.
# Keylogger-Monitor in Python

This project is a keylogger written in Python, designed for monitoring keystrokes, collecting sensitive data (such as phone numbers, emails, passwords), and gathering cookies from websites.

## Description

This script captures the keystrokes of the user, logs them into a file, and checks for sensitive data such as phone numbers, email addresses, and passwords. Additionally, it can collect cookies from websites via HTTP requests. All collected data can be sent to a server for further storage or analysis.

## Features

- Keystroke capture
- Log archiving when the file size exceeds the limit
- Sensitive data detection (emails, phone numbers, passwords)
- Cookie collection from websites
- Sending collected data to a server

## Instructions for Running

### 1. Install Dependencies

To run the project, you need to install the following libraries:

```bash
pip install pynput requests
