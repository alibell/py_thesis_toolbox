import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact
from scipy.stats import normaltest, kstest, levene, ttest_ind, mannwhitneyu, f_oneway, kruskal
import statsmodels.stats.weightstats as ws

# Qualitatif

class testQualitatif ():
    """
        Applique le test qualitatif le plus adapté à partir d'un jeu de données
            df : jeu de données
            y : variable à tester
            x : variable dont on souhaite mesurer l'impact
    """
    
    def __init__ (self, df, y, x):
        
        # Calcul du tableau de contingence
        self.contingency = self._get_contingency(df, y, x)
        
    def _get_contingency (self, df, y, x):
        
        contingency = pd.DataFrame(
            {"n":df.groupby(x)[y].value_counts()}
        ).reset_index() \
        .pivot_table(index = [x], columns = [y]) \
        .fillna(0)
        contingency.columns = contingency.columns.droplevel(0)
        
        return(contingency.values.astype(int))
        
    def best_test (self):
        
        """
            Selectionne le meilleur test possible
        """
        
        # Ordre de priorité
        ## 1. Khi2
        ## 2. Khi2 - Yates
        ## 3. Student test
        ## 4. Absence de test
        
        order_test = {
            "khi2":[self.khi2,[False]],
            "khi2_yates":[self.khi2,[True]],
            "fisher":[self.fisher,[]],
            "no_test":[self._no_test, []]
        }
        
        ## Application des tests dans l'ordre
        for test_name, test in order_test.items():
            test_result = test[0](*test[1])

            if (test_result["valid"] == True):
                return (test_name, test_result)
        
    def khi2 (self, yates_correction = False):
        """
            Test du Khi-2
            Paramètre :
                yates_correction : Si True, effectue la correction de Yates
        """
        
        # Application du test
        test_result = chi2_contingency(self.contingency, correction=yates_correction)
        
        # Validité du test
        if yates_correction == False:
            khi2_valid = len([True for x in test_result[3] for y in x if y < 5]) == 0
        else:
            khi2_valid = (len([True for x in test_result[3] for y in x if y < 3]) == 0) \
                        & (test_result[2] == 1)
        
        # Structuration du résultat
        output_result = dict(zip(
            ["statistic","p_value", "dof", "theorical_values","observed_values","yates_correction", "valid"],
            list(test_result)+[self.contingency, yates_correction, khi2_valid]
        ))
        
        return output_result
    
    def fisher (self):
        """
            Test de Fisher
        """
        
        # Vérification des CI
        valid = (self.contingency.shape == (2,2))
        
        if (valid == True):
            fisher_result = fisher_exact(self.contingency)
            
            output_result = dict(zip(
                ["statistic", "p_value", "observed_values","valid"],
                list(fisher_result)+[self.contingency, valid]
            ))
        else:
            output_result = {"valid":valid}
            
        return output_result
    
    def _no_test (self):
        """
            Retourne l'absence de test
        """
        
        output_result = {"valid":True}
        
        return output_result