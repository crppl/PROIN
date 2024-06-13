import pandas as pd
import math
import re
import requests

from statistics import mean
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from sklearn import metrics


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
    baseline = pd.DataFrame({ 'brand': ["n/a"], 'price': [3860], 'Ram': ["n/a"], 'Ram_type': ["DDR4"], 'ROM': [512],  'ROM_type': ["SSD"], 'display_size': [15.6],  'OS': ["Windows 11 OS"], 'warranty': ["1"], 'resolution': ["1920x1080"], 'processor': ["n/a"], 'cores': ["n/a"],  'threads': ["n/a"], 'GPU': ["n/a"]})

    def __init__(this, file):
        this.orygDane = pd.read_csv(file)
        req = requests.get('https://api.frankfurter.app/latest?from=INR&to=PLN')
        if req.status_code == 200:
            this.exrate = req.json()['rates']['PLN']
        else:
            this.exrate = 0.047
        this.teachModel()

    def clearData(this):
        this.dane = this.dane.drop(['Unnamed: 0.1', 'Unnamed: 0', 'name', 'spec_rating'], axis=1) # zastanów się nad usuwaniem name
        this.dane['Ram'] = this.dane['Ram'].str.replace('GB', '')
        this.dane['Ram'] = this.dane['Ram'].astype(int)

        this.dane['ROM'] = this.dane['ROM'].str.replace('GB', '')
        this.dane['ROM'] = this.dane['ROM'].str.replace('TB', '000')
        this.dane['ROM'] = this.dane['ROM'].astype(int)

        this.dane['OS'] = this.dane['OS'].str.replace('  ', ' ')

        this.dane['CPU'] = this.dane['CPU'].str.replace('Dual Core', '2 Cores')
        this.dane['CPU'] = this.dane['CPU'].str.replace('Quad Core', '4 Cores')
        this.dane['CPU'] = this.dane['CPU'].str.replace('Octa Core', '8 Cores')
        this.dane['CPU'] = this.dane['CPU'].str.replace('Hexa Core', '6 Cores') #16 cores


        this.dane['GPU'] = this.dane['GPU'].str.replace('Nvidia', 'NVIDIA')
        this.dane['GPU'] = this.dane['GPU'].str.replace('Geforce', 'GeForce')
        this.dane['GPU'] = this.dane['GPU'].str.replace('RTX RTX', 'RTX')


        this.dane['GPU'] = this.dane['GPU'].str.replace('Integrated Intel', 'Intel')  # keep
        this.dane['GPU'] = this.dane['GPU'].str.replace('Iris Xe Graphics', 'Iris Xe')    # keep
        this.dane['GPU'] = this.dane['GPU'].str.replace('Integrated Iris', 'Iris')
        this.dane['GPU'] = this.dane['GPU'].str.replace('UHD Graphics', 'UHD')
        this.dane['GPU'] = this.dane['GPU'].str.replace('Intel Integrated Intel', 'Intel')
        this.dane['GPU'] = this.dane['GPU'].str.replace('Integrated UHD', 'UHD')
        this.dane['GPU'] = this.dane['GPU'].str.replace('Intel Graphics', 'Intel Integrated')
        this.dane['GPU'] = this.dane['GPU'].str.replace('Integrated Integrated', 'Integrated')
        this.dane['GPU'] = this.dane['GPU'].str.replace('Intel Intel', 'Intel')


        this.dane['GPU'] = this.dane['GPU'].str.replace('RX 6500M Graphics', 'RX 6500M')
        this.dane['GPU'] = this.dane['GPU'].str.replace('AMD Radeon AMD', 'AMD Radeon')
        this.dane['GPU'] = this.dane['GPU'].str.replace('AMD Radeon Radeon', 'AMD Radeon')
        this.dane['GPU'] = this.dane['GPU'].str.replace('AMD Radeon Graphics', 'AMD Radeon')
        this.dane['GPU'] = this.dane['GPU'].str.replace('M Graphics', 'M')
        this.dane['GPU'] = this.dane['GPU'].str.replace('Vega 7 Graphics', 'Vega 7')
        this.dane['GPU'] = this.dane['GPU'].str.replace('Vega 8 Graphics', 'Vega 8')

        this.dane['GPU'] = this.dane['GPU'].str.replace('-core', '-Core')
        this.dane['price'] *= this.exrate      

    def enhanceData(this):
        # złącz rozdzielczość
        aaa = []
        for i in range(0, this.dane.shape[0]):
            temp = []
            if this.dane.loc[i, 'resolution_height'] > this.dane.loc[i, 'resolution_width']:  
                tmp = this.dane.loc[i, 'resolution_height']
                this.dane.loc[i, 'resolution_height'] = this.dane.loc[i, 'resolution_width']
                this.dane.loc[i, 'resolution_width'] = tmp
            temp.append(str(int(this.dane.loc[i, 'resolution_width'])))
            temp.append(str(int(this.dane.loc[i, 'resolution_height'])))
            aaa.append("x".join(temp))
        
        # rozłącz rdzenie i wątki
        cores = []
        threads = []
        for i in range(0, this.dane.shape[0]):
            core = this.dane.loc[i, 'CPU']
            if "Core" in core:
                core = core[0:3]
                #print(core)
                core = re.sub(" ", "", core)
                core = re.sub("C", "", core)
                #print(core)
            else:
                core = ""
            cores.append(core)

            thread = this.dane.loc[i, 'CPU']
            if "Thread" in thread:
                thread = thread[-10:-1]
                #print(thread)
                thread = re.sub(" Thread", "", thread)
                thread = re.sub(" ", "", thread)
                #print(thread)
            else:
                thread = ""
            threads.append(thread)


        # ujednolicenie nazw procesorów
        processors = []
        for i in this.dane.processor:
            if re.search("(.* (Core i.|Celeron|Pentium) .*)|(.*(Ryzen .|Athlon) .*)", i):
                i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i)  # usuwa ostatnie słowo
                i = re.sub(r'  \Z', "", i)    # usuwa podwójną spację
                i = re.sub(r' \Z', "", i)     # usuwa pojedynczą spację
            elif re.search("Apple", i):
                i = re.sub(" Apple M. Chip", "", i) 
                i = re.sub("Max M. Max", "Max", i) 
                i = re.sub("Pro M. Pro", "Pro", i)
            processors.append(i)
        

        # ujednolicenie nazw procesorów graficznych - daje +30pln do rozrzutu
        gpus = []
        for i in this.dane.GPU:
            i = re.sub(r' \Z', "", i)    
            if re.search("NVIDIA", i):
                if re.search("GeForce .TX", i):
                    if i[-2:] == 'Ti':
                        i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i)  
                        i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i)  
                        i = re.sub(r' \Z', "", i)
                        i += 'Ti'
                    elif i[-2:] == 'da':
                        i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i)  
                        i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i)  
                        i = re.sub(r' \Z', "", i)
                        i += 'Ada'
                    elif i[-2:] != "TX":
                        i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i)  
                        i = re.sub(r'  \Z', "", i)
                        i = re.sub(r' \Z', "", i)
            elif re.search("Intel.*UHD .*", i):
                i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i) 
            elif re.search("AMD Radeon .*M", i):
                i = re.sub(r'\b[\w-]+\b(?=\s*$)', "", i) 
            i = re.sub(r' \Z', "", i)
            gpus.append(i)
        

        this.dane = this.dane.rename(columns={'GPU': 'graphics'})

        this.dane = this.dane.drop('processor', axis=1)
        dfToAdd = pd.DataFrame({ 'resolution': aaa, 'processor': processors, 'cores': cores, 'threads': threads, 'GPU': gpus})
        this.dane = pd.concat([this.dane, dfToAdd], axis=1).drop(['resolution_width', 'resolution_height', 'CPU', 'graphics'], axis=1)


    
    def teachModel(this):
        this.dane = this.orygDane.copy()
        this.clearData()
        this.enhanceData()
        dum = pd.get_dummies(this.dane)
        x = dum.drop('price', axis=1)
        y = this.dane.price

        this.regLin = LinearRegression()
        this.regLin.fit(x, y)
        this.regLas = Lasso(max_iter=1500)
        this.regLas.fit(x, y)
        this.regRid = Ridge()
        this.regRid.fit(x, y)
        this.regRfr = RandomForestRegressor(n_estimators=50, max_depth=13)
        this.regRfr.fit(x, y)
        this.regGra = GradientBoostingRegressor()
        this.regGra.fit(x, y)





    def prepareParams(this, prms):
        paff = []
        for i in this.dane.columns:
            if prms.loc[0, i] != "n/a":
                if i == 'Ram' or i == 'ROM' or i == 'warranty':
                    prms[i] = prms[i].astype(int)
                if i == 'display_size':
                    prms[i] = prms[i].astype(float)
                this.dane = this.dane[this.dane[i] == prms.loc[0, i]] 

        if this.dane.shape[0] != 0:
            this.lackFlag = 0
            for i in range(0, this.dane.shape[0]):
                paff.append(this.dane.iloc[i, :].to_list())

        else:
            paaa = []
            for i in this.dane.columns:
                if i != 'price' and prms.loc[0, i] != "n/a":
                    paaa.append(prms.loc[0, i])
                else:
                    this.lackFlag = 1
                    paaa.append(this.baseline.loc[0, i])
            paff.append(paaa)

        duma = pd.get_dummies(pd.DataFrame(paff, columns=this.dane.columns))

        pbff = []

        for j in range(0, duma.shape[0]):
            pbbb = [False for x in this.dum.columns]
            for k in range(0, duma.shape[1]):
                for i in range(0, len(pbbb)):
                    if duma.columns[k] == this.dum.columns[i]:
                        pbbb[i] = duma.iloc[j, k]
                        break
            pbff.append(pbbb)

        return pd.DataFrame(pbff, columns=this.dum.columns)





    def getPrice(this, params):
        this.dane = this.orygDane.copy()
        this.clearData()
        this.enhanceData()
        this.dum = pd.get_dummies(this.dane)
        abc = this.prepareParams(params)
        this.x = abc.drop('price', axis=1)
        this.y = abc['price']

        if this.lackFlag:
            this.predRfr = this.regRfr.predict(this.x)
            this.predGra = this.regGra.predict(this.x)
            this.prediction = mean([mean(this.predRfr), mean(this.predGra)])
        else:
            this.predLin = this.regLin.predict(this.x)
            this.predLas = this.regLas.predict(this.x)
            this.predRid = this.regRid.predict(this.x)
            this.predRfr = this.regRfr.predict(this.x)
            this.predGra = this.regGra.predict(this.x)
            this.prediction = mean([ mean(this.predLin),mean(this.predLas), mean(this.predRid), mean(this.predRfr), mean(this.predGra)])

        this.dane = this.orygDane.copy()
        this.clearData()
        this.enhanceData()
        return this.prediction

    def getRMS(this):
        if this.lackFlag:
            finalRMS = mean(
                [
                    metrics.root_mean_squared_error(this.y, this.predRfr),
                    metrics.root_mean_squared_error(this.y, this.predGra)
                ]
            )
        else:
            finalRMS = mean( 
                [ 
                    metrics.root_mean_squared_error(this.y, this.predLin),
                    metrics.root_mean_squared_error(this.y, this.predLas),
                    metrics.root_mean_squared_error(this.y, this.predRid),
                    metrics.root_mean_squared_error(this.y, this.predRfr)
                ]
            )
        return finalRMS


    def printInfo(this):
        print(this.dane.info())

    def getColumns(this):
        return this.dane.columns

    def getData(this):
        return this.dane.copy()



    def getBrandNames(this):
        return sorted(this.dane.brand.unique().copy())




    def getCPUTypes(this, br="n/a"):
        if br == "n/a":
            return sorted(this.dane.processor.unique().copy())
        else:
            return sorted(this.dane.processor[this.dane.brand.str.contains("Apple")].unique().copy(), key=sortkey)

    def getCPUCores(this, threads="n/a"):
        if threads == "n/a":
            return sorted(this.dane.cores.unique().copy(), key=sortkey)
        else:
            return sorted(this.dane.cores[this.dane.threads.str.contains(threads)].unique().copy(), key=sortkey)
    
    def getCPUCoresApple(this):
        return sorted(this.dane.cores[this.dane.processor.str.contains("Apple")].unique().copy(), key=sortkey)

    def getCPUThreads(this, cores="n/a"):
        if cores == "n/a":
            return sorted(this.dane.threads.unique().copy(), key=sortkey)
        else:
            return sorted(this.dane.threads[this.dane.cores.str.contains(cores)].unique().copy(), key=sortkey)




    def getDisplaySizes(this, res="n/a"):
        if res == "n/a":
            return sorted(this.dane.display_size.unique().copy())
        else:
            return sorted(this.dane.display_size[this.dane.resolution.str.contains(res)].unique().copy())

    def getResolutions(this, dis="n/a"):
        if dis == "n/a":
            return sorted(this.dane.resolution.unique().copy())
        else:
            return sorted(this.dane.resolution[this.dane.display_size == float(dis)].unique().copy())




    def getStorageSizes(this):
        return sorted(this.dane.ROM.unique().copy()) 

    def getStorageTypes(this):
        return sorted(this.dane.ROM_type.unique().copy())




    def getRAMSizes(this, rat="n/a"):
        if rat == "n/a":
            return sorted(this.dane.Ram.unique().copy()) 
        else:
            return sorted(this.dane.Ram[this.dane.Ram_type.str.contains(rat)].unique().copy())

    def getRAMTypes(this, ram="n/a"):
        if ram == "n/a":
            return sorted(this.dane.Ram_type.unique().copy())
        else:
            return sorted(this.dane.Ram_type[this.dane.Ram == int(ram)].unique().copy())



    def getOSTypes(this):
        return sorted(this.dane.OS.unique().copy())


    def getGPUs(this):
        return sorted(this.dane.GPU.unique().copy(), key=sortkey)
    
    def getGPUsApple(this):
        return sorted(this.dane.GPU[this.dane['brand'].str.contains("Apple")].unique().copy(), key=sortkey)


    def getWarranty(this):
        return sorted(this.dane.warranty.unique().copy())
    







