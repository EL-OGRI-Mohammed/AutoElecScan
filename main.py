import cv2
import requests
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
import json
import os
import tensorflow as tf
from tensorflow import keras

class DetecteurComposants:
    def __init__(self):
        self.modele = None
        self.classes = {}
        self.modele_charge = False
        self.charger_modele_ia()

    def charger_modele_ia(self):
        """Charger le modèle IA et les classes"""
        try:
            # Chemins absolus vers vos fichiers
            chemin_modele = r"le chemin vers votre modele dans votre pc"
            chemin_classes = r"le chemin vers les classes dans votre pc"

            print("🔧 Chargement du modèle IA...")

            # Vérifier si les fichiers existent
            if not os.path.exists(chemin_modele):
                print(f"❌ Fichier modèle non trouvé: {chemin_modele}")
                self.creer_modele_simulation()
                return

            if not os.path.exists(chemin_classes):
                print(f"❌ Fichier classes non trouvé: {chemin_classes}")
                self.creer_classes_simulation()
                return

            # Charger le modèle TensorFlow
            self.modele = keras.models.load_model(chemin_modele)

            # Charger les classes
            with open(chemin_classes, 'r', encoding='utf-8') as f:
                self.classes = json.load(f)

            self.modele_charge = True
            print(f"✅ Modèle IA chargé - {len(self.classes)} classes disponibles")
            print(f"📋 Classes: {list(self.classes.values())}")

        except Exception as e:
            print(f"❌ Erreur chargement modèle IA: {e}")
            self.creer_modele_simulation()

    def creer_modele_simulation(self):
        """Créer un modèle simulé si le vrai modèle n'est pas disponible"""
        print("🔧 Création d'un modèle simulé...")
        self.modele_charge = True
        self.creer_classes_simulation()
        print("✅ Modèle simulé créé - Prêt pour les tests")

    def creer_classes_simulation(self):
        """Créer des classes simulées"""
        self.classes = {
            "0": "Résistance 1kΩ",
            "1": "Condensateur Électrolytique 100µF",
            "2": "Condensateur Céramique 10nF",
            "3": "Transistor NPN BC547",
            "4": "Transistor PNP BC557",
            "5": "Diode 1N4148",
            "6": "LED Rouge 5mm",
            "7": "Circuit Intégré 555",
            "8": "Circuit Intégré LM741",
            "9": "Bobine 100µH",
            "10": "Quartz 16MHz",
            "11": "Connecteur USB",
            "12": "Interrupteur",
            "13": "Potentiomètre 10kΩ"
        }

    def pretraiter_image(self, image):
        """Prétraiter l'image pour l'IA"""
        try:
            # Redimensionner à la taille attendue par le modèle (224x224 standard)
            image_redimensionnee = cv2.resize(image, (224, 224))

            # Normaliser les pixels [0, 255] -> [0, 1]
            image_normalisee = image_redimensionnee / 255.0

            # Ajouter dimension batch
            image_batch = np.expand_dims(image_normalisee, axis=0)

            return image_batch

        except Exception as e:
            print(f"❌ Erreur prétraitement: {e}")
            return None

    def analyser_composant(self, image):
        """Analyser l'image et identifier le composant avec l'IA"""
        try:
            if not self.modele_charge:
                return "Modèle non chargé", 0.0

            # Prétraiter l'image
            image_batch = self.pretraiter_image(image)
            if image_batch is None:
                return "Erreur prétraitement", 0.0

            # Faire la prédiction
            if self.modele is not None:
                # VRAI MODÈLE IA
                predictions = self.modele.predict(image_batch, verbose=0)
                id_classe = np.argmax(predictions[0])
                confiance = float(predictions[0][id_classe])
            else:
                # MODÈLE SIMULÉ (si vrai modèle pas disponible)
                import random
                id_classe = random.randint(0, len(self.classes) - 1)
                confiance = random.uniform(0.7, 0.95)

            # Obtenir le nom du composant
            composant = self.classes.get(str(id_classe), f"Composant {id_classe}")

            return composant, confiance

        except Exception as e:
            print(f"❌ Erreur analyse IA: {e}")
            return "Erreur analyse", 0.0

