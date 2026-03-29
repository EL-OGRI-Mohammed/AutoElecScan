📝 Présentation du Projet

AutoElecScan est une solution de vision artificielle conçue pour automatiser la reconnaissance et la classification de composants électroniques. Ce projet combine le Deep Learning et l'Informatique Industrielle pour offrir une inspection rapide et précise dans un environnement de laboratoire ou de production.


Le système utilise un modèle de réseau de neurones convolutionnels (CNN) pour identifier en temps réel plusieurs classes de composants (résistances, condensateurs, diodes, etc.) à travers un flux vidéo distant.


🛠️ Spécifications Techniques
Intelligence Artificielle & Vision

Architecture : CNN (Convolutional Neural Network) basé sur EfficientNetB0.


Performance : Précision de 99.44% obtenue sur le dataset d'entraînement.


Traitement d'image : Utilisation de OpenCV pour le prétraitement et la gestion du flux vidéo.



Framework : Développé avec TensorFlow / Keras.


Logiciel & Interface

Langage : Python.



Interface Graphique : GUI développée avec Tkinter pour la visualisation en temps réel et le monitoring.



Architecture : Client-Serveur permettant l'acquisition d'images via un flux vidéo IP (Smartphone/Caméra IP).


📂 Structure du Dépôt
main.py : Script principal gérant l'interface Tkinter et la logique de détection.

modele_v1.h5 : Modèle de Deep Learning entraîné.

classes.txt : Fichier contenant les étiquettes des composants.

requirements.txt : Liste des dépendances Python.

⚙️ Configuration et Installation
1. Installation des dépendances
Assurez-vous d'avoir Python installé, puis exécutez :

Bash
pip install -r requirements.txt
2. Configuration locale
Dans le fichier main.py, configurez les chemins d'accès à votre modèle et votre fichier de classes :

Python
# Modifier ces chemins selon votre répertoire local
chemin_modele = r"votre_chemin/modele_v1.h5"
chemin_classes = r"votre_chemin/classes.txt"
3. Connexion Caméra (IP Webcam)
Installez l'application IP Webcam sur votre smartphone.

Lancez le serveur vidéo.

Mettez à jour l'adresse IP dans la variable CAMERA_URL du script main.py.

🚀 À propos de l'auteur
Actuellement en 2ème année de cycle d'ingénieur à l'EMI, je me spécialise en Automatique et Informatique Industrielle (AII). Passionné par l'innovation technologique et les systèmes intelligents, ce projet s'inscrit dans mon expertise en systèmes embarqués et vision artificielle.



Projet réalisé dans le cadre académique de l'École Mohammadia d'Ingénieurs. 
+1
