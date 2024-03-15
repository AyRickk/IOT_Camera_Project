import subprocess

# Define variables
subject = "Security alert: Camera obstructed or covered"
send_email = "aymeric.daniel@isen.yncrea.fr"

# Construction du corps de l'e-mail
body = f"""\
Subject: {subject}
To: {send_email}
Content-Type: text/plain; charset=UTF-8

Hello,

This is an automatic message from our security system. We are informing you that one of our surveillance cameras appears to be obstructed or covered.

This may indicate an attempt to conceal suspicious activity or a technical problem preventing the camera from working properly. We advise you to check the condition of the camera as soon as possible.
If you have any questions or require assistance, please contact us at pilook81help@gmail.com.

Thank you for your cooperation.

Best regards,
"""

# Envoyer l'email en utilisant subprocess
process = subprocess.Popen(["sendmail", send_email], stdin=subprocess.PIPE)
process.communicate(input=body.encode())
