import os
import subprocess
import glob
import base64

# Rechercher tous les fichiers .mp4 et .jpg dans les répertoires correspondants
mp4_files = glob.glob("./videos/*.mp4")
img_files = glob.glob("./img/*.jpg")  # Assurez-vous que cela correspond au format de vos images

# Trier les fichiers par date de modification et obtenir le dernier fichier de chaque type
last_video_file = sorted(mp4_files, key=lambda x: os.path.getmtime(x))[-1] if mp4_files else None
last_img_file = sorted(img_files, key=lambda x: os.path.getmtime(x))[-1] if img_files else None

# Vérifier si les fichiers existent
if not last_video_file or not last_img_file:
    print("Required files not found")
    exit(1)  # Arrêtez l'exécution si un fichier est manquant

# Define variables
subject = "Security alert: Human or Car detected"
send_email = "aymeric.daniel@isen.yncrea.fr"

# Début de la construction du corps de l'e-mail
body = f"""\
Subject: {subject}
To: {send_email}
Content-Type: multipart/mixed; boundary=boundary123

--boundary123
Content-Type: text/plain; charset=UTF-8

Hi,

This is an automated message from our company, and please note that this email address does not accept replies.

We wanted to bring to your attention that we have recently detected suspicious activity through one of our surveillance cameras. Attached to this email is a video recording and the last captured image of the incident.

If you have any questions or concerns, please contact us at pilook81help@gmail.com.

Thank you for your cooperation.

Best regards,
"""

# Ajouter la vidéo
with open(last_video_file, "rb") as file:
    encoded_video = base64.b64encode(file.read()).decode()
body += f"""\
--boundary123
Content-Type: video/mp4; charset=UTF-8
Content-Disposition: attachment; filename="{os.path.basename(last_video_file)}"
Content-Transfer-Encoding: base64

{encoded_video}

"""

# Ajouter l'image
with open(last_img_file, "rb") as file:
    encoded_image = base64.b64encode(file.read()).decode()
body += f"""\
--boundary123
Content-Type: image/jpeg; charset=UTF-8
Content-Disposition: attachment; filename="{os.path.basename(last_img_file)}"
Content-Transfer-Encoding: base64

{encoded_image}

--boundary123--
"""

# Envoyer l'email en utilisant subprocess
process = subprocess.Popen(["sendmail", send_email], stdin=subprocess.PIPE)
process.communicate(input=body.encode())

