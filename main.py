import datamod as dm
import pandas as pd

test = dm.DataMod("data.csv")


params = test.getData()
params2 = params.copy()

params = params.iloc[0, :]

params['spec_rating'] = "none"


if len(params.shape) == 1:
    x = params.index
else:
    x = params.columns
for i in x:
    if params[i] != "none":
        params2 = params2.drop(params2[ params2[i] != params[i] ].index)

#print(params.shape)
#print(params2.shape)

dump = pd.get_dummies(params2)

#print(dump)

#print(dump.columns)


print(test.getPrice(params2))
print(params2.loc[0, 'price'])
