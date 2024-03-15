# Projet PiCamera2 Surveillance

## Introduction
Ce projet consiste en une application de surveillance utilisant une caméra PiCamera2 avec Flask, OpenCV pour la détection d'objets et de mouvements, ainsi que la gestion de vidéos et d'images capturées. L'application détecte les mouvements et les objets, enregistre des vidéos et des images lors de la détection, et offre une interface web pour visualiser les médias capturés.

## Table des Matières
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Fonctionnalités](#fonctionnalités)
- [Dépendances](#dépendances)
- [Configuration](#configuration)
- [Exemples](#exemples)
- [Dépannage](#dépannage)
- [Contributeurs](#contributeurs)

## Installation

### Prérequis
- Raspberry Pi avec PiCamera2
- Python 3.6 ou supérieur

### Étapes
1. Clonez le dépôt Git sur votre Raspberry Pi.
2. Installez les dépendances en exécutant :
```bash
sudo apt install python3-picamera2
sudo apt install python3-flask
sudo apt install python3-numpy
sudo apt install python3-opencv
```

## Utilisation
Pour démarrer l'application, exécutez le script principal avec Python :

```bash
python3 camera.py
```

L'application démarrera un serveur Flask accessible à l'adresse `http://0.0.0.0:5000` depuis n'importe quel navigateur web sur le même réseau.

## Fonctionnalités

- Détection de mouvement : Utilise les différences entre les images successives pour détecter le mouvement.
- Détection d'objets : Utilise SSD MobileNet pré-entraîné pour identifier les objets (personnes, voitures) dans le champ de la caméra.
- Enregistrement vidéo : Enregistre une vidéo lors de la détection d'un mouvement ou d'un objet.
- Capture d'images : Capture et sauvegarde des images de la scène avec la plus haute confiance de détection.
- Interface Web : Permet de visualiser les vidéos et images capturées via une interface web simple.
  
## Dépendances
- Flask
- OpenCV
- PiCamera2
- Numpy

## Configuration
Les paramètres clés du script (par exemple, l'intervalle de détection, la durée de pré-capture) peuvent être ajustés en modifiant les variables au début du script.

## Exemples
Accéder à l'interface web pour visualiser les images et vidéos capturées :

- Ouvrez un navigateur web et naviguez vers http://adresse_ip_du_pi:5000.
- Les médias capturés peuvent être consultés et téléchargés depuis cette interface.
  
## Dépannage
- Caméra non détectée : Assurez-vous que la caméra est correctement connectée au Raspberry Pi et que celle-ci est activée dans la configuration raspi-config.
- Dépendances manquantes : Vérifiez que toutes les dépendances nécessaires sont installées en exécutant
```bash
sudo apt install python3-picamera2
sudo apt install python3-flask
sudo apt install python3-numpy
sudo apt install python3-opencv
```
## Contributeurs
- @AyRickk
- @LNJAD
- @SpaceNightt
- @PKNekoLink
