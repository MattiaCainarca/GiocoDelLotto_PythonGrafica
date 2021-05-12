import tkinter as tk
import codicefiscale
from datetime import datetime
import numpy as np
import os.path


fields = ('Codice Fiscale', 'Tipo Di Giocata', 'Numeri', 'Ruota', 'Puntata', 'Risultato')
entries = {}
valori_utente = ['0', '0', '0', '0', '0', '0']
numeroCampi = 6

modalita = ["ESTRATTO", "AMBO", "TERNO", "QUATERNA", "CINQUINA", "ESTRATTO SECCO", "AMBO SECCO", "TERNO SECCO", "QUATERNA SECCA", "CINQUINA SECCA"]

nomiRuote = ["TORINO", "MILANO", "VENEZIA", "GENOVA", "FIRENZE", "ROMA", "NAPOLI", "BARI", "PALERMO", "CAGLIARI",
             "NAZIONALE"]

vincite = [5, 25, 450, 12000, 600000, 55, 250, 4500, 120000, 6000000]


def calcoloCodiceFiscale(cod_fisc):  # Controlla che che il codice fiscale inserito sia corretto:
    if cod_fisc == '0':
        return "Inserire un codice fiscale!"
    elif not codicefiscale.isvalid(cod_fisc):
        return "CF errato"
    else:
        if verificaEta(cod_fisc):
            return "OK"
        else:
            return "Sei Minorenne"


def verificaEta(cod_fisc):  # Viene verificato se l'utente ha almeno 18 anni:
    dataNascita = getDataNascita(cod_fisc)
    dataNascita[2] = convertiAnno(dataNascita[2])
    eta = calcolaEta(int(dataNascita[0]), int(dataNascita[1]), int(dataNascita[2]))
    if eta >= 18:
        return 1
    else:
        print("Mi dispiace non hai un'età sufficiente per giocare.")
        return 0


def getDataNascita(codice):  # Restituisce la data di nascita:
    data = (codicefiscale.get_birthday(codice))  # Dal codice inserito ricava la data di nascita.
    return data.split('-')  # Divide la data di nascita in un array di tre elementi [giorno, mese, anno].


def convertiAnno(anno):  # Converte l'anno del codice fiscale in un anno con 4 cifre:
    year = datetime.now().strftime(
        "%y")  # Assegna alla varibiale "year" solo le ultime due cifre dell'anno corrente (2021 --> 21).
    if int(anno) < int(year):
        return int(anno) + 2000
    else:
        return int(anno) + 1900


def calcolaEta(giorno, mese, anno):  # Ritorna l'età in base al codice fiscale inserito:
    today = datetime.today()
    return today.year - anno - ((today.month, today.day) < (mese, giorno))


def salvaEstrazione():  # Viene salvata la matrice su un file con la data del giorno corrente:
    filename = fileGiornoOdierno()
    if not os.path.exists(filename):
        num_estratti = generaNumeriRuote()
        file = open(filename, 'w')
        np.savetxt(file, num_estratti, fmt='%i', delimiter=';', newline='\n')
        file.close()


def fileGiornoOdierno():
    now = datetime.now()
    nome_file = now.strftime("NumeriVincenti_%d-%m-%Y")
    nome_file = f'{nome_file}.txt'
    return nome_file


def generaNumeriRuote():  # Genera 5 numeri compresi tra 0 e 90 diversi per ogni riga, per ogni ruota:
    mat = np.zeros((11, 5))
    for i in range(len(mat)):
        mat[i] = np.random.choice(89, 5, replace=False) + 1
    return mat


def controllaModalita(mod):  # L'utente sceglie la modalità con la quale vuole fare la sua puntata:
    if mod == '0':
        return "Inserire una modalità!"
    elif mod in modalita:
        return "OK"
    else:
        return "Modalita non esistente"


def controllaRuota(ruota, mod):  # L'utente sceglie la ruota du cui vuole fare la sua puntata:
    if ruota in nomiRuote or modalita.index(mod) < 6:
        return "OK"
    elif ruota == '0':
        return "Inserire una ruota!"
    else:
        return "Ruota non esistente"


def splitNumeri(numeri):
    return numeri.split(' ')


def controllaNumeri(numeri_da_giocare,
                    mod):  # Chiede all'utente di inserire i numeri per effetturare la giocata in base alla modalità scelta:
    numeri_scelti = splitNumeri(numeri_da_giocare)
    numeri_da_giocare = modalita.index(mod) + 1
    if numeri_da_giocare > 5:
        numeri_da_giocare -= 5
    if len(numeri_scelti) != numeri_da_giocare:
        return "Numeri inseriti non sufficienti"
    else:
        for i in range(numeri_da_giocare):
            if (numeri_scelti[i] < '1') or (numeri_scelti[i] > '90') or not(numeriDoppi(numeri_scelti, i)):
                return "Numeri non Validi"
        else:
            return 'OK'


def numeriDoppi(numeri, i):
    for j in range(i):
        if numeri[j] == numeri[i]:
            return 0
    return 1


def leggiFile():  # Legge i numeri estratti dal file dei numeri vincenti del giorno corrente:
    filename = fileGiornoOdierno()
    file = open(filename, 'r')
    matrice = np.loadtxt(file, dtype=int, delimiter=';', usecols=(0, 1, 2, 3, 4))
    return matrice


def controlloVincite(num_estratti, mod_scelta, num_scelti, r_scelta,
                     punt_scelta):  # Vengono confrontati i numeri inseriti dall'utente con quelli dell'estrazione:
    num_split = splitNumeri(num_scelti)
    m = modalita.index(mod_scelta) + 1
    if m < 6:
        indovinati = controlloVinciteEstrazioni(num_split, m, num_estratti)
    else:
        r = nomiRuote.index(r_scelta)
        indovinati = controlloVinciteEstrazioniSecche(num_split, num_estratti[r])
    if indovinati > 0:
        return calcoloVincita(indovinati, m, int(punt_scelta))
    else:
        return "Non hai trovato nessuno numero"


def controlloVinciteEstrazioni(num_utente, mod,
                               num_vincenti):  # Controlla se i numeri dell'utenti sono presenti in quelli estratti, su tutte le ruote:
    trovati = 0
    for i in range(10):
        trovati_interni = 0
        for j in range(mod):
            if int(num_utente[j]) in num_vincenti[i]:
                trovati_interni += 1
        if trovati_interni >= mod:
            trovati += 1
    return trovati


def controlloVinciteEstrazioniSecche(num_utente, num_vincenti):  # Controlla se i numeri dell'utenti sono presenti in quelli estratti, sulla ruota scelta dall'utente:
    for i in range(len(num_utente)):
        if not int(num_utente[i]) in num_vincenti:
            return 0
    return 1


def calcoloVincita(trovati, mod_scelta, punt_scelta):  # Viene calcolata la vincita in base all'importo giocato:
    return vincite[mod_scelta - 1] * trovati * punt_scelta


def aggiornaFileGiocatori(cod_fisc, num_utente,
                          ammontare):  # Viene aggiunto al file dei giocatori, il codice fiscale dell'utente con la rispettiva vincita:
    if ammontare == "Non hai trovato nessuno numero":
        ammontare = 0
    now = datetime.now()
    data = now.strftime("%d-%m-%Y")
    filename = f"{data}_{cod_fisc}.txt"
    if os.path.exists(filename):
        file_utenti = open(filename, "a")
    else:
        file_utenti = open(filename, "w")
    file_utenti.write(f"{cod_fisc}, {num_utente}, {ammontare}\n")
    file_utenti.close()


def stampaCampi():
    for i in range(numeroCampi - 1):
        valori_utente[i] = entries[fields[i]].get()
        valori_utente[i] = valori_utente[i].upper()

    salvaEstrazione()
    if int(valori_utente[4]) > 0:
        test = calcoloCodiceFiscale(valori_utente[0])
        if test == 'OK':
            test = controllaModalita(valori_utente[1])
            if test == 'OK':
                test = controllaRuota(valori_utente[3], valori_utente[1])
                if test == 'OK':
                    test = controllaNumeri(valori_utente[2], valori_utente[1])
                    if test == 'OK':
                        numeri_estratti = leggiFile()
                        test = controlloVincite(numeri_estratti, valori_utente[1], valori_utente[2], valori_utente[3],
                                                valori_utente[4])
                        aggiornaFileGiocatori(valori_utente[0], valori_utente[2], test)
    else:
        test = "Somma scommessa non valida"

    entries[fields[numeroCampi - 1]].delete(0, tk.END)
    entries[fields[numeroCampi - 1]].insert(0, test)


def makeform(root, fields):
    root.iconphoto(False, tk.PhotoImage(file='logolotto.png'))
    root.winfo_toplevel().title("Gioco del Lotto")
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=15, text=field + ": ", anchor='w')
        ent = tk.Entry(row, width=30)
        ent.insert(0, '0')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries[field] = ent
    return entries


root = tk.Tk()
entries = makeform(root, fields)
b1 = tk.Button(root, text='Esci', command=root.quit)
b1.pack(side=tk.RIGHT, padx=5, pady=5)
b2 = tk.Button(root, text='Gioca', command=lambda: stampaCampi())
b2.pack(side=tk.RIGHT, padx=5, pady=5)
root.mainloop()
