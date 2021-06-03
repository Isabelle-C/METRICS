ind

dataDict = make_dict()

tumorID = biopsiesDF['TUMOR ID'][ind]
seed = biopsiesDF['SEED'][ind]

if tumorID != prevTumorID:
    tumorDF2 = tumorsDF.loc[tumorsDF['TUMOR ID'] == tumorID]

for ind in tumorDF2.index:
    print(ind)
    #replicateDF = replicatesDF.iloc[ind]

len(tumorsDF)
tumorDF2['SEED']