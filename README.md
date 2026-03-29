# AutoElecScan

## Présentation du Projet

AutoElecScan est une solution de vision artificielle conçue pour automatiser la reconnaissance et la classification de composants électroniques.

Ce projet combine le Deep Learning et l’Informatique Industrielle afin d’offrir une inspection rapide, fiable et précise dans un environnement de laboratoire ou de production.

Le système repose sur un modèle de réseau de neurones convolutionnels (CNN) capable d’identifier en temps réel plusieurs classes de composants électroniques (résistances, condensateurs, diodes, circuits intégrés, etc.) à travers un flux vidéo distant.

---

## Spécifications Techniques

### Intelligence Artificielle & Vision

- Architecture du modèle : CNN basé sur EfficientNetB0  
- Performance : 99.44 % de précision obtenue sur le dataset d’entraînement  
- Traitement d’image : OpenCV pour le prétraitement et la gestion du flux vidéo  
- Framework IA : TensorFlow / Keras  

### Logiciel & Interface

- Langage : Python  
- Interface graphique : Tkinter (visualisation en temps réel et monitoring)  
- Architecture système : Client-Serveur  
- Acquisition vidéo : Flux IP (Smartphone ou Caméra IP)  

---

## Structure du Dépôt

- `main.py` : Script principal gérant l’interface Tkinter et la logique de détection  
- `modele_v1.h5` : Modèle de Deep Learning entraîné  
- `classes.txt` : Fichier contenant les étiquettes des composants  
- `requirements.txt` : Liste des dépendances Python  

---

## Configuration et Installation

### 1. Installation des dépendances

Assurez-vous d’avoir Python installé, puis exécutez :

```bash
pip install -r requirements.txt
```

---

### 2. Configuration locale

Dans le fichier `main.py`, configurez les chemins d’accès au modèle et au fichier des classes :

```python
# Modifier ces chemins selon votre répertoire local

chemin_modele = r"votre_chemin/modele_v1.h5"
chemin_classes = r"votre_chemin/classes.txt"
```

---

### 3. Connexion Caméra (IP Webcam)

1. Installer l’application IP Webcam sur votre smartphone  
2. Lancer le serveur vidéo  
3. Mettre à jour l’adresse IP dans la variable `CAMERA_URL` du script `main.py`  

---

## À propos de l’auteur

Étudiant en 2ème année du cycle d’ingénieur à l’École Mohammadia d’Ingénieurs (EMI), spécialité Automatique et Informatique Industrielle (AII).

Passionné par les systèmes intelligents, l’automatisation et la vision artificielle, ce projet s’inscrit dans une démarche de développement de solutions industrielles basées sur l’Intelligence Artificielle et les systèmes embarqués.

---

Projet réalisé dans le cadre académique de l’École Mohammadia d’Ingénieurs.