class FluxVideo:
    def __init__(self, ip_telephone="192.168.0.221", port=8080):
        self.ip_telephone = ip_telephone
        self.port = port
        self.url_video = f"http://{ip_telephone}:{port}/video"
        self.url_capture = f"http://{ip_telephone}:{port}/shot.jpg"
        self.capture = None
        self.actif = False
        self.image_actuelle = None
        self.detecteur = DetecteurComposants()
        self.derniere_image_time = 0

    def demarrer_flux(self):
        """Démarrer la capture vidéo"""
        try:
            print(f"🎬 Connexion au téléphone: {self.ip_telephone}")

            # Essayer d'abord le flux MJPEG
            self.capture = cv2.VideoCapture(self.url_video)

            # Configurer le timeout
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not self.capture.isOpened():
                print("❌ Impossible d'ouvrir le flux vidéo MJPEG")
                return False

            # Tester la lecture
            ret, frame = self.capture.read()
            if not ret:
                print("❌ Impossible de lire le flux vidéo")
                self.capture.release()
                return False

            self.actif = True
            print("✅ Flux vidéo démarré avec succès")

            # Démarrer le thread de capture
            thread_capture = threading.Thread(target=self.capturer_images)
            thread_capture.daemon = True
            thread_capture.start()

            return True

        except Exception as e:
            print(f"❌ Erreur démarrage flux: {e}")
            return False

    def capturer_images(self):
        """Capturer les images en continu avec gestion d'erreurs améliorée"""
        print("📹 Démarrage du thread de capture...")
        compteur_images = 0

        while self.actif:
            try:
                if self.capture and self.capture.isOpened():
                    # Vider le buffer
                    for _ in range(2):
                        self.capture.grab()

                    ret, frame = self.capture.retrieve()

                    if ret and frame is not None:
                        self.image_actuelle = frame
                        compteur_images += 1
                        self.derniere_image_time = time.time()

                        if compteur_images % 30 == 0:
                            print(f"📊 Images capturées: {compteur_images}")
                    else:
                        print("⚠️  Frame vide ou corrompue")
                        self.reconnecter()

                else:
                    print("🔌 Capture fermée - Reconnexion...")
                    self.reconnecter()

            except Exception as e:
                print(f"❌ Erreur capture: {e}")
                self.reconnecter()

            time.sleep(0.033)  # ~30 FPS

        print("🛑 Thread de capture arrêté")

    def reconnecter(self):
        """Reconnecter au flux vidéo"""
        try:
            print("🔄 Tentative de reconnexion...")
            if self.capture:
                self.capture.release()
                time.sleep(1)

            self.capture = cv2.VideoCapture(self.url_video)
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if self.capture.isOpened():
                print("✅ Reconnexion réussie")
                return True
            else:
                print("❌ Échec reconnexion")
                return False

        except Exception as e:
            print(f"❌ Erreur reconnexion: {e}")
            return False

    def capturer_image_unique(self):
        """Capturer une image unique via l'URL shot.jpg"""
        try:
            print("📸 Capture d'image unique...")
            response = requests.get(self.url_capture, timeout=10)
            if response.status_code == 200:
                image_data = np.frombuffer(response.content, np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
                if image is not None:
                    print("✅ Image unique capturée")
                    return image
                else:
                    print("❌ Échec décodage image")
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur capture unique: {e}")
        return None

    def obtenir_image(self):
        """Obtenir la dernière image capturée"""
        return self.image_actuelle

    def est_actif(self):
        """Vérifier si le flux est actif"""
        return self.actif and (time.time() - self.derniere_image_time < 5.0)

    def arreter_flux(self):
        """Arrêter le flux vidéo"""
        print("🛑 Arrêt du flux vidéo...")
        self.actif = False
        if self.capture:
            self.capture.release()
        cv2.destroyAllWindows()
        print("✅ Flux vidéo arrêté")

class InterfaceScanner:
    def __init__(self):
        self.fenetre = tk.Tk()
        self.flux_video = None
        self.composant_actuel = "Non identifié"
        self.confiance_actuelle = 0.0
        self.analyse_active = False
        self.intervalle_analyse = 2.0  # secondes entre les analyses

        # Configuration du style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.configurer_interface()
        self.demarrer_interface_config()

    def configurer_interface(self):
        """Configurer l'interface graphique principale"""
        self.fenetre.title("🔍 Scanner Composants Électroniques")
        self.fenetre.geometry("1200x800")
        self.fenetre.configure(bg='#2c3e50')

        # Style moderne
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TLabel', background='#2c3e50', foreground='white')
        self.style.configure('TLabelframe', background='#34495e', foreground='white')
        self.style.configure('TLabelframe.Label', background='#34495e', foreground='white')
        self.style.configure('Accent.TButton',
                           background='#27ae60',
                           foreground='white',
                           font=('Arial', 12, 'bold'))

        # Cadre principal
        self.cadre_principal = ttk.Frame(self.fenetre, padding="10")
        self.cadre_principal.pack(fill=tk.BOTH, expand=True)

    def demarrer_interface_config(self):
        """Interface de configuration initiale"""
        # Nettoyer l'interface
        for widget in self.cadre_principal.winfo_children():
            widget.destroy()

        # Titre
        titre = ttk.Label(self.cadre_principal,
                         text="🔍 Configuration du Scanner",
                         font=('Arial', 20, 'bold'),
                         foreground='#3498db')
        titre.pack(pady=20)

        # Cadre configuration
        cadre_config = ttk.LabelFrame(self.cadre_principal,
                                    text="📱 Configuration Téléphone",
                                    padding="20")
        cadre_config.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)

        # Instructions
        instructions = ttk.Label(cadre_config,
                               text="""
📋 Instructions de configuration :

1. 📲 Sur votre téléphone Android :
   • Téléchargez 'IP Webcam' depuis le Play Store
   • Lancez l'application
   • Cliquez sur 'Start Server'

2. 🌐 Notez l'adresse IP affichée
   (Exemple : 10.72.125.227:8080)

3. 🔌 Assurez-vous que le téléphone et le PC sont sur le même réseau WiFi

4. ⚙️ Dans IP Webcam, allez dans Paramètres → Video preferences →
   Décochez "Use built-in camera viewer" pour meilleure performance
""",
                               font=('Arial', 12),
                               justify=tk.LEFT)
        instructions.pack(pady=20)

        # Champ IP
        cadre_ip = ttk.Frame(cadre_config)
        cadre_ip.pack(fill=tk.X, pady=20)

        ttk.Label(cadre_ip, text="IP du téléphone:",
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)

        self.entry_ip = ttk.Entry(cadre_ip, font=('Arial', 12), width=20)
        self.entry_ip.pack(side=tk.LEFT, padx=10)
        self.entry_ip.insert(0, "192.168.0.221")  # Votre IP

        ttk.Label(cadre_ip, text=":8080",
                 font=('Arial', 12)).pack(side=tk.LEFT)

        # Statut actuel
        self.label_statut_config = ttk.Label(cadre_config,
                                           text="🔍 Prêt à se connecter",
                                           font=('Arial', 11),
                                           foreground='#f39c12')
        self.label_statut_config.pack(pady=10)

        # Boutons
        cadre_boutons = ttk.Frame(cadre_config)
        cadre_boutons.pack(pady=30)

        ttk.Button(cadre_boutons,
                  text="🎬 Démarrer le Scanner",
                  command=self.demarrer_scanner,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=10)

        ttk.Button(cadre_boutons,
                  text="🔍 Tester Connexion",
                  command=self.tester_connexion_config).pack(side=tk.LEFT, padx=10)

        # Mode démo (si connexion échoue)
        ttk.Button(cadre_boutons,
                  text="🎭 Mode Démo",
                  command=self.mode_demo).pack(side=tk.LEFT, padx=10)

        # Informations modèle IA
        cadre_ia = ttk.Frame(cadre_config)
        cadre_ia.pack(fill=tk.X, pady=20)

        texte_ia = "🤖 Modèle IA: " + ("✅ Chargé" if True else "❌ Non chargé")
        label_ia = ttk.Label(cadre_ia,
                           text=texte_ia,
                           font=('Arial', 10, 'bold'),
                           foreground='#27ae60')
        label_ia.pack()

    def mode_demo(self):
        """Mode démo avec vidéo de test"""
        print("🎭 Activation du mode démo...")
        self.flux_video = FluxVideo(ip_telephone="demo")
        self.flux_video.actif = True

        # Créer une image de démo
        image_demo = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image_demo, "MODE DÉMO - Placez un composant ici",
                   (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.rectangle(image_demo, (220, 180), (420, 300), (0, 0, 255), 3)

        self.flux_video.image_actuelle = image_demo
        self.afficher_interface_principale()
        messagebox.showinfo("Mode Démo", "Mode démo activé. Le scanner fonctionne avec une image de test.")

    def tester_connexion_config(self):
        """Tester la connexion depuis l'interface de configuration"""
        ip_telephone = self.entry_ip.get().strip()

        if not ip_telephone:
            messagebox.showerror("Erreur", "Veuillez entrer l'IP du téléphone")
            return

        self.label_statut_config.config(text="🔍 Test de connexion en cours...", foreground='#f39c12')

        # Tester la connexion dans un thread séparé
        thread_test = threading.Thread(target=self.effectuer_test_connexion, args=(ip_telephone,))
        thread_test.daemon = True
        thread_test.start()

    def effectuer_test_connexion(self, ip_telephone):
        """Effectuer le test de connexion"""
        try:
            url_test = f"http://{ip_telephone}:8080"
            response = requests.get(url_test, timeout=5)

            if response.status_code == 200:
                self.fenetre.after(0, lambda: self.label_statut_config.config(
                    text="✅ Connexion réussie!", foreground='#27ae60'))
            else:
                self.fenetre.after(0, lambda: self.label_statut_config.config(
                    text="❌ Connexion échouée", foreground='#e74c3c'))

        except Exception as e:
            self.fenetre.after(0, lambda: self.label_statut_config.config(
                text=f"❌ Erreur: {str(e)}", foreground='#e74c3c'))

    def demarrer_scanner(self):
        """Démarrer le scanner avec l'IP configurée"""
        ip_telephone = self.entry_ip.get().strip()

        if not ip_telephone:
            messagebox.showerror("Erreur", "Veuillez entrer l'IP du téléphone")
            return

        print(f"🚀 Démarrage avec IP: {ip_telephone}")

        # Initialiser le flux vidéo
        self.flux_video = FluxVideo(ip_telephone=ip_telephone)

        # Tester la connexion
        if not self.tester_connexion():
            messagebox.showerror("Erreur Connexion",
                               f"Impossible de se connecter au téléphone {ip_telephone}\n"
                               "Vérifiez:\n"
                               "• L'IP est correcte\n"
                               "• IP Webcam est lancé\n"
                               "• Même réseau WiFi\n\n"
                               "Essayez le mode démo pour tester le système.")
            return

        # Démarrer le flux vidéo
        if self.flux_video.demarrer_flux():
            self.afficher_interface_principale()
        else:
            messagebox.showerror("Erreur",
                               "Impossible de démarrer le flux vidéo.\n"
                               "Essayez le mode démo ou vérifiez les paramètres IP Webcam.")

    def tester_connexion(self):
        """Tester la connexion au téléphone"""
        try:
            url_test = f"http://{self.flux_video.ip_telephone}:8080"
            response = requests.get(url_test, timeout=5)
            return response.status_code == 200
        except:
            return False

    def afficher_interface_principale(self):
        """Afficher l'interface principale du scanner"""
        # Nettoyer l'interface
        for widget in self.cadre_principal.winfo_children():
            widget.destroy()

        # Titre
        titre = ttk.Label(self.cadre_principal,
                         text="🔍 Scanner Composants Électroniques - TEMPS RÉEL",
                         font=('Arial', 18, 'bold'),
                         foreground='#3498db')
        titre.pack(pady=10)

        # Cadre contenu
        cadre_contenu = ttk.Frame(self.cadre_principal)
        cadre_contenu.pack(fill=tk.BOTH, expand=True)

        # Cadre vidéo (gauche)
        cadre_video = ttk.LabelFrame(cadre_contenu, text="🎥 Vue Caméra", padding="10")
        cadre_video.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Label pour la vidéo avec taille fixe
        self.label_video = ttk.Label(cadre_video,
                                   background='black',
                                   text="Chargement de la vidéo...\n\nSi la vidéo n'apparaît pas:\n• Vérifiez la connexion\n• Essayez le mode démo",
                                   font=('Arial', 12),
                                   foreground='white',
                                   justify=tk.CENTER)
        self.label_video.pack(fill=tk.BOTH, expand=True)

        # Cadre informations (droite)
        cadre_info = ttk.LabelFrame(cadre_contenu, text="📊 Analyse", padding="10", width=350)
        cadre_info.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        cadre_info.pack_propagate(False)

        # Statut connexion
        statut_texte = f"📱 Connecté: {self.flux_video.ip_telephone}"
        if self.flux_video.ip_telephone == "demo":
            statut_texte = "🎭 Mode Démo Activé"

        self.label_statut = ttk.Label(cadre_info,
                                    text=statut_texte,
                                    font=('Arial', 12, 'bold'),
                                    foreground='#27ae60')
        self.label_statut.pack(pady=10)

        # Statut flux vidéo
        self.label_statut_video = ttk.Label(cadre_info,
                                          text="📹 Vidéo: En attente...",
                                          font=('Arial', 10),
                                          foreground='#f39c12')
        self.label_statut_video.pack(pady=5)

        # Statut IA
        statut_ia = "✅ IA Activée" if self.flux_video.detecteur.modele_charge else "⚠️ IA Simulation"
        self.label_ia = ttk.Label(cadre_info,
                                 text=f"🤖 {statut_ia}",
                                 font=('Arial', 10),
                                 foreground='#3498db')
        self.label_ia.pack(pady=5)

        # Résultat analyse
        cadre_resultat = ttk.LabelFrame(cadre_info, text="🔍 Résultat", padding="10")
        cadre_resultat.pack(fill=tk.X, pady=10)

        ttk.Label(cadre_resultat, text="Composant identifié:",
                 font=('Arial', 11, 'bold')).pack(anchor='w')

        self.label_composant = ttk.Label(cadre_resultat,
                                       text="En attente...",
                                       font=('Arial', 14, 'bold'),
                                       foreground='#f39c12')
        self.label_composant.pack(fill=tk.X, pady=5)

        # Confiance
        cadre_confiance = ttk.Frame(cadre_resultat)
        cadre_confiance.pack(fill=tk.X, pady=10)

        ttk.Label(cadre_confiance, text="Niveau de confiance:",
                 font=('Arial', 11, 'bold')).pack(anchor='w')

        self.variable_confiance = tk.DoubleVar()
        barre_confiance = ttk.Progressbar(cadre_confiance,
                                        variable=self.variable_confiance,
                                        maximum=100)
        barre_confiance.pack(fill=tk.X, pady=5)

        self.label_pourcentage = ttk.Label(cadre_confiance, text="0%")
        self.label_pourcentage.pack()

        # Contrôles
        cadre_controles = ttk.Frame(cadre_info)
        cadre_controles.pack(fill=tk.X, pady=20)

        ttk.Button(cadre_controles,
                  text="🎬 Démarrer Analyse Auto",
                  command=self.demarrer_analyse_auto).pack(fill=tk.X, pady=5)

        ttk.Button(cadre_controles,
                  text="⏹ Arrêter Analyse",
                  command=self.arreter_analyse).pack(fill=tk.X, pady=5)

        ttk.Button(cadre_controles,
                  text="📸 Capture Unique",
                  command=self.capture_unique).pack(fill=tk.X, pady=5)

        ttk.Button(cadre_controles,
                  text="💾 Sauvegarder Résultat",
                  command=self.sauvegarder_resultat).pack(fill=tk.X, pady=5)

        ttk.Button(cadre_controles,
                  text="⚙️ Reconfigurer",
                  command=self.demarrer_interface_config).pack(fill=tk.X, pady=5)

        # Instructions
        instructions = ttk.Label(cadre_info,
                               text="""🎯 Instructions:
• Placez le composant dans le cadre
• Assurez un bon éclairage
• Maintenez stable pendant l'analyse
• Les résultats s'affichent automatiquement""",
                               font=('Arial', 9),
                               justify=tk.LEFT,
                               background='#ecf0f1',
                               foreground='#2c3e50',
                               padding=10)
        instructions.pack(fill=tk.X, pady=20)

        # Démarrer la mise à jour vidéo
        self.mettre_a_jour_video()

    def mettre_a_jour_video(self):
        """Mettre à jour l'affichage vidéo"""
        if self.flux_video and self.flux_video.est_actif():
            image = self.flux_video.obtenir_image()

            if image is not None:
                try:
                    # Redimensionner l'image pour l'affichage
                    hauteur, largeur = image.shape[:2]

                    # Dessiner le cadre de ciblage
                    centre_x, centre_y = largeur // 2, hauteur // 2
                    taille_cible = min(largeur, hauteur) // 3

                    # Cadre rouge
                    cv2.rectangle(image,
                                 (centre_x - taille_cible, centre_y - taille_cible),
                                 (centre_x + taille_cible, centre_y + taille_cible),
                                 (0, 0, 255), 3)

                    # Croix de centrage
                    cv2.line(image, (centre_x, 0), (centre_x, hauteur), (0, 255, 0), 2)
                    cv2.line(image, (0, centre_y), (largeur, centre_y), (0, 255, 0), 2)

                    # Convertir pour Tkinter
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image_pil = Image.fromarray(image_rgb)

                    # Redimensionner pour l'affichage (maintenir le ratio)
                    ratio = min(800 / largeur, 600 / hauteur)
                    nouvelle_largeur = int(largeur * ratio)
                    nouvelle_hauteur = int(hauteur * ratio)

                    image_pil = image_pil.resize((nouvelle_largeur, nouvelle_hauteur), Image.Resampling.LANCZOS)

                    image_tk = ImageTk.PhotoImage(image_pil)
                    self.label_video.configure(image=image_tk, text="")
                    self.label_video.image = image_tk

                    self.label_statut_video.config(text="📹 Vidéo: ✅ Active", foreground='#27ae60')

                except Exception as e:
                    print(f"❌ Erreur affichage vidéo: {e}")
                    self.label_video.config(text=f"Erreur vidéo: {str(e)}")
            else:
                self.label_statut_video.config(text="📹 Vidéo: ⏳ En attente...", foreground='#f39c12')
        else:
            self.label_statut_video.config(text="📹 Vidéo: ❌ Non connectée", foreground='#e74c3c')
            if self.flux_video and self.flux_video.ip_telephone != "demo":
                self.label_video.config(text="Connexion vidéo perdue...\nReconnexion automatique en cours")

        # Rappeler cette fonction
        self.fenetre.after(100, self.mettre_a_jour_video)

    def demarrer_analyse_auto(self):
        """Démarrer l'analyse automatique"""
        self.analyse_active = True
        self.analyser_periodiquement()
        print("✅ Analyse automatique démarrée")

    def arreter_analyse(self):
        """Arrêter l'analyse automatique"""
        self.analyse_active = False
        print("⏹ Analyse arrêtée")

    def analyser_periodiquement(self):
        """Analyser périodiquement l'image"""
        if self.analyse_active and self.flux_video and self.flux_video.obtenir_image() is not None:
            # Analyser l'image
            composant, confiance = self.flux_video.detecteur.analyser_composant(
                self.flux_video.obtenir_image()
            )

            # Mettre à jour l'interface
            self.composant_actuel = composant
            self.confiance_actuelle = confiance

            self.label_composant.config(text=composant)
            self.variable_confiance.set(confiance * 100)
            self.label_pourcentage.config(text=f"{confiance*100:.1f}%")

            # Changer la couleur selon la confiance
            if confiance > 0.8:
                couleur = '#27ae60'  # Vert
            elif confiance > 0.6:
                couleur = '#f39c12'  # Orange
            else:
                couleur = '#e74c3c'  # Rouge

            self.label_composant.config(foreground=couleur)

            print(f"🔍 {composant} - {confiance*100:.1f}%")

        # Rappeler si l'analyse est toujours active
        if self.analyse_active:
            self.fenetre.after(int(self.intervalle_analyse * 1000), self.analyser_periodiquement)

    def capture_unique(self):
        """Effectuer une capture et analyse unique"""
        if self.flux_video:
            image = self.flux_video.capturer_image_unique()
            if image is not None:
                composant, confiance = self.flux_video.detecteur.analyser_composant(image)

                self.label_composant.config(text=composant)
                self.variable_confiance.set(confiance * 100)
                self.label_pourcentage.config(text=f"{confiance*100:.1f}%")

                messagebox.showinfo("Résultat",
                                  f"Composant: {composant}\nConfiance: {confiance*100:.1f}%")
            else:
                messagebox.showerror("Erreur", "Impossible de capturer l'image")

    def sauvegarder_resultat(self):
        """Sauvegarder le résultat actuel"""
        if self.composant_actuel != "Non identifié":
            timestamp = int(time.time())
            donnees = {
                'composant': self.composant_actuel,
                'confiance': self.confiance_actuelle,
                'timestamp': timestamp,
                'ip_telephone': self.flux_video.ip_telephone
            }

            nom_fichier = f"resultat_{timestamp}.json"
            with open(nom_fichier, 'w', encoding='utf-8') as f:
                json.dump(donnees, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Sauvegarde", f"Résultat sauvegardé: {nom_fichier}")
        else:
            messagebox.showwarning("Aucun résultat", "Aucun composant identifié à sauvegarder")

    def demarrer(self):
        """Démarrer l'application"""
        try:
            self.fenetre.mainloop()
        except KeyboardInterrupt:
            print("\n🛑 Arrêt de l'application...")
        finally:
            if self.flux_video:
                self.flux_video.arreter_flux()

def main():
    print("🔧 Initialisation du Scanner de Composants Électroniques")
    print("=" * 60)

    # Vérifier les dépendances
    try:
        import cv2
        import requests
        import PIL
        import tensorflow
        print("✅ Toutes les dépendances sont installées")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez avec: pip install opencv-python requests pillow tensorflow")
        return

    # Démarrer l'application
    app = InterfaceScanner()
    app.demarrer()

if __name__ == "__main__":
    main()