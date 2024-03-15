#!/bin/bash

ip_address=1.1.1.1  # Adresse IP à surveiller
email=$2
lock_file="/home/pi/lock_file/$ip_address"  # Fichier de verrouillage

if ping -c 1 "$ip_address" > /dev/null 2>&1; then
    # L'adresse IP répond
    if [ -f "$lock_file" ]; then
        # Supprimer le fichier de verrouillage si l'adresse IP répond maintenant
        rm "$lock_file"
    fi
    echo "L'adresse IP $ip_address répond."
else
    # L'adresse IP ne répond pas
    if [ ! -f "$lock_file" ]; then
        # Envoyer le flag seulement si le fichier de verrouillage n'existe pas
        echo "L'adresse IP $ip_address ne répond pas. nous ne sommes pas relier a internet"
        # on envoie un SMS 
      
        touch "$lock_file"  # Créer un fichier de verrouillage
    fi
fi
