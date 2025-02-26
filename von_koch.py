"""
Application graphique permettant de visualiser et manipuler un flocon de Von Koch.

Cette application permet de:
- Afficher un flocon de Von Koch avec un niveau de récursion configurable
- Zoomer/dézoomer avec la molette de souris ou les boutons +/-
- Se déplacer dans la vue en faisant glisser la souris 
- Modifier le niveau de récursion avec des boutons dédiés

Le flocon de Von Koch est une figure fractale construite en remplaçant récursivement
chaque segment d'un triangle équilatéral par 4 segments formant une pointe.
"""

import tkinter as tk
import math
import platform

class VonKochApp:
    """
    Application principale pour visualiser le flocon de Von Koch.
    
    Attributes:
        TAILLE_FLOCON (int): Taille de base du flocon en pixels
        NIVEAU_RECURSION (int): Niveau de récursion initial du flocon (plus le niveau est élevé, plus le flocon est détaillé)
    """
    
    TAILLE_FLOCON = 600
    NIVEAU_RECURSION = 4
    
    def __init__(self, root):
        """
        Initialise l'application avec l'interface graphique et les contrôles.

        Args:
            root: Fenêtre principale Tkinter
        """
        self.root = root
        self.root.title("Flocon de Von Koch")
        
        # Configuration du canvas principal
        self.canvas_width = 1000
        self.canvas_height = 800
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Variables pour gérer le zoom et le déplacement
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.dragging = False
        self.last_x = 0
        self.last_y = 0
        
        self.niveau = self.NIVEAU_RECURSION
        
        # Détection du système d'exploitation pour adapter les contrôles
        self.os = platform.system()
        
        # Création de la barre d'information en bas de la fenêtre
        self.info_frame = tk.Frame(root)
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.info_zoom = tk.Label(self.info_frame, text=f"Zoom: {self.zoom:.2f}x", font=("Arial", 10))
        self.info_zoom.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.instructions = tk.Label(self.info_frame, 
                         text="Navigation: Clic gauche + déplacer | Zoom: Molette de souris",
                         font=("Arial", 10))
        self.instructions.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Configuration des événements souris pour le déplacement
        self.canvas.bind("<ButtonPress-1>", self.commencer_deplacement)
        self.canvas.bind("<B1-Motion>", self.deplacer)
        self.canvas.bind("<ButtonRelease-1>", self.arreter_deplacement)
        
        # Configuration des événements de zoom selon le système d'exploitation
        if self.os == "Windows":
            self.canvas.bind("<MouseWheel>", self.zoomer_windows)
        elif self.os == "Darwin":
            self.canvas.bind("<MouseWheel>", self.zoomer_macos)
        else:
            self.canvas.bind("<Button-4>", self.zoomer_in_linux)
            self.canvas.bind("<Button-5>", self.zoomer_out_linux)
        
        # Raccourcis clavier pour le zoom
        self.root.bind("<plus>", lambda e: self.zoomer_clavier(True))
        self.root.bind("<minus>", lambda e: self.zoomer_clavier(False))
        
        self.dessiner_flocon()
        
        # Création des boutons de contrôle du zoom
        boutons_frame = tk.Frame(self.info_frame)
        boutons_frame.pack(side=tk.LEFT, padx=20)
        
        zoom_in_btn = tk.Button(boutons_frame, text="+", command=lambda: self.zoomer_clavier(True))
        zoom_in_btn.pack(side=tk.LEFT, padx=5)
        
        zoom_out_btn = tk.Button(boutons_frame, text="-", command=lambda: self.zoomer_clavier(False))
        zoom_out_btn.pack(side=tk.LEFT, padx=5)
        
        # Affichage du niveau de récursion actuel
        self.info_niveau = tk.Label(self.info_frame, text=f"Niveau: {self.niveau}", font=("Arial", 10))
        self.info_niveau.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Création des boutons de contrôle du niveau de récursion
        niveau_frame = tk.Frame(self.info_frame)
        niveau_frame.pack(side=tk.LEFT, padx=20)
        
        niveau_down_btn = tk.Button(niveau_frame, text="Niveau -", command=lambda: self.changer_niveau(-1))
        niveau_down_btn.pack(side=tk.LEFT, padx=5)
        
        niveau_up_btn = tk.Button(niveau_frame, text="Niveau +", command=lambda: self.changer_niveau(1))
        niveau_up_btn.pack(side=tk.LEFT, padx=5)
    
    def calculer_points_koch(self, x1, y1, x2, y2, niveau):
        """
        Calcule récursivement les points formant le motif de Von Koch.
        Pour chaque segment, crée 4 nouveaux segments formant une pointe.

        Args:
            x1, y1: Coordonnées du point de départ
            x2, y2: Coordonnées du point d'arrivée
            niveau: Niveau de récursion actuel

        Returns:
            list: Liste des points [(x,y)] formant le motif
        """
        if niveau == 0:
            return [(x1, y1), (x2, y2)]
        
        # Calcul du vecteur directeur et de sa longueur
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        
        # Calcul des points du motif de Koch
        p1_x = x1 + dx/3
        p1_y = y1 + dy/3
        
        p3_x = x1 + 2*dx/3
        p3_y = y1 + 2*dy/3
        
        # Point formant la pointe (rotation de 60° par rapport au segment)
        p2_x = p1_x + distance/3 * math.cos(angle + math.pi/3)
        p2_y = p1_y + distance/3 * math.sin(angle + math.pi/3)
        
        # Appels récursifs pour chaque nouveau segment
        segment1 = self.calculer_points_koch(x1, y1, p1_x, p1_y, niveau-1)
        segment2 = self.calculer_points_koch(p1_x, p1_y, p2_x, p2_y, niveau-1)
        segment3 = self.calculer_points_koch(p2_x, p2_y, p3_x, p3_y, niveau-1)
        segment4 = self.calculer_points_koch(p3_x, p3_y, x2, y2, niveau-1)
        
        # Combine les segments en évitant les points en double
        result = segment1[:-1] + segment2[:-1] + segment3[:-1] + segment4
        
        return result
    
    def dessiner_flocon(self):
        """Dessine le flocon complet sur le canvas avec les paramètres actuels."""
        self.canvas.delete("all")
        
        taille = self.TAILLE_FLOCON * self.zoom
        
        # Calcule le centre de la vue en tenant compte du déplacement
        centre_x = self.canvas_width / 2 + self.pan_x
        centre_y = self.canvas_height / 2 + self.pan_y
        
        # Calcule les dimensions du triangle équilatéral de base
        hauteur = taille * math.sqrt(3) / 2
        
        # Calcule les trois sommets du triangle
        x1 = centre_x
        y1 = centre_y - hauteur/2
        
        x2 = centre_x - taille/2
        y2 = centre_y + hauteur/2
        
        x3 = centre_x + taille/2
        y3 = centre_y + hauteur/2
        
        # Calcule les points pour chaque côté du triangle
        points_cote1 = self.calculer_points_koch(x1, y1, x2, y2, self.niveau)
        points_cote2 = self.calculer_points_koch(x2, y2, x3, y3, self.niveau)
        points_cote3 = self.calculer_points_koch(x3, y3, x1, y1, self.niveau)
        
        # Combine tous les points en évitant les doublons
        tous_points = []
        tous_points.extend(points_cote1[:-1])
        tous_points.extend(points_cote2[:-1])
        tous_points.extend(points_cote3[:-1])
        
        # Convertit la liste de points en liste plate pour create_polygon
        points_plats = [coord for point in tous_points for coord in point]
        
        # Dessine le flocon
        self.canvas.create_polygon(points_plats, outline="white", fill="", width=2)
        
        # Met à jour l'affichage du zoom
        self.info_zoom.config(text=f"Zoom: {self.zoom:.2f}x")
    
    def commencer_deplacement(self, event):
        """Initialise le déplacement du flocon."""
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y
    
    def deplacer(self, event):
        """Gère le déplacement continu du flocon."""
        if self.dragging:
            # Calcule le déplacement depuis la dernière position
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            
            # Met à jour la position
            self.pan_x += dx
            self.pan_y += dy
            
            # Mémorise la position actuelle
            self.last_x = event.x
            self.last_y = event.y
            
            # Redessine le flocon
            self.dessiner_flocon()
    
    def arreter_deplacement(self, event):
        """Termine le déplacement du flocon."""
        self.dragging = False
    
    def zoomer_windows(self, event):
        """Gère le zoom sur Windows."""
        factor = 1.0 + (event.delta / 1200.0)
        self.zoom *= factor
        self.zoom = max(0.1, min(50.0, self.zoom))
        self.dessiner_flocon()
    
    def zoomer_macos(self, event):
        """Gère le zoom sur macOS."""
        factor = 1.0 + (event.delta / 120.0)
        self.zoom *= factor
        self.zoom = max(0.1, min(50.0, self.zoom))
        self.dessiner_flocon()
    
    def zoomer_in_linux(self, event):
        """Gère le zoom avant sur Linux."""
        self.zoom *= 1.1
        self.zoom = min(50.0, self.zoom)
        self.dessiner_flocon()
    
    def zoomer_out_linux(self, event):
        """Gère le zoom arrière sur Linux."""
        self.zoom /= 1.1
        self.zoom = max(0.1, self.zoom)
        self.dessiner_flocon()
    
    def zoomer_clavier(self, zoom_in):
        """
        Gère le zoom via le clavier.
        
        Args:
            zoom_in (bool): True pour zoomer, False pour dézoomer
        """
        if zoom_in:
            self.zoom *= 1.2
        else:
            self.zoom /= 1.2
        
        self.zoom = max(0.1, min(50.0, self.zoom))
        self.dessiner_flocon()
        
    def changer_niveau(self, delta):
        """
        Change le niveau de récursion du flocon.
        
        Args:
            delta (int): Valeur à ajouter au niveau actuel (+1 ou -1)
        """
        self.niveau += delta
        self.niveau = max(0, min(7, self.niveau))
        self.info_niveau.config(text=f"Niveau: {self.niveau}")
        self.dessiner_flocon()


if __name__ == "__main__":
    root = tk.Tk()
    app = VonKochApp(root)
    root.mainloop()