import math
import pandas as pd
from .test import testQualitatif, testQuantitatif

class analyseStatistiques ():
    """
        Permet l'analyse d'un jeu de données.
        Analyses univariés :
            Description des données
            Application des tests

        Input : dataset
    """
    
    def __init__ (self, df):
        # Chargement du dataframe
        self.df = df
        
    def _describe_qualitative (self, data):
        
        """
            Calculate n and p of each modalitie of the qualitative value
            Input : data, Pandas Series containing data to describe
        """
                
        table = data.value_counts()
        description = pd.DataFrame({'n':table, 'p':table/table.sum()}) \
            .to_dict("index")
        description["total"] = table.sum()
        
        return(description)
    
    def _get_sub_table(self, variable, axes):
        
        # On sélectionne les données à analyse
        if (axes is None):
            temp_data = self.df[[variable]]
        else:
            temp_data = self.df[[variable]+axes]
        
        temp_data = temp_data.dropna()
        
        return(temp_data)
        
        
    def _analyse_univarie_qualitative (self, variable, axes = None):
        
        temp_data = self._get_sub_table(variable, [])
        
        # On charge un dictionnaire vide
        analyse = {}
        
        analyse["n"] = temp_data.shape[0]

        ## Globale : en dehors de l'axe d'analyse
        analyse["global"] = self._describe_qualitative(temp_data[variable])

        ## Spécifique : Dans les axes d'analyse
        if (axes is not None):
                
            analyse["sous_groupes"] = {}
            analyse["test"] = {}
            
            for axe in axes:  
                
                temp_data = self._get_sub_table(variable, [axe])
                
                # Axe values
                axe_values = temp_data[axe] \
                    .drop_duplicates().values.tolist()
                
                # Description
                analyse["sous_groupes"][axe] = {}
                for values in axe_values:
                    analyse["sous_groupes"][axe][values] = self._describe_qualitative(
                        temp_data[
                            temp_data[axe] == values
                        ] \
                        .reset_index(drop = True)[variable]
                    )

                # Test statistique
                analyse["test"][axe] = testQualitatif(temp_data, variable,axe).best_test()

        analyse["type"] = "qualitative"

        return analyse
    
    def _describe_quantitative (self, data):
        """
            Calculate mean, median, Q25, 50, 27, std, std_mean and CI for quantitative data
            Input : data, Pandas Series containing data to describe
        """
        
        # Dict containing data
        description = {}
        
        description["n"] = data.shape[0]
        description["mean"] = data.mean()
        description["median"] = data.median()
        description["Q25"] = data.quantile(0.25)
        description["Q75"] = data.quantile(0.75)
        description["std"] = data.std()
        description["std_mean"] = description["std"]/math.sqrt(description["n"])
        description["ci_95"] = [description["mean"]-1.96*description["std_mean"], 
                                description["mean"]+1.96*description["std_mean"]]        
        
        return description
    
    def _analyse_univarie_quantitative (self, variable, axes = None):
        
        # On sélectionne les données à analyse
        temp_data = self._get_sub_table(variable, [])
        
        # On charge un dictionnaire vide
        analyse = {}
        
        analyse["n"] = temp_data.shape[0]

        ## Globale : en dehors de l'axe d'analyse
        analyse["global"] = self._describe_quantitative(temp_data[variable])
                
        ## Spécifique : Dans les axes d'analyse
        if (axes is not None):
                
            analyse["sous_groupes"] = {}
            analyse["test"] = {}

            for axe in axes:  
                
                temp_data = self._get_sub_table(variable, [axe])
                
                # Axe values
                axe_values = temp_data[axe] \
                    .drop_duplicates().values.tolist()
                
                # Description
                analyse["sous_groupes"][axe] = {}
                for values in axe_values:
                    analyse["sous_groupes"][axe][values] = self._describe_quantitative(
                        temp_data[
                            temp_data[axe] == values
                        ] \
                        .reset_index(drop = True)[variable]
                    )

                # Test statistique
                analyse["test"][axe] = testQuantitatif(temp_data, variable,axe).best_test()

        analyse["type"] = "quantitative"

        return analyse
        
    def analyse_univarie (self, variables, axes = None):
        """
            Analyse descriptive univariée
                variable : dictionnaire contenant la liste des variables à analyser de la forme :
                    Key = Nom de la variable, Value : type de variable : quantitative ou qualitative
                axes : axes d'analyse de la variable, doivent être de type qualitative. Liste de variables.                
        """
                
        # Sortie des résultats
        resultats = {}
        
        for variable, type_variable in variables.items():
            if type_variable == 'qualitative':
                resultats[variable] = self._analyse_univarie_qualitative(variable, axes)
            elif type_variable == 'quantitative':
                resultats[variable] = self._analyse_univarie_quantitative(variable, axes)                
                
        return(resultats)