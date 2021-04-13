from io import StringIO, BytesIO
import pyexcel as pe
import csv 
import math

class genererTableau ():
    
    """
        ecrire_tableau :
        Permet de créer un tableau et l'exporter au format excel, ods ou csv à partir de données d'analyses.
        
        Input :
            data : données aggrégées généré par les méthodes de analyseStatistiques
            precision : nombre de décimales de précision
            quantitative_string_format : format d'écriture de la moyenne, écart type et taille d'échantillon des variables quantitatives
            qualitative_string_format : format d'écriture du n et de la proportion des variables qualitatives
    """
    
    def __init__ (self, data, precision = 2, quantitative_string_format = "{mean:.2f} +/- {std:.2f} ({n})", qualitative_string_format = "{n} ({p:.2%})"):
        
        """
            Data : data contenant les données aggrégées, généré par analyseStatistiques.analyse_univarie
        """
        
        # Parametres
        self.quantitative_string_format = quantitative_string_format
        self.qualitative_string_format = qualitative_string_format
        self.absence_test = "Absence de test effectué (CI des tests conventionnels non remplis)"
        self.precision = precision
        
        self.data = data
        self.liste_variables = list(data.keys()) # Liste des variables analysables
        self.liste_axes = list(list(data.values())[0]["sous_groupes"].keys()) # Liste des axes d'analyses
        
        # On récupère la liste des modalités de chaque axes
        self.liste_modalites = dict(zip(
            self.liste_axes,
            [self._obtenir_modalite_axe(x, True) for x in self.liste_axes]
        ))
        
        # On récupère la liste des modalités de chaque variable
        self.liste_modalites_variables = dict(zip(
            self.liste_variables,
            [self._obtenir_modalite_variable(x, True) for x in self.liste_variables]
        ))
        
    def _generer_texte_propre (self, texte):
        """
            Nettoie un texte
            Si il s'agit d'un flottant : le met en int
        """
        
        if type(texte) != type(str()):
            texte = str(int(texte))
            
        return(texte)
        
    def _generer_str_mean_std_n(self, mean, std, n):
        
        """
            Simple fonction qui écrit un string mélangeant moyenne, écart-type et taille de l'effectif
            Format par défault :
                {mean:.2f} +/- {std:.2f} ({n})
                
            Peut-être personalisé par le paramètre string_format.
            
            Input :
                mean, std et n
        """
        
        texte = self.quantitative_string_format.format(
            mean = round(mean, self.precision), 
            std=round(std, self.precision), 
            n=round(n, self.precision)
        )
        
        return(texte)
    
    def _generer_str_n_p(self, n, p):
        
        """
            Simple fonction qui écrit un string mélangeant moyenne, écart-type et taille de l'effectif
            Format par défault :
                {n} ({p:.0%})
                
            Peut-être personalisé par le paramètre string_format.
            
            Input :
                mean, std et n
            Sortie :
                texte
        """
        
        texte = self.qualitative_string_format.format(
            p = round(p, self.precision), 
            n = round(n, self.precision)
        )
        
        return(texte)
    
    def _generer_str_valeur(self, valeur):
        
        """
            Simple fonction qui écrit un string à partir d'une valeur
                            
            Input :
                valeur
            Sortie :
                texte
        """
        
        texte = "{}".format(
            round(valeur, self.precision)
        )
        
        return(texte)
    
    def _generer_str_ci(self, liste_ci):
        
        """
            Simple fonction qui écrit un string à partir d'une liste représentant un intervale de confiance
                            
            Input :
                liste_ci : liste de 2 items décrivant un intervalle de confiance
            Sortie :
                texte
        """
        
        texte = "{}-{}".format(
            self._generer_str_valeur(liste_ci[0]),
            self._generer_str_valeur(liste_ci[1])
        )
        
        return(texte)
    
    def _generer_str_resultat_test(self, test):
        
        """
            Génère une liste avec formatage textuel du résultat d'un test
            Vérifie la bonne application du test avant.
            
            Input :
                test : liste contenant le résultat du test
            Sortie :
                liste de 3 éléments comprenant : Test, Paramètre et p
        """
        
        resultat = []
        
        if len(test[1].keys()) > 1:
            resultat.append(test[0]) # Nom du test
            resultat.append(self._generer_str_valeur(test[1]["statistic"])) # Paramètre de test
            resultat.append(self._formater_p_value(test[1]["p_value"])) # Petit p du test
        else:
            resultat.append(self.absence_test)
            resultat = resultat + ["", ""]
            
        return(resultat)
    
    def _formater_p_value(self, p_value):
    
        # Nombre de décimales concernées
        n_digit = len(str(p_value).split(".")[-1].split("0"))

        borne_basse = 5*math.pow(10, -n_digit)
        borne_sup = math.pow(10, -n_digit+1)

        estimation_p = borne_basse if p_value <= borne_basse else borne_sup

        # Affichage
        if p_value > 0.01:
            formated_p_value = str(round(p_value, 3))
        else:
            if p_value > 0.001:
                formated_p_value = "< "+str(estimation_p)
            else:
                formated_p_value = "< 10^"+str(n_digit-1)    

        return(formated_p_value)
        
    def _verifier_existence_variables(self, variables):
        
        """
           Vérifie que les variables existent bien dans le jeu de données.
           Input : variables : liste des variables à tester
           Output : None
        """
        
        variables_manquantes = [x for x in variables if x not in self.liste_variables]
            
        if len(variables_manquantes) > 0:
            raise Exception("Erreur, les variables {} sont inexistantes des données aggrégées.".format(
                ", ".join(variables_manquantes)
            ))
            
    def _verifier_existence_axes(self, axes):
        
        """
           Vérifie que les axes existent bien dans le jeu de données.
           Input : variables : liste des axes à tester
           Output : None
        """
        
        if axes is not None:
            axes_manquants = [x for x in axes if x not in self.liste_axes]
        else:
            axes_manquants = []
            
        if len(axes_manquants) > 0:
            raise Exception("Erreur, les axes {} sont inexistantes des données aggrégées.".format(
                ", ".join(axes_manquants)
            ))
            
    def _obtenir_modalite_axe (self, axe, ajouter_nom = True):
        
        """
            Retourne une liste contenant toutes les modalités pour un axe donné
            Input :
                axe : nom de l'axe à analyse
                ajouter_nom : Si True, alors le nom de l'axe est ajouté à la modalité (concaténation)
        """
        
        # Liste des modalités
        modalites = list(self.data.values())[0]["sous_groupes"][axe].keys()
        
        # Post-traitement : on corrige les float et boolean pour les afficher en int
        modalites = [int(x) if type(x) != type(str()) else x for x in modalites]
        
        # On affiche le nom de l'axe avec si nécessaire
        modalites_avec_str = [axe+" "+str(x) for x in modalites]
        
        if ajouter_nom:
            return(modalites_avec_str)
        else:
            return(modalites)
        
    def _obtenir_modalite_variable (self, variable, ajouter_nom = True):
        
        """
            Retourne une liste contenant toutes les modalités pour une variable donnée
            Input :
                variable : nom de la variable à analyser
                ajouter_nom : Si True, alors le nom de l'axe est ajouté à la modalité (concaténation)
        """
        
        # Liste des modalités
        modalites = [x for x in list(self.data[variable]["global"].keys()) if x != "total"]
        
        # Post-traitement : on corrige les float et boolean pour les afficher en int
        modalites = [int(x) if type(x) != type(str()) else x for x in modalites]
        
        # On affiche le nom de l'axe avec si nécessaire
        modalites_avec_str = [axe+" "+str(x) for x in modalites]
        
        if ajouter_nom:
            return(modalites_avec_str)
        else:
            return(modalites)
            
    def _generer_en_tete_descriptif(self, axes):
        
        """
            Genere l'en-tête d'un tableau Descriptif
            Input :
                axes : liste des axes d'analyse
            Output : None
        """
        
        # Initialisation de l'en-tête
        en_tete = ["","",""]
        
        # Lecture des axes
        for axe in axes:
            en_tete = en_tete+self.liste_modalites[axe]+["Test","Paramètre", "p"]
            
        return en_tete
    
    def _generer_en_tete_detail(self, variable):
        
        """
            Genere l'en-tête d'un tableau Descriptif
            Input :
                axes : liste des axes d'analyse
            Output : None
        """
        
        # Type de variable
        type_variable = self.data[variable]["type"]
        
        # Initialisation de l'en-tête
        en_tete = []
        
        en_tete.append(variable) # Nom de la variable
        en_tete.append("") # Espace technique
        
        ## Pour les variables quantitatives
        if type_variable == "quantitative":
            en_tete = en_tete + ["n", "mean", "std", "IC 95%"]
        elif type_variable == "qualitative":
            en_tete.append("n")
            en_tete = en_tete + self.liste_modalites_variables[variable]
        
        en_tete = en_tete + ["Test", "Parameter", "p"]
            
        return en_tete
    
    def _generer_lignes_descriptif (self, variable, axes):
        
        """
            Genere des ligne d'analyse d'un tableau descriptif pour une variable
            Input :
                variable : nom de la variable
                axes : axes sur lesquels générer la ligne
        """
        
        lignes = []
        
        if self.data[variable]["type"] == "quantitative":
            # Ligne d'une variable quantitative : une seule ligne
            
            ligne = [] # On instancie la ligne
            ligne.append(variable+" mean +/- std (n)") # Ajout du nom de variable
            ligne.append("") # Espace vide, technique
            ligne.append(self._generer_str_mean_std_n(
                self.data[variable]["global"]["mean"],
                self.data[variable]["global"]["std"],
                self.data[variable]["global"]["n"]
            )) # Données globales
            
            # Données liées à chaque axe
            for axe in axes:
                
                donnees_axe = self.data[variable]["sous_groupes"][axe]
                # Pour chaque valeur de l'axe
                for valeur in donnees_axe.keys():
                    
                    ligne.append(self._generer_str_mean_std_n(
                        donnees_axe[valeur]["mean"],
                        donnees_axe[valeur]["std"],
                        donnees_axe[valeur]["n"]
                    )) # Données hors test
                
                ligne = ligne + self._generer_str_resultat_test(self.data[variable]["test"][axe]) # Données du test
                
            lignes.append(ligne)
        else:
            # Lignes d'un variable qualitative : une ligne par modalité
            
            ## On écrit la première ligne : nom de variable et test
            ligne = [] # On instancie la ligne
            ligne.append(variable+" no. (%)") # Nom de variable
            ligne = ligne + ["", ""] # Variable vides
            
            # Données liées à chaque axe
            for axe in axes:
                
                blank_list = ["" for x in range(len(self.liste_modalites[axe]))]
                
                ligne = ligne + blank_list # Blanc lié aux tests
                ligne = ligne + self._generer_str_resultat_test(self.data[variable]["test"][axe]) # Données du test
                
            lignes.append(ligne)
            
            ## On écrit les lignes propres à chaque variable
            
            liste_labels = self.data[variable]["global"].keys()
            
            for label in liste_labels:
                                
                # On ignore le label total
                if label != "total":
                    
                    ligne = []
                    
                    ligne.append("") # Première ligne vide
                    ligne.append(self._generer_texte_propre(label)) # Libelé analysé   
                    ligne.append(self._generer_str_n_p(
                        n = self.data[variable]["global"][label]["n"], 
                        p = self.data[variable]["global"][label]["p"]
                    )) # Données générales
                    
                    # Valeur par axe
                    for axe in axes:
                        
                        liste_valeurs = list(self.data[variable]["sous_groupes"][axe].keys())
                        
                        # Pour chaque valeur de l'axe
                        for valeur in liste_valeurs: # On met 0 si la valeur n'existe pas
                            
                            donnees_axe = self.data[variable]["sous_groupes"][axe][valeur]
                                
                            n = donnees_axe[label]["n"] if label in donnees_axe.keys() else 0
                            p = donnees_axe[label]["p"] if label in donnees_axe.keys() else 0

                            ligne.append(self._generer_str_n_p(
                                n = n, 
                                p = p
                            )) # Données spécifique à chaque axe
                    
                    ligne = ligne + ["", "", ""] # Espaces vides entre 2 axes

                lignes.append(ligne)
        
        return(lignes)
    
    def _generer_lignes_detail(self, variable, axe = None):
        
        """
            Genere des ligne d'analyse d'un tableau détaillé pour une variable
            Input :
                variable : nom de la variable
                axe : axe sur lesquels générer les ligne
        """        
    
        lignes = []
        
        if self.data[variable]["type"] == "quantitative":
            # Génération de la ligne simple
            if axe is None:
                ligne = [] # On instancie la ligne
                ligne = ligne + ["", ""] # Blanc technique
                ligne.append(self._generer_str_valeur(self.data[variable]["global"]["n"])) # Taille d'échantillon
                ligne.append(self._generer_str_valeur(self.data[variable]["global"]["mean"])) # Moyenne
                ligne.append(self._generer_str_valeur(self.data[variable]["global"]["std"])) # Ecart type
                ligne.append(self._generer_str_ci(self.data[variable]["global"]["ci_95"])) # IC à 95%
                ligne = ligne + ["", "", ""] # Blanc technique
                
                lignes.append(ligne)
            else:
                # On vérifie l'axe
                self._verifier_existence_axes([axe])
                
                # Données sur l'axe
                donnees_axe = self.data[variable]["sous_groupes"][axe]
                
                # On écrit le nom de l'axe
                ligne = []
                ligne.append(axe) # Nom de l'axe
                ligne = ligne + ["","","","",""]
                
                # Résultat du test
                ligne = ligne + self._generer_str_resultat_test(self.data[variable]["test"][axe])
                
                lignes.append(ligne)
                
                # On parcours toutes les modalités de l'axe
                for valeur_axe in donnees_axe.keys():
                    
                    ligne = []
                    
                    ligne.append("") # Ligne blanche technique
                    ligne.append(self._generer_texte_propre(valeur_axe)) # Valeur sur l'axe
                    ligne.append(self._generer_str_valeur(donnees_axe[valeur_axe]["n"])) # Taille d'échantillon
                    ligne.append(self._generer_str_valeur(donnees_axe[valeur_axe]["mean"])) # Moyenne
                    ligne.append(self._generer_str_valeur(donnees_axe[valeur_axe]["std"])) # Ecart type
                    ligne.append(self._generer_str_ci(donnees_axe[valeur_axe]["ci_95"])) # IC à 95%
                    
                    ligne = ligne + ["", "", ""] # Blanc technique
                    lignes.append(ligne)
        else:
            # Génération de la ligne simple
                        
            if axe is None:
                ligne = [] # On instancie la ligne
                ligne = ligne + ["", ""] # Blanc technique
                ligne.append(self._generer_str_valeur(self.data[variable]["global"]["total"])) # Taille d'échantillon
                for variable_valeur in self.data[variable]["global"].keys():
                    if variable_valeur != "total":
                        ligne.append(self._generer_str_n_p(
                                n = self.data[variable]["global"][variable_valeur]["n"], 
                                p = self.data[variable]["global"][variable_valeur]["p"]
                            ))
                ligne = ligne + ["", "", ""] # Blanc technique
                
                lignes.append(ligne)
                
            else:
                # On vérifie l'axe
                self._verifier_existence_axes([axe])
                
                # Données sur l'axe
                donnees_axe = self.data[variable]["sous_groupes"][axe]
                
                # On écrit le nom de l'axe
                ligne = []
                ligne.append(axe) # Nom de l'axe
                ligne = ligne + ["",""] + ["" for x in range(len(self.liste_modalites_variables[variable]))] # Blanc technique
                
                # Résultat du test
                ligne = ligne + self._generer_str_resultat_test(self.data[variable]["test"][axe])
                
                lignes.append(ligne)
                
                # On parcours toutes les modalités de l'axe
                for valeur_axe in donnees_axe.keys():
                    
                    ligne = []
                    
                    ligne.append("") # Ligne blanche technique
                    ligne.append(self._generer_texte_propre(valeur_axe)) # Valeur sur l'axe
                    ligne.append(self._generer_str_valeur(donnees_axe[valeur_axe]["total"])) # Taille d'échantillon
                    
                    for variable_valeur in donnees_axe[valeur_axe].keys():
                        if variable_valeur != "total":
                            ligne.append(self._generer_str_n_p(
                                    n = donnees_axe[valeur_axe][variable_valeur]["n"], 
                                    p = donnees_axe[valeur_axe][variable_valeur]["p"]
                                )) 
                    
                    ligne = ligne + ["", "", ""] # Blanc technique
                    lignes.append(ligne)
            
        return lignes
    
    def _generer_sortie (self, chemin, tableau, format_fichier):
        
        """
            Génère le fichier de sortie
                input :
                    chemin : chemin du fichier de sortie
                    tableau : liste contenant les lignes à écrire
                    format_fichier : format du fichier de sortie
                output :
                    si chemin textuel : aucune sortie, écriture du fichier
                    si chemin du fichier vaut None : retour du stream
        """
        
        # Création du fichier
        if format_fichier in ["csv", "tsv"]:
            f = StringIO()
        elif format_fichier in ["ods", "xlsx"]:
            f = BytesIO()
            
        # Ecriture du fichier en stream
        if format_fichier == 'csv':
            csv.writer(f, delimiter = ",").writerows(tableau)
        elif format_fichier == 'tsv':
            csv.writer(f, delimiter = "\t").writerows(tableau)
        elif format_fichier in ['ods','xlsx']:
            sheet = pe.Sheet(data)
            f = sheet.save_to_memory(format_fichier, f)
        elif format_fichier == 'raw':
            f = tableau
        else:
            raise Exception("Format de sortie non supporté.")
            
        if type(chemin) == type(str()):
            # On écrit le fichier
            if format_fichier in ["csv", "tsv"]:
                fichier_sortie = open(chemin, "w")
            else:
                fichier_sortie = open(chemin, "wb")
            
            fichier_sortie.write(file)
        else:
            # On renvoie le buffer
            return (f)

            
    def tableau_descriptif (self, chemin, variables, axes = None, format_sortie = "csv"):
        
        """
            Décrit le contenu de plusieurs variables selon un axe ou plusieurs axes donnés.
            L'axe correspond forcément à une variable qualitative.
            
            Input :
                chemin : chemin du fichier de sortie
                variables : liste des variables à traiter
                axes : liste des axes d'analyse
                format_sortie :
                    'tsv' pour un tableau séparé par une tabulation
                    'csv' pour un tableau séparé par une virgule
                    'ods' pour un fichier ods
                    'xlsx' pour un fichier xlsx
                    'raw' pour un envoie brut des données (liste python)
            Output :
                si chemin textuel : aucune sortie, écriture du fichier
                si chemin du fichier vaut None : retour du stream
        """
        
        # Vérification que toutes les variables et axes existent
        self._verifier_existence_variables(variables)
        self._verifier_existence_axes(axes)
        
        # Récupération des donnée
        
        # Génération de l'en-tête
        en_tete = self._generer_en_tete_descriptif(axes)
        
        # Création du tableau
        tableau = []
        tableau.append(en_tete)
        
        # Traitement des variables une à une
        for variable in variables:
            
            lignes = self._generer_lignes_descriptif(variable, axes)
            tableau = tableau+lignes
            
        # Generation de la sortie
        sortie = self._generer_sortie(chemin, tableau, format_sortie)
        
        return(sortie)
    
    def tableau_detail_variable (self, chemin, variable, axes = None, format_sortie = "csv"):
        
        """
            Décrit le contenu d'une variable selon un axe ou plusieurs axes donnés.
            Les axes correspondent forcément à des variable qualitatives.
            
            Input :
                chemin : chemin du fichier de sortie
                variable : nom de la variable à traiter
                axes : liste des axes d'analyse
                format_sortie :
                    'tsv' pour un tableau séparé par une tabulation
                    'csv' pour un tableau séparé par une virgule
                    'ods' pour un fichier ods
                    'xlsx' pour un fichier xlsx
                    'raw' pour un envoi brut des données pythons
            Output :
                si chemin textuel : aucune sortie, écriture du fichier
                si chemin du fichier vaut None : retour du stream
        """
        
        # Vérification que toutes les variables et axes existent
        self._verifier_existence_variables([variable])
        self._verifier_existence_axes(axes)
        
        # Récupération des donnée
        
        # Génération de l'en-tête
        en_tete = self._generer_en_tete_detail(variable)
                
        # Création du tableau
        tableau = []
        tableau.append(en_tete)
        
        # On génère la première ligne d'analyse
        tableau = tableau + self._generer_lignes_detail(variable, None)
        
        # Ligne vide
        tableau.append(["" for x in range(len(tableau[-1]))])
        
        # Ajout des axes
        for axe in axes:
            tableau = tableau + self._generer_lignes_detail(variable, axe)
        
        return(tableau)