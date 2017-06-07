#Algorytm losowego lasu na przykladzie danych Sonar

#Importowanie potrzebnych bibliotek
from random import seed
from random import randrange
from csv import reader
from math import sqrt

#Wczytywanie pliku csv
def load_csv(nazwaPliku):
    dane = list() #tworzenie zmiennej na dane
    with open(nazwaPliku, 'r') as plik: #otwieranie pliku
        wczytywanieCsv = reader(plik)   #przypisywanie wszystkich danych z pliku do zmiennej wczytywanieCsv
        for row in wczytywanieCsv: #pobieranie wierszy z wczytanych danych
            if not row:
                continue
            dane.append(row) #uzupełnianie listy z danymi
    return dane

#Konwersja kolumn z danych typu String na zmiennoprzecinkowe float
def strToFloat(dane, kolumna):
    for row in dane:
        row[kolumna] = float(row[kolumna].strip())#Konwersja wartości typu string na float

#Konwersja kolumn z danych typu String na liczby całkowite integer
def strToInt(dane, kolumna):
    wartosciKlasy = [row[kolumna-1] for row in dane]
    unique = set(wartosciKlasy)
    sprawdzanie = dict()
    for i, wartosc in enumerate(unique): #Sprawdzanie unikalnosci kolejnych wyrazów (zmiana id z String na integer)
        sprawdzanie[wartosc] = i
    for row in dane:
        row[kolumna-1] = sprawdzanie[row[kolumna-1]]
    return sprawdzanie

#podział danych na k składowych
def podzial(dane, nSkladowe):
    #przygotowywanie zmiennych potrzebnych do bezpicznego stworzenia podzialu
    danePodzial = list()
    daneKopia = list(dane)
    #ustalenie wielkosci skladowych
    wielkoscSkladowych = int(len(dane)/nSkladowe)
    #przypisywanie skladowych
    for i in range(nSkladowe):
        skladowe = list()
        while len(skladowe)<wielkoscSkladowych:
            index = randrange(len(daneKopia))
            skladowe.append(daneKopia.pop(index))
        danePodzial.append(skladowe)
    return danePodzial

#dokładność mierzona w procentach
def miaraDokladnosci(aktualne, przewidywane):
    poprawne = 0
    for i in range(len(aktualne)):
        if aktualne[i] == przewidywane[i]: #Sprawdzanie ile się zgadza
            poprawne +=1
    return poprawne / float(len(aktualne))*100.00 #wyliczanie dokładności i przeliczanie na procenty

#Ewaluacja algorytmu z wykorzystaniem powyższego podziału
def ewaluacja(dane, algorytm, nSkladowe, *args):
    skladowe = podzial(dane, nSkladowe)
    wynik = list() #deklarowanie listy na dane wyjsciowe
    #skladanie segregowanie wynikow
    for skladowa in skladowe:
        train_set = list(skladowe)
        train_set.remove(skladowa)
        train_set = sum(train_set, [])
        test_set = list()
        for row in skladowa:
            kopiaWiersza = list(row)
            test_set.append(kopiaWiersza)
            kopiaWiersza[-1] = None
        #wykonywanie kilku poprzednih algorytmow
        przewidywana = algorytm(train_set, test_set, *args)
        aktualna = [row[-1] for row in skladowa]
        dokladnosc = miaraDokladnosci(aktualna, przewidywana)
        wynik.append(dokladnosc)
    return wynik

#Dzielenie danych na podstawie atrybutów i wartości atrybutów
def testowyPodzial(index, wartosc, dane):
    lewa, prawa = list(), list() #Tworzenie gałęzi drzewa
    for wiersz in dane: #Pętla odpowiadająca za podział
        if wiersz[index] < wartosc:
            lewa.append(wiersz)
        else:
            prawa.append(wiersz)
    return lewa, prawa

#obliczanie współczynnika gini do podziału danych
def wspolczynnikGini(grupy, wartosciKlasy):
    gini = 0.0 #ustalanie pierwotnej wartości współczynnika, aby poprawnie się kod kompilował
    for wartoscKlasy in wartosciKlasy:
        for grupa in grupy:
            wielkosc = len(grupa) #przypisywanie do zmiennej rozmiaru pobranej grupy
            if wielkosc == 0:
                continue    #sprawdzanie czy grupa nie jest pusta, co przeszkodziło by w kompilacji
            proporcje = [wiersz[-1] for wiersz in grupa].count(wartoscKlasy)/float(wielkosc) #Sprawdzanie proporcji wielkosci grupy do calej palety danych
            gini += (proporcje * (1.0 - proporcje))
    return gini

#Wybieranie najlepszego podziału. Pobiera dane z różnej wielkości rozmiarem danych i cechy wejścia jako argumenty definicji
def wybierzPodzial(dane, nCechy):
    wartoscKlasy = list(set(row[-1] for row in dane))#sprawdzanie wartości całej klasy
    indexB, wartoscB, punktyB, grupy_B = 999, 999, 999, None #przypisanie wstępnych wartości w celu uniknięcia błędów kompilacji
    cechy = list() #przygotowywanie pustej listy na sprawdzanie cech
    while len(cechy) < nCechy: #pętla uzupełniająca listę
        index = randrange(len(dane[0])-1)
        if index not in cechy:
            cechy.append(index) #dodawanie do listy cech
    for index in cechy:
        for wiersz in dane:
            grupy = testowyPodzial(index, wiersz[index], dane) #funkcja pomocnicza, która dzieli w potencjalnych miejscach
            gini = wspolczynnikGini(grupy, wartoscKlasy) #Współczynnik gini sprawdza "koszt" podziału
            if gini < punktyB:
                indexB, wartoscB, punktyB, grupy_B = index, wiersz[index], gini, grupy
    return {'index':indexB, 'wartosc':wartoscB, 'grupy':grupy_B}

#Tworzenie węzła do terminala
def toTerminal(grupa):
    wyjscia = [row[-1] for row in grupa]
    return max(set(wyjscia), key=wyjscia.count)

#Tworzenie podzialu do węzła terminala
def podzialT(wezel, maxGlebokosc, minRozmiar, nCechy, glebokosc):
    lewa, prawa = wezel['grupy']
    del(wezel['grupy'])
    #sprawdzanie braku podzialu
    if not lewa or not prawa:
        wezel['lewa'] = wezel['prawa'] = toTerminal(lewa+prawa)
        return
    #sprawdzanie maksymalnej glebokosci
    if glebokosc >= maxGlebokosc:
        wezel['lewa'], wezel['prawa'] = toTerminal(lewa), toTerminal(prawa)
        return
    #proces dla lewego dziecka
    if len(lewa) <= minRozmiar:
        wezel['lewa'] = toTerminal(lewa)
    else:
        wezel['lewa'] = wybierzPodzial(lewa, nCechy)
        podzialT(wezel['lewa'], maxGlebokosc, minRozmiar, nCechy, glebokosc+1)
    #proces dla prawego dziecka
    if len(prawa) <= minRozmiar:
        wezel['prawa'] = toTerminal(prawa)
    else:
        wezel['prawa'] = wybierzPodzial(prawa, nCechy)
        podzialT(wezel['prawa'], maxGlebokosc, minRozmiar, nCechy, glebokosc + 1)

#budowanie drzewa decyzyjnego
def budowanieDrzewa(train, maxGlebokosc, minRozmiar, nCechy):
    korzen = wybierzPodzial(train, nCechy)
    podzialT(korzen, maxGlebokosc, minRozmiar, nCechy, 1)
    return korzen

#Przewidywanie za pomocą drzewa decyzyjnego
def predykcja(wezel, row):
    if row[wezel['index']]<wezel['wartosc']:
        if isinstance(wezel['lewa'], dict):
            return predykcja(wezel['lewa'], row)
        else:
            return wezel['lewa']
    else:
        if isinstance(wezel['prawa'], dict):
            return predykcja(wezel['prawa'], row)
        else:
            return wezel['prawa']

#Tworzenie losowej probki z danych z zastapieniem
def podProbka(dane, stosunek):
    probka = list()
    nProbka = round(len(dane)*stosunek)
    while len(probka)<nProbka:
        index = randrange(len(dane))
        probka.append(dane[index])
    return probka

#predykcja z workiem drzew
def predykcjaWorek(drzewa, row):
    predykcje = [predykcja(drzewo, row) for drzewo in drzewa]
    return max(set(predykcje), key=predykcje.count)

#właściwy algorytm losowego lasu
def losowyLas(train, test, maxGlebokosc, minRozmiar, wielkoscProbki, nDrzew, nCechy):
    drzewa = list()
    for i in range(nDrzew):
        probka = podProbka(train, wielkoscProbki)
        drzewo = budowanieDrzewa(probka, maxGlebokosc, minRozmiar, nCechy)
        drzewa.append(drzewo)
    predykcje = [predykcjaWorek(drzewa, row) for row in test]
    return predykcje

#Testowanie algorytmu losowego lasu
seed(1)
#wczytywanie i przygotowanie danych
while True:
    try:
        nazwaPliku = input('podaj nazwę pobieranego pliku (bez rozszerzenia)(przykładowy test): ') + '.csv'
        break
    except ValueError:
        print('Błędna wartość wprowadź ponownie')
dane = load_csv(nazwaPliku)
#konwersja atrybutów tekstowych na liczby zmiennoprzecinkowe
for i in range(0, len(dane[0])-1):
    strToFloat(dane, i)
#konwersja klas kolumn na liczby całkowite
strToInt(dane, len(dane[0]))
#ewaluacja algorytmu
while True:
    try:
        nSkladowe = int(input('Podaj liczbę gałęzi drzewa, (na przykłąd 5): '))
        maxGlebokosc = int(input('Podaj maksymalną głębokość drzewa (na przykład 10): '))
        minWielkosc = int(input('Podaj minimalną wielkość gałęzi (na przykład 1): '))
        wielkoscProbki = float(input('Podaj wielkość pobieranej próbki (na przykład 1.0): '))
        break
    except ValueError:
        print('Błędna wartość! wprowadź ponownie')

Drzew = list()
ile = int(input('Podaj jaką liczbę ilości drzew chcesz sprawdzić (na przykład 3)(przykładowe liczby to 1,3,5)(im więcej drzew oraz kombinacji tym dłuższe działanie skryptu!)'))
for i in range(0,ile):
    print('podaj rozmiar lasu numer %s: ' %i)
    d = int(input())
    Drzew.append(d)

print('Tworzenie drzew...')
nCechy = int(sqrt(len(dane[0])-1))
for nDrzew in Drzew:
    wynik = ewaluacja(dane, losowyLas, nSkladowe, maxGlebokosc, minWielkosc, wielkoscProbki, nDrzew, nCechy)
    print('Drzewa: %d' % nDrzew)
    print('Wynik: %s' % wynik)
    print('Średnia precyzja: %.3f%%' % (sum(wynik)/float(len(wynik))))