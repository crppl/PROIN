import numpy as np
import pandas as pd
import math
import re

from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn import svm

from sklearn import metrics
from sklearn import tree


def sortkey(n):
    i = 0
    ret = ""
    while i < len(n) and n[i].isnumeric():
        ret += n[i]
        i+=1
    if ret == "" or ret == "0":
        return 0
    return math.log2(float(ret))
    

class DataMod:
    ###
    # inicjalizacja i czyszczenie
    def __init__(this, file):
        this.orygDane = pd.read_csv(file)
        this.dane = this.orygDane.copy()
        this.clearData()
        this.enhanceData()
        this.teachModel("Linear")

    def clearData(this):
        this.dane = this.dane.drop(['Unnamed: 0.1', 'Unnamed: 0', 'name'], axis=1) # zastanów się nad usuwaniem name
        this.dane['Ram'] = this.dane['Ram'].str.replace('GB', '')
        this.dane['ROM'] = this.dane['ROM'].str.replace('GB', '')
        this.dane['ROM'] = this.dane['ROM'].str.replace('TB', '000')
        this.dane['OS'] = this.dane['OS'].str.replace('  ', ' ')
        this.dane['CPU'] = this.dane['CPU'].str.replace('Dual Core', '2 Cores')
        this.dane['CPU'] = this.dane['CPU'].str.replace('Quad Core', '4 Cores')
        this.dane['CPU'] = this.dane['CPU'].str.replace('Octa Core', '8 Cores')
        this.dane['CPU'] = this.dane['CPU'].str.replace('Hexa Core', '16 Cores')
        this.dane['price'] *= 0.045

    def enhanceData(this):
        # złącz rozdzielczość
        aaa = []
        for i in range(0, this.dane.shape[0]):
            temp = []
            if this.dane.loc[i, 'resolution_height'] > this.dane.loc[i, 'resolution_width']:   #głupie dane
                tmp = this.dane.loc[i, 'resolution_height']
                this.dane.loc[i, 'resolution_height'] = this.dane.loc[i, 'resolution_width']
                this.dane.loc[i, 'resolution_width'] = tmp
            temp.append(str(int(this.dane.loc[i, 'resolution_width'])))
            temp.append(str(int(this.dane.loc[i, 'resolution_height'])))
            x = "x".join(temp)
            aaa.append("x".join(temp))
        
        # rozłącz rdzenie i wątki
        cores = []
        threads = []
        for i in range(0, this.dane.shape[0]):
            core = this.dane.loc[i, 'CPU']
            if "Core" in core:
                core = core[0:2]
                core = re.sub(" ", "", core)
            else:
                core = ""
            cores.append(core)

            thread = this.dane.loc[i, 'CPU']
            if "Thread" in thread:
                thread = thread[-10:-1]
                thread = re.sub(" Thread", "", thread)
                thread = re.sub(" ", "", thread)
            else:
                thread = ""
            threads.append(thread)
        
        # dodaj do danych
        dfToAdd = pd.DataFrame({ 'resolution': aaa, 'cores': cores, 'threads': threads})
        this.dane = pd.concat([this.dane, dfToAdd], axis=1).drop(['resolution_width', 'resolution_height', 'CPU'], axis=1)
        this.dane.dropna()

    
    ### 
    # funckję związane z modelem
    def teachModel(this, type):
        dum = pd.get_dummies(this.dane)
        #print(dum.columns)
        x = dum.drop('price', axis=1)
        y = this.dane.price

        X_train, x_test, Y_train, y_test = train_test_split(x, y, test_size=0.2)
        this.reg = LinearRegression()
        match type:
            case "lasso":
                this.reg = Lasso()
            case "ridge":
                this.reg = Ridge()
        this.reg.fit(x, y)
 
    def prepareParams(this, dump):
        if len(dump.shape) == 1:
            x = dump.index
        else:
            x = dump.columns
        for i in x:
            if "none" not in dump[i]:
                #print(this.dum.columns)
                #print("==="*30)
                #print(dump.loc[0, i])
                #print("==="*30)
                for j in this.dum.columns:
                    #print(j)
                    if j == i:
                        this.dum = this.dum.drop(this.dum[ this.dum[j] != dump.loc[0, i] ].index)
                        break

    ### 
    # funkcje wypisywania wszystkiego
    def getPrice(this, params):
        #print(this.dane.columns)
        this.dane = this.orygDane.copy()
        this.clearData()
        this.enhanceData()
        this.dum = pd.get_dummies(this.dane)
        dump = pd.get_dummies(params)
        this.prepareParams(dump)
        x = this.dum.drop('price', axis=1)
        #print(dump)
        #print(this.dum.columns)
        this.price = this.reg.predict(x)
        #print(this.price)
        return this.price.copy()

    def printInfo(this):
        print(this.dane.info())

    def getData(this):
        return this.dane.copy()#drop('price', axis=1).copy()

    def getProcTypes(this):
        dat = this.dane.processor.unique().copy()
        ret = []
        for i in dat:
            if re.search("(.* (Core i.|Celeron|Pentium) .*)|(.*(Ryzen .|Athlon) .*)", i):
                i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i)  # usuwa ostatnie słowo
                i = re.sub(r'  \Z', "", i)    # usuwa podwójną spację
                i = re.sub(r' \Z', "", i)     # usuwa pojedynczą spację
            elif re.search("Apple", i):
                i = re.sub(" Apple M. Chip", "", i) 
                i = re.sub("Max M. Max", "Max", i) 
                i = re.sub("Pro M. Pro", "Pro", i)
            if i not in ret:
                ret.append(i)
        return ret

    def getRAMSizes(this):
        return sorted(this.dane.Ram.unique().copy(), key=sortkey)

    def getStorageSizes(this):
        return sorted(this.dane.ROM.unique().copy(), key=sortkey)

    def getDisplaySizes(this):
        return sorted(this.dane.display_size.unique().copy())

    def getResolutions(this):
        return sorted(this.dane.resolution.unique().copy())

    def getCPUCores(this):
        return sorted(this.dane.cores.unique().copy(), key=sortkey)

    def getCPUThreads(this):
        return sorted(this.dane.threads.unique().copy(), key=sortkey)
    
    def getBrandNames(this):
        return sorted(this.dane.brand.unique().copy())

    def getStorageTypes(this):
        return sorted(this.dane.ROM_type.unique().copy())

    def getRAMTypes(this):
        return sorted(this.dane.Ram_type.unique().copy())

    def getOSTypes(this):
        return sorted(this.dane.OS.unique().copy())

    def getWarranty(this):
        return sorted(this.dane.warranty.unique().copy())
    




def abc():
    print("This works!")



