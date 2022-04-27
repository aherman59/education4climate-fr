# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 14:59:13 2022

@author: Pierre
"""
#%%
from collections.abc import Iterable

import pandas as pd

courses_path = "d:/programmation/insa/data/crawling-output/insa_strasbourg_courses_2021.json"
programs_path = "d:/programmation/insa/data/crawling-output/insa_strasbourg_programs_2021.json"
scores_path = "d:/programmation/insa/data/scoring-output/insa_strasbourg_courses_scoring_2021.csv"
#%%
df_courses = pd.read_json(courses_path)
df_programs = pd.read_json(programs_path)
df_scores = pd.read_csv(scores_path)
df_scores = df_scores.drop_duplicates()
#%%
df_tableau = df_programs.explode(['courses', 'heures', 'ETCS'])
df_tableau['Etablissement'] = "INSA Strasbourg"

df_tableau.ETCS = df_tableau.ETCS.astype(str)
df_tableau.ETCS = df_tableau.ETCS.apply(lambda x: x.replace('.',','))
df_tableau.rename(columns={'formation':'Filière', 'heures':'Volume horaire'}, inplace=True)
df_tableau['Semestre'] = ""
df_tableau['Parcours'] = ""
df_tableau['Enseignement'] = ""
df_tableau['Obligatoire'] = "x"
tmp = df_tableau.courses.str.split('-')
df_tableau['Nom du cours'] = tmp.apply(lambda x: ' '.join([y for y in x if len(y)>4]) if isinstance(x, Iterable) else "")
df_tableau['Choix/option ? (électif)'] = ""
df_tableau = df_tableau.merge(df_scores, left_on="courses", right_on="id")
df_tableau['Cours dédié ?'] = "N'aborde pas les enjeux"
tmp = (df_tableau.climate+df_tableau.energy+df_tableau.environment+df_tableau.resources+df_tableau.sustainability)
df_tableau.loc[tmp == 1,'Cours dédié ?'] = "Aborde ponctuellement les enjeux"
df_tableau.loc[tmp > 1,'Cours dédié ?'] = "Aborde régulièrement les enjeux"
df_tableau.loc[df_tableau.dedicated,'Cours dédié ?'] = "Dédié"
#%%
df_tableau = df_tableau[['Etablissement', 'Filière', 'Semestre', 'Parcours', 'Obligatoire',
                         'Enseignement', 'Nom du cours', 'Choix/option ? (électif)',
                         'Cours dédié ?', 'Volume horaire', 'ETCS']]


df_tableau.to_excel("d:/programmation/insa/data/strasbourg_scrapper.xlsx", sheet_name = "Données brutes")
#%%
print(pd.get_option("display.width")) #80
print(pd.get_option("display.max_columns")) #0
print(pd.get_option("display.max_colwidth")) #50
print(pd.get_option("display.expand_frame_repr"))
#%%
pd.set_option("display.max_colwidth", 30)
#%%
pd.describe_option()
#%%
