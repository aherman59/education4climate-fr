# Méthode de scoring des programmes de cours 

Cette petite note récapitule la **méthodologie employée pour évaluer les cours et cursus universitaires** au regard des enjeux climatiques et envirionnementaux dans le cadre du programme Education4Climate porté par The Shifters Belgium.

## Une évaluation selon 5 thématiques principales

Les cours et cursus sont évalués selon **5 thèmes principaux** :

- Climat
- Durablité
- Ressources
- Environnement
- Energie

Pour chacun de ses 5 thèmes, un **lexique composé d'un ensemble d'expressions régulières** est défini. Par exemple :

```
(?:de l')humanite, cycles? bio-?geo-?(?:chimique|physique)]",['climate']
"[impacts? (?:de l'|des )homme, cycles? bio-?geo-?(?:chimique|physique)]",['climate']
"[impacts? (?:de l'|des )industrie, cycles? bio-?geo-?(?:chimique|physique)]",['climate']
"[nucleaire, pollu(?:ant|tion), environnement]","['energy', 'environment']"
"[performances? energ[^ ]+, developp[^ ]+ durab[^ ]+, environnement]",['energy']
"[performances? energ[^ ]+, durabilite, environnement]",['energy']
"[performances? energ[^ ]+, solution durab[^ ]+, environnement]",['energy']
"[plastique, ocean]",['environment']
"[plastique, pollution]",['environment']
"[pollution, aquifere]",['environment']
"[pollution, cours d'eau]",['environment']
"[pollution, ocean]",['environment']``
```

Un **lexique spécifique** est également établi pour évaluer si un **cours est complétement dédié** aux thématiques définies.

```
patterns,themes
atmosphere,'[]'
biodivers[^ ]+,'[]'
biosphere,'[]'
climat[^ ]+,'[]'
durable,'[]'
durabilite,'[]'
economie circulaire,'[]'
economie regenerative,'[]'
ecolo[^ ]+,'[]'
environnement,'[]'
energ[^ ]+,'[]'
regenerative economy,'[]'
resources? naturelles?,'[]'
transition,'[]'
```

## Evaluation d'un cours

Pour chacun des cours, la méthode est la suivante.

- Dès qu'une expression régulière du lexique est détectée dans les éléments/contenus récupérés pour le cours (un paramétrage est possible à ce niveau), une note de 1 est affectée au thème associé.
- Si aucune expression associée à un thème n'est identifiée pour le cours, une note de 0 affectée pour ce thème.

De la même manière si le **nom du cours** contient un élément du lexique spécifique, une note de 1 sera affectée pour ce cours dans un colonne *dedicated*.

Le fichier final des résultats à l'échelle des cours se présente ainsi sous la forme d'un fichier csv :

```
id,climate,energy,environment,resources,sustainability,dedicated
Cours_A,0,1,0,0,0,0
Cours_B,0,0,1,0,0,0
Cours_C,0,0,0,1,0,1
Cours_D,0,0,0,0,0,0
```

A noter qu'un fichier est généré en parallèle pour permettre d'identifier les expressions qui ont été repérées pour chacun des cours et qui ont permis d'établir le scoring.

## Evaluation d'un cursus

Pour chacun des cursus et **sur la base de l'ensemble des notations des cours associés**, la notation s'effectue de la façon suivante :

- Pour chaque thème, **on somme les notes (0 ou 1) de chacun des cours**
- Pour la colonne *dedicaded*, on somme les notes (0 ou 1) des cours "dédiés"
- On ajoute une colonne *total*, qui somme les cours qui ont obtenu une fois la note 1 sur l'un des thèmes.

Le fichier final des résultat à l'échelle des cursus se présente ainsi sous la forme d'un fichier csv :

```
id,climate,energy,environment,resources,sustainability,dedicated,total
CURSUS_1,0,0,0,0,0,0,0
CURSUS_2,0,0,0,0,0,0,0
CURSUS_3,0,0,0,0,0,0,0
CURSUS_4,0,1,3,1,3,2,4
CURSUS_5,0,1,1,1,1,1,1
```