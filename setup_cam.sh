#!/bin/bash
# Vérification des arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 ip"
    exit 1
fi

# Récupération des arguments
ip=$1
email=$email
minute="*/5"
heure="*"
jourDuMois="*"
mois="*"
jourDeLaSemaine="*"
commande="/home/pi/ping.sh $ip $email >> /home/pi/cron_output.txt"

# Création du cronjob
(crontab -l ; echo "$minute $heure $jourDuMois $mois $jourDeLaSemaine $commande") | crontab -

echo "Cronjob ajouté : $minute $heure $jourDuMois $mois $jourDeLaSemaine $commande"
