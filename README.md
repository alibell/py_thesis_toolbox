# py_thesis_toolbox

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