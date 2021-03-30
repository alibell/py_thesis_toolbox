import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact
from scipy.stats import normaltest, kstest, levene, ttest_ind, mannwhitneyu, f_oneway, kruskal
import statsmodels.stats.weightstats as ws

class testQuantitatif ():
    """
        Applique le test qualitatif le plus adapté à partir d'un jeu de données
            df : dataframe contenant les données
            y : variable à tester
            x : variable dont on souhaite mesurer l'impact
    """
    
    def __init__ (self, df, y, x):
        
        # Calcul du tableau de contingence
        self.df = df
        self.x = x
        self.y = y
        
        # On détermines les modalités de x
        self.x_shapes = self.df[x].drop_duplicates()
        
        # On détermine les valeurs de y pour chaque x
        self.y_values = {}
        for x_value in self.x_shapes:
            self.y_values[x_value] = df[
                            df[x] == x_value
                        ][y] \
                        .values
            
        # On détermine les éléments de validités
        self.x_shape = self.x_shapes.shape[0]
        self.n_sup_30 = ((df.groupby(x).count()[y] >= 30).sum() == 2)
        
    def _check_all_group_normal(self):
        
        # Application du test de normalité
        normal_test_result = self.normal_distribution();
        
        # On vérifie que tous les groupes sont distribués normalement
        valid = len([False for x in normal_test_result.values() if x["p_value"] < 0.05]) == 0
        
        return valid
        
    def best_test (self, normal = None):
        
        """
            Selectionne le meilleur test possible
            
            Variable :
                normal : boolean, si True, on suppose une distribution normale sans faire de test de normalité
        """
        
        # Arbre decisionnel
        ## x_shape :
        ### 2 :
        #### N1, N2 >= 30 : Z-test
        #### N1, N2 <= 30 : 
        ##### Distribution de chaque groupe normale ?
        ###### Egalite variance : t-test
        ###### Absence égalité variance : test de welch
        ##### Absence de distribution normale : MWWilcoxon
        ### > 2 :
        #### Egalite variance et distribution normal : ANOVA
        #### Autrement un test de Kruskal Wallis
        
        if self.x_shape == 2:
            if self.n_sup_30:
                # Application du Z-test
                result = self.z_test()
                test_applied = "z_test"
            else:
                # Vérification de la normalité
                if normal or self._check_all_group_normal():
                    # Vérification de l'égalité des variance
                    if self.variance_equity["p_value"] >= 0.05:
                        # On suppose l'égalité de variance : t-test
                        welch = False
                        test_applied = "t_test"
                    else:
                        # On ne suppose pas l'égalité de variance : test de welch
                        welch = True
                        test_applied = "t_test Welch"
                        
                    result = self.t_test(welch)
                else:
                    test_applied = "Mann-Whitney Wilcoxon"
                    result = self.mwwilcoxon()
        else:
            # Vérification de la normalité et de l'égalité de variance
            if (normal or self._check_all_group_normal()) and (self.variance_equity["p_value"] >= 0.05):
                # Anova
                test_applied = "ANOVA_1W"
                result = self.anova_1w()
            else:
                test_applied = "Kurskal_Wallis"
                result = self.kruskal_wallis()
                
        return (test_applied, result)
                
    def _apply_test (self, test_function, params = {}):
        
        # Application du test
        test_result = test_function(*list(self.y_values.values()),
                                **params)
        
        output_result = dict(zip(
            ["statistic","p_value"],
            [test_result.statistic, test_result.pvalue]
        ))
        
        return(output_result)
        
    def normal_distribution (self):
        
        # On applique le test de normalité à chaque catégorie
        norm_test_result = dict(zip(
            self.y_values.keys(),
            [   dict(zip(
                    ["statistic", "p_value"],
                    [x.statistic, x.pvalue]
                ))
                for x in
                [kstest(y_values, "norm") for y_values in self.y_values.values()]         
            ]
        ))
            
        return (norm_test_result)
    
    def z_test (self):
        
        # Application du test
        test_result = ws.ztest(*list(self.y_values.values()))
        
        output_result = dict(zip(
            ["statistic","p_value"],
            list(test_result)
        ))
        
        return(output_result)

    def t_test (self, welch = False):
        
        # Application du test
        output_result = self._apply_test(ttest_ind, {"equal_var":welch})
        
        return(output_result)
    
    def mwwilcoxon (self):
        
        # Application du test
        output_result = self._apply_test(mannwhitneyu)
        
        return(output_result)
    
    def variance_equity (self):
        
        """
            Test de Levene mesuré sur la moyenne
        """
        
        # Application du test
        output_result = self._apply_test(levene,{"center":"mean"})
        
        return(output_result)
    
    def anova_1w (self):
        
        """
            ANOVA - One way : compare la variance de tous les groupes
        """
        
         # On applique le test 
        output_result = self._apply_test(f_oneway)
        
        return(output_result)
        
    def kruskal_wallis (self):
         # On applique le test 
        output_result = self._apply_test(kruskal)
        
        return(output_result)
    
    def _no_test (self):
        """
            Retourne l'absence de test
        """
        
        output_result = {"valid":True}
        
        return output_result