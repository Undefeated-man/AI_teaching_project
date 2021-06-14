from django.test import TestCase
import pandas as pd
import numpy as np
from .models import *

# Create your tests here.
# read from the excel tables
lectureExcel_2 = pd.read_excel('./Lectures/lecture2.xlsx')
lectureExcel_3 = pd.read_excel('./Lectures/lecture3.xlsx')
lectureExcel_4 = pd.read_excel('./Lectures/lecture4.xlsx')
lectureExcel_5 = pd.read_excel('./Lectures/lecture5.xlsx')
lectureExcel_6 = pd.read_excel('./Lectures/lecture6.xlsx')
lectureExcel_7 = pd.read_excel('./Lectures/lecture7.xlsx')
lectureExcel_8 = pd.read_excel('./Lectures/lecture8.xlsx')
lectureExcel_9 = pd.read_excel('./Lectures/lecture9.xlsx')
lectureExcel_10 = pd.read_excel('./Lectures/lecture10.xlsx')
lectureExcel_11 = pd.read_excel('./Lectures/lecture11.xlsx')

# to generate a list with all the concept in all excels
conceptList = lectureExcel_2['Concept'].tolist() + lectureExcel_3['Concept'].tolist() + \
              lectureExcel_4['Concept'].tolist() + lectureExcel_5['Concept'].tolist() + \
              lectureExcel_6['Concept'].tolist() + lectureExcel_7['Concept'].tolist() + \
              lectureExcel_8['Concept'].tolist() + lectureExcel_9['Concept'].tolist() + \
              lectureExcel_10['Concept'].tolist() + lectureExcel_11['Concept'].tolist()

# to generate a list with all the sub-concept 1 in all excels
subConceptList_1 = lectureExcel_2['Sub-Concept 1'].tolist() + lectureExcel_3['Sub-Concept 1'].tolist() + \
                   lectureExcel_4['Sub-Concept 1'].tolist() + lectureExcel_5['Sub-Concept 1'].tolist() + \
                   lectureExcel_6['Sub-Concept 1'].tolist() + lectureExcel_7['Sub-Concept 1'].tolist() + \
                   lectureExcel_8['Sub-Concept 1'].tolist() + lectureExcel_9['Sub-Concept 1'].tolist() + \
                   lectureExcel_10['Sub-Concept 1'].tolist() + lectureExcel_11['Sub-Concept 1'].tolist()

# to generate a list with all the sub-concept 2 in all excels (llectureExcel_4 does not have sub-concept 2 column1!)
subConceptList_2 = lectureExcel_2['Sub-Concept 2'].tolist() + lectureExcel_3['Sub-Concept 2'].tolist() + \
                   lectureExcel_10['Sub-Concept 2'].tolist() + lectureExcel_5['Sub-Concept 2'].tolist() + \
                   lectureExcel_6['Sub-Concept 2'].tolist() + lectureExcel_7['Sub-Concept 2'].tolist() + \
                   lectureExcel_8['Sub-Concept 2'].tolist() + lectureExcel_9['Sub-Concept 2'].tolist() + \
                   lectureExcel_11['Sub-Concept 2'].tolist()

# to generate a dataframe with unique concept in all excels
conceptListDataFrame = pd.Series(conceptList).dropna().drop_duplicates().reset_index().drop(labels="index", axis=1)
conceptListDataFrame.columns = ['Concept']

# to generate a dataframe with unique sub-concept 1 & 2 in all excels
subConceptListDataFrame_1 = pd.Series(subConceptList_1).dropna().drop_duplicates().reset_index().drop(labels="index", axis=1)
subConceptListDataFrame_2 = pd.Series(subConceptList_2).dropna().drop_duplicates().reset_index().drop(labels="index", axis=1)
subConceptListDataFrame = pd.concat([subConceptListDataFrame_1,subConceptListDataFrame_2],axis=0,ignore_index=True)
subConceptListDataFrame.columns = ['Sub-Concept']


def toDataBase(dataframe):
    for index, row in dataframe.iterrows():
        allConceptName = Concept.objects.values_list("conceptName",flat=True).distinct()
        allSubConceptName = SubConcept.objects.values_list("subConceptName",flat=True).distinct()
        if row["Concept"] in allConceptName:
            if np.isnan(row["Sub-Concept 1"]):
                subConcept=None
            elif row["Sub-Concept 1"] in allSubConceptName:
                subConcept=SubConcept.objects.get(subConceptName=row["Sub-Concept 1"])
            else:
                subConcept=SubConcept.objects.create(subConceptName=row["Sub-Concept 1"])
            concept=Concept.objects.get(conceptName=row["Concept"])
        else:
            if np.isnan(row["Sub-Concept 1"]):
                subConcept=None
            elif row["Sub-Concept 1"] in allSubConceptName:
                subConcept=SubConcept.objects.get(subConceptName=row["Sub-Concept 1"])
            else:
                subConcept=SubConcept.objects.create(subConceptName=row["Sub-Concept 1"])
            concept=Concept.objects.create(conceptName=row["Concept"])
        if np.isnan(row["Sub-Concept 2"]):
                subConcept2=None
        elif row["Sub-Concept 2"] in allSubConceptName:
                subConcept2=SubConcept.objects.create(subConceptName=row["Sub-Concept 2"])
        else:
            subConcept2=SubConcept.objects.create(subConceptName=row["Sub-Concept 2"])
        question=Question.objects.create(concept=concept,subConcept1=subConcept,subConcept2=subConcept2,example=row["example"],
                                         meaning=row["Meaning （English）"],translation=row["Meaning"])

toDataBase(conceptListDataFrame)
toDataBase(subConceptListDataFrame)