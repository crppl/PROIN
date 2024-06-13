from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import datamod as dm
import pandas as pd



def caseApple():
    val = cbBrand.get()
    types = ["n/a"]
    oss = ["n/a"]
    gpu = ["n/a"]
    xyz = dm.getGPUsApple()
    valos = cbOS.get()
    valgp = cbGPU.get()
    valcp = cbCPUType.get()
    if "Apple" in val:
        if "Mac" not in valos:
            cbOS.set("n/a")
        if "Apple" not in valcp:
            cbCPUType.set("n/a")
            cbCores.set("n/a")
        if valgp not in xyz:
            cbGPU.set("n/a")
        for i in dm.getOSTypes():
            if "Mac" in i:
                oss.append(i)
        for i in dm.getCPUTypes():
            if "Apple" in i:
                types.append(i)
        types.append("Intel")
        gpu.extend(xyz)
        labThreads.pack_forget()
        cbThreads.pack_forget()
        cbThreads.set("n/a")

    elif val == "n/a":
        oss.extend(dm.getOSTypes())
        types.extend(dm.getCPUTypes())
        gpu.extend(dm.getGPUs())
        
    else:
        if "Mac" in valos:
            cbOS.set("n/a")
        if "Apple" in valcp:
            cbCPUType.set("n/a")
        if valgp in xyz:
            cbGPU.set("n/a")
        for i in dm.getOSTypes():
            if "Mac" not in i:
                oss.append(i)
        for i in dm.getCPUTypes():
            if "Apple" not in i:
                types.append(i)
        for i in dm.getGPUs():
            if i not in xyz:
                gpu.append(i)
    cbOS['value'] = oss
    cbCPUType['value'] = types
    cbGPU['value'] = gpu


def evBrand(event):
    caseApple()



def evOS(event):
    val = cbOS.get()
    if "Mac" in val:
        cbBrand.set("Apple")
    caseApple()



def evType(event):
    val = cbCPUType.get()
    cores = ["n/a"]
    threads = ["n/a"]
    if "Apple" in val:
        cores.extend(dm.getCPUCoresApple())
        if cbBrand.get() != "Apple":
            cbBrand.set("Apple")
    else:
        cores.extend(dm.getCPUCores())
        labThreads.pack(padx=10)
        cbThreads.pack(padx=10, pady=10)
    caseApple()
    threads.extend(dm.getCPUThreads())
    cbCores['value'] = cores
    cbThreads['value'] = threads



def evCores(event):
    thread = ["n/a"]
    thread.extend(dm.getCPUThreads(cbCores.get()))
    if thread[1] == "":
        thread.pop(1)
    cbThreads['value'] = thread



def evThreads(event):
    cores = ["n/a"]
    cores.extend(dm.getCPUCores(cbThreads.get()))
    cbCores['value'] = cores



def evRam(event):
    ramt = ["n/a"]
    ramt.extend(dm.getRAMTypes(cbRam.get()))
    cbRamTypes['value'] = ramt



def evRamTypes(event):
    ramm = ["n/a"]
    ramm.extend(dm.getRAMSizes(cbRamTypes.get()))
    cbRam['value'] = ramm



def evDisplay(event):
    resols = ["n/a"]
    resols.extend(dm.getResolutions(cbDisplay.get()))
    cbResolution['value'] = resols



def evResolution(event):
    disps = ["n/a"]
    disps.extend(dm.getDisplaySizes(cbResolution.get()))
    cbDisplay['value'] = disps



def evGPU(event):
    gpuapple = dm.getGPUsApple()
    if cbGPU.get() in gpuapple:
        cbBrand.set("Apple")
    caseApple()




### inne funkcje

def checkValues(params):
    return all(x == params[1] for x in params)



def getCBoxValues():
    params = [
        cbBrand.get(),
        "n/a",
        cbRam.get(),        # int
        cbRamTypes.get(),
        cbStorage.get(),    # int
        cbStorageTypes.get(),
        cbDisplay.get(),    # float
        cbOS.get(),
        cbWarranty.get(),
        cbResolution.get(),
        cbCPUType.get(),
        cbCores.get(),
        cbThreads.get(),
        cbGPU.get()
    ]
    if checkValues(params):
        return -1
    pdparam = pd.DataFrame([params], columns=dm.getColumns())
    return pdparam



def butter(event):
    prms = getCBoxValues()
    if isinstance(prms, int):
        messagebox.showerror("Błąd!", "Należy wybrać parametry, na podstawie których należy wyznaczyć cenę.")
        return
    ret = dm.getPrice(prms)
    var = dm.getRMS()

    predPrice.set("Wycena laptopa: " + str(round(ret, 2)) + " PLN")
    variance.set("Estymowana rozbieżność: " + str(int(var)) + " PLN")



def butclr(event):
    cbBrand.set("n/a")
    cbBrand.event_generate("<<ComboboxSelected>>")
    cbCores.set("n/a")
    cbCores.event_generate("<<ComboboxSelected>>")
    cbCPUType.set("n/a")
    cbCPUType.event_generate("<<ComboboxSelected>>")
    cbDisplay.set("n/a")
    cbDisplay.event_generate("<<ComboboxSelected>>")
    cbGPU.set("n/a")
    cbGPU.event_generate("<<ComboboxSelected>>")
    cbOS.set("n/a")
    cbOS.event_generate("<<ComboboxSelected>>")
    cbRam.set("n/a")
    cbRam.event_generate("<<ComboboxSelected>>")
    cbRamTypes.set("n/a")
    cbRamTypes.event_generate("<<ComboboxSelected>>")
    cbResolution.set("n/a")
    cbResolution.event_generate("<<ComboboxSelected>>")
    cbStorage.set("n/a")
    cbStorage.event_generate("<<ComboboxSelected>>")
    cbStorageTypes.set("n/a")
    cbStorageTypes.event_generate("<<ComboboxSelected>>")
    cbThreads.set("n/a")
    cbThreads.event_generate("<<ComboboxSelected>>")
    cbWarranty.set("n/a")
    cbWarranty.event_generate("<<ComboboxSelected>>")
    predPrice.set("")
    variance.set("")



dm = dm.DataMod("data.csv")

# gui
root = Tk()
root.title("NDWL")
root.minsize(870, 600)
root.iconbitmap("ikonka.ico")


predPrice = StringVar()
predPrice.set("")

variance = StringVar()
variance.set("")

testScore = StringVar()
testScore.set("")

trainScore = StringVar()
trainScore.set("")

# baseline data

mod = ["", "Linear", "Lasso", "Ridge", "Random Forest"]
typ = ["n/a"] + dm.getCPUTypes()
cor = ["n/a"] + dm.getCPUCores()
thr = ["n/a"] + dm.getCPUThreads()
bra = ["n/a"] + dm.getBrandNames()
os = ["n/a"] + dm.getOSTypes()
war = ["n/a"] + dm.getWarranty()
ram = ["n/a"] + dm.getRAMSizes()
rat = ["n/a"] + dm.getRAMTypes()
sto = ["n/a"] + dm.getStorageSizes()
stt = ["n/a"] + dm.getStorageTypes()
dis = ["n/a"] + dm.getDisplaySizes()
res = ["n/a"] + dm.getResolutions()
gpu = ["n/a"] + dm.getGPUs()

width=250
height=225

### frames


frameMain = LabelFrame(root, text="Informacje ogólne", width=width, height=height)
frameMain.grid(column=0,row=1, padx=20, pady=10)

frameCPU = LabelFrame(root, text="Parametry procesora", width=width, height=height)
frameCPU.grid(column=1,row=1, padx=20, pady=10, columnspan=2)

frameRam = LabelFrame(root, text="Pamięć RAM", width=width, height=height)
frameRam.grid(column=3, row=1, padx=20, pady=10)

frameStorage = LabelFrame(root, text="Pamięć masowa", width=width, height=height)
frameStorage.grid(column=0, row=2, padx=20, pady=10)

frameDisplay = LabelFrame(root, text="Parametry ekranu",width=width, height=height)
frameDisplay.grid(column=1, row=2, padx=20, pady=10, columnspan=2)

frameGPU = LabelFrame(root, text="Karta graficzna", width=width, height=height)
frameGPU.grid(column=3, row=2, padx=20, pady=10)


### labels

labBrand = Label(frameMain, text="Marka laptopa:")
labOS = Label(frameMain, text="System operacyjny:")
labWarranty = Label(frameMain, text="Gwarancja [lata]:")

labType = Label(frameCPU, text="Rodzaj procesora:")
labCores = Label(frameCPU, text="Liczba rdzeni procesora:")
labThreads = Label(frameCPU, text="Liczba wątków procesora:")

labRam = Label(frameRam, text="Rozmiar pamięci RAM [GB]:")
labRamType = Label(frameRam, text="Rodzaj pamięci RAM:")

labStorage = Label(frameStorage, text="Rozmiar pamięci masowej [GB]:")
labStorageType = Label(frameStorage, text="Rodzaj pamięci masowej:")

labDisplay = Label(frameDisplay, text="Przekątna ekranu [\"]:")
labResolution = Label(frameDisplay, text="Rozdzielczość ekranu:")

labGPU = Label(frameGPU, text="Rodzaj karty graficznej:")
labG1 = Label(frameGPU)

### comboboxes

cbBrand = ttk.Combobox(frameMain, state="readonly", value=bra)
cbBrand.current(0)
cbBrand.bind("<<ComboboxSelected>>", evBrand)

cbOS = ttk.Combobox(frameMain, state="readonly", value=os)
cbOS.current(0)
cbOS.bind("<<ComboboxSelected>>", evOS)

cbWarranty = ttk.Combobox(frameMain, state="readonly", value=war)
cbWarranty.current(0)

cbCPUType = ttk.Combobox(frameCPU, state="readonly", value=typ, width=28)
cbCPUType.current(0)
cbCPUType.bind("<<ComboboxSelected>>", evType)

cbCores = ttk.Combobox(frameCPU, state="readonly", value=cor)
cbCores.current(0)
cbCores.bind("<<ComboboxSelected>>", evCores)

cbThreads = ttk.Combobox(frameCPU, state="readonly", value=thr)
cbThreads.current(0)
cbThreads.bind("<<ComboboxSelected>>", evThreads)

cbRam = ttk.Combobox(frameRam, state="readonly", value=ram)
cbRam.current(0)
cbRam.bind("<<ComboboxSelected>>", evRam)

cbRamTypes = ttk.Combobox(frameRam, state="readonly", value=rat)
cbRamTypes.current(0)
cbRamTypes.bind("<<ComboboxSelected>>", evRamTypes)

cbStorage = ttk.Combobox(frameStorage, state="readonly", value=sto)
cbStorage.current(0)

cbStorageTypes = ttk.Combobox(frameStorage, state="readonly", value=stt)
cbStorageTypes.current(0)

cbDisplay = ttk.Combobox(frameDisplay, state="readonly", value=dis)
cbDisplay.current(0)
cbDisplay.bind("<<ComboboxSelected>>", evDisplay)

cbResolution = ttk.Combobox(frameDisplay, state="readonly", value=res)
cbResolution.current(0)
cbResolution.bind("<<ComboboxSelected>>", evResolution)

cbGPU = ttk.Combobox(frameGPU, state="readonly", value=gpu, width=28)
cbGPU.current(0)
cbGPU.bind("<<ComboboxSelected>>", evGPU)








btn = Button(root, text="Oblicz")
btn.bind("<Button-1>", butter)
btn.grid(column=2, row=4)

btnclr = Button(root, text="Wyczyść")
btnclr.bind("<Button-1>", butclr)
btnclr.grid(column=1, row=4)

labAns = Label(root, textvariable=predPrice)
labAns.grid(column=1, row=5, columnspan=2)

labVar = Label(root, textvariable=variance)
labVar.grid(column=1, row=6, columnspan=2)

# pakowanie

frameMain.pack_propagate(False)
frameCPU.pack_propagate(False)
frameRam.pack_propagate(False)
frameStorage.pack_propagate(False)
frameDisplay.pack_propagate(False)

labBrand.pack(padx=10)
cbBrand.pack(padx=10, pady=10)
labOS.pack(padx=10)
cbOS.pack(padx=10, pady=10)
labWarranty.pack(padx=10)
cbWarranty.pack(padx=10, pady=10)

labType.pack(padx=10)
cbCPUType.pack(padx=10, pady=10)
labCores.pack(padx=10)
cbCores.pack(padx=10, pady=10)
labThreads.pack(padx=10)
cbThreads.pack(padx=10, pady=10)

labRam.pack(padx=10)
cbRam.pack(padx=10, pady=10)
labRamType.pack(padx=10)
cbRamTypes.pack(padx=10, pady=10)

labStorage.pack(padx=10)
cbStorage.pack(padx=10, pady=10)
labStorageType.pack(padx=10)
cbStorageTypes.pack(padx=10, pady=10)

labDisplay.pack(padx=10)
cbDisplay.pack(padx=10, pady=10)
labResolution.pack(padx=10)
cbResolution.pack(padx=10, pady=10)

labGPU.pack(padx=10)
cbGPU.pack(padx=27, pady=10)
labG1.pack(padx=10, pady=61)



root.mainloop()