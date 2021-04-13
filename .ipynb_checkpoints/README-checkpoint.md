# py_thesis_toolbox

Main repository : https://gogs.alibellamine.me/alibell/py_thesis_toolbox/

Outils d'analyse des données de thèses.
Applique une description des données suivi d'une série de tests univariés.

## Installation du plugin

```
    git clone https://gogs.alibellamine.me/alibell/py_thesis_toolbox.git
    cd py_thesis_toolbox
    pip install -r requirements.txt
    pip install .
```

## Utilisation

### Analyses d'un jeu de donnée

L'analyse d'un jeu de données procède aux traitements suivant :
- Analyse descriptive : moyenne, nombre de sujet, médiane, intervales inter-quartiles
- Analyse explicative descriptive
- Application de test lors de l'analyse explicative descriptive

**@TODO : Implémenter la création d'un modèle multivariés**

```
    from thesis_analysis import analyseStatistiques

    analyses = analyseStatistiques(df)
    analyses.analyse_univarie(
        variable_interet,
        variables_explicatives
    )
```

#### variable_interet

La variable **variable d'intérêt** comprend un dictionnaire décrivant une liste de variables qualitatives ou quantitative.
Le dictionnaire doit être de la forme :

```
{
    nom_de_variable:type_de_variable["qualitative","quantitative"]
    ...
}
```

#### variables_explicatives

Liste de variables explicatives.
L'ensemble des variables doit être de type qualitatif.
Il s'agit d'une liste :

```
[
    nom_de_variable
    ...
]
```

### Application d'un test spécifique


```
    from thesis_analysis.test import testQualitatif, testQuantitatif

    test = testQualitatif(df, y, x)
    test.best_test()
```

Applique pour un jeu x et y le meilleur test possible.
Paramètres :
- df : DataFrame contenant l'ensemble du jeu de données
- y : variable d'intérêt sur laquelle on mesure l'impact de la variable x
- x : variable dont on mesure l'impact sur y

La fonction **best_test** détermine le meilleur test applicable aux données.

Il est possible d'executer une série de test manuellement.
La liste des test peut être obtenue en éxecutant :

```
    dir(test)
```

### Restitution d'une analyse dans un tableau

```
    from thesis_analysis import analyseStatistiques
    from thesis_analysis import genererTableau
    
    # Analyse du jeu de données
    analyses = analyseStatistiques(df)
    resultat = analyses.analyse_univarie(
        variable_interet,
        variables_explicatives
    )
    
    # Ecriture du tableau
    tableau = genererTableau(resultat)
    tableau.tableau_descriptif("tableau.xlsx", variables, axes, format_sortie = "xlsx") # Tableau descriptif, souvent table 1
    tableau.tableau_detail_variable("tableau.xlsx", variable, axes, format_sortie = "xlsx") # Tableau détaillé : analyse d'une variable
```

#### Types de tableaux

Il existe 2 types de tableau :

- Le tableau descriptif :
    - Il correspond essentiellement au tableau 1 des publications scientifiques. Il décrit un ensemble de variables, chacunes dans une ou plusieurs lignes dédiés, éventuellement croisé avec un ou plusieurs axes (- ie - des variables qualitatives) qui sont représentés dans une ou plusieurs colonnes séparées
    - Il est généré à l'aide de la méthode : tableau_descriptif
- Le tableau détaillé :
    - Il correspond à un tableau détaillé pour une variable, il décrit pour uen variable donnée l'ensemble des caractéristiques en colonnes et pour chaque variables avec laquelle cette axe avec laquelle cette variable est croisé les principaux indicateurs est resulté de test. Ainsi chaque axe est analysé sur une ou plusieurs lignes dédiés.
    - Il est généré à l'aide de la méthode : tableau_detail_variable
    
#### Paramètre de la classe genererTableau

```
    genererTableau(data, precision = 2, quantitative_string_format = "{mean:.2f} +/- {std:.2f} ({n})", qualitative_string_format = "{n} ({p:.2%})")
```

- data : données à afficher, il s'agit d'un dictionnaire produit grace à la classe analyseStatistiques
- precision : degré de précision en décimal des résultats affichés
- quantitative_string_format : format d'affichage des valeurs pour les variable quantitatives dans le tableau descriptif
- qualitative_string_format : format d'affichage des valeurs pour les variable qualitatives dans le tableau descriptif

#### Paramètre de la génération de tableau : méthodes tableau_descriptif et tableau_detail_variable

```
    tableau.tableau_descriptif(chemin = "tableau.xlsx", variables, axes, format_sortie = "xlsx")
    tableau.tableau_detail_variable(chemin = "tableau.xlsx", variable, axes, format_sortie = "xlsx")
```

- chemin : Chemin du fichier de sortie :
    - Ecrit le fichier dans le chemin indiqué
    - Si le chemin prend la valeur None : est renvoyé un buffer : soit un objet StringIO ou BytesIO si un fichier texte ou binaire est généré, soit une liste si le format "raw" est sélectionné
- variables : variables à analyses, la méthode quantitative_string_format analyse plusieurs variables à la fois
- variable (pour tableau_detail_variable) : variable à analyse, la méthode qualitative_string_format n'analyse qu'une seule variable à la fois 
- axes : axes d'analyse à restituer
- format_sortie : format de sortie du tableau, formats attendus :
    - csv
    - tsv
    - xlsx
    - ods
    - raw : si raw est sélectioné, le chemin attendu est None, dans ce cas une liste est directement retourné. Cela peut-être utile pour insérer plusieurs tableaux dans des feuilles différentes d'un même fichier XLSX / ODS.