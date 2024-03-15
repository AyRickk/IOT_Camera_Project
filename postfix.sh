#!/bin/bash

echo -e " \033[32;5mUpdate&Upgrade\033[0m"
sudo apt-get update && sudo apt-get upgrade

echo -e " \033[32;5mInstall Postfix\033[0m"
sudo apt-get install libsasl2-modules postfix

echo -e " \033[32;5mMise en place de l'email et du password\033[0m"

echo -e " \033[32;5mRentrez l'email que vous utilisez :\033[0m"
read emailUtilisateur
echo "Vous avez rentrer que l'email de l'utilisateur est : $emailUtilisateur"

echo -e " \033[32;5mRentrez le mot de passe associé obtenu sur Gmail :\033[0m"
read MotDePasseUtilisateur
echo "Vous avez rentrer que le mot de passe associé est : $MotDePasseUtilisateur"

echo "[smtp.gmail.com]:587 $emailUtilisateur:$MotDePasseUtilisateur" | sudo tee /etc/postfix/sasl/sasl_passwd

unset emailUtilisateur
unset MotDePasseUtilisateur

sudo postmap /etc/postfix/sasl/sasl_passwd

sudo chown root:root /etc/postfix/sasl/sasl_passwd /etc/postfix/sasl/sasl_passwd.db
sudo chmod 0600 /etc/postfix/sasl/sasl_passwd /etc/postfix/sasl/sasl_passwd.db

echo -e " \033[32;5mModification du main.cf\033[0m"
sudo tee -a /etc/postfix/main.cf <<EOF
relayhost = [smtp.gmail.com]:587
# Enable SASL authentication
smtp_sasl_auth_enable = yes
# Disallow methods that allow anonymous authentication
smtp_sasl_security_options = noanonymous
# Location of sasl_passwd
smtp_sasl_password_maps = hash:/etc/postfix/sasl/sasl_passwd
# Enable STARTTLS encryption
smtp_tls_security_level = encrypt
# Location of CA certificates
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt
EOF

echo -e " \033[32;5mRestart de Postfix\033[0m"
sudo systemctl restart postfix

sleep 5