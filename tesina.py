import re
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

pd.set_option("display.max_rows", None, "display.max_columns",
              None)  # impostazione visualizzazione
pd.set_option('display.width', 1000)  # del dataframe
opt = Options()  # modalità di esecuzione del driver
opt.headless = True  # senza GUI


def bandi_veneto(n):
    chrome = webdriver.Chrome()
    chrome.get('https://bandi.regione.veneto.it/Public/Elenco?Tipo=1')

    descrizioni = []
    strutture = []
    scadenze = []
    i = 1  # parto dalla pagina 1
    while i < n + 1:
        risultati = WebDriverWait(chrome, 10).until(
            ec.visibility_of_all_elements_located(
                (By.TAG_NAME, 'tr')))
        risultati.pop(0)  # il primo 'tr' è nell’head 'th', inutile

        for ris in risultati:
            descrizioni.append(ris.find_element_by_class_name(
                'col-xs-12.col-sm-12.col-md-12.col-lg-12.padding-lateral'
                '-none.evidenzia').text)
            strutture.append(ris.find_element_by_class_name(
                'evidenzia.selenium-field-struttura').text)
            scadenze.append(
                ris.find_element_by_class_name('DtScadenza.evidenzia').text)
        i += 1
        try:
            chrome.find_element_by_link_text(str(i)).click()  # pag
            # successiva
        except:
            break
        WebDriverWait(chrome, 10).until(
            ec.visibility_of_all_elements_located(
                (By.CLASS_NAME,
                 'col-xs-12.col-sm-12.col-md-12.col-lg-12.padding-lateral'
                 '-none.evidenzia')))
        WebDriverWait(chrome, 10).until(
            ec.visibility_of_all_elements_located(
                (By.CLASS_NAME, 'evidenzia.selenium-field-struttura')))
        # Non aspetto il caricamento delle scadenze, perchè capita siano
        # omesse
    chrome.quit()
    return pd.DataFrame({'Scadenza': scadenze, 'Descrizione': descrizioni,
                         'Struttura': strutture})

df = bandi_veneto(2)
df.to_excel(
    r'C:\Users\giach\Desktop\TESI\output_scraping\bandi_veneto.xlsx',
    index=False, header=True)


def atti_veneto(n):
    if n > 12224:
        n = 12224
    if n < 0:
        print('Numero di pagine non valido')
        return None
    chrome = webdriver.Chrome()
    chrome.get(
        'https://bur.regione.veneto.it/BurvServices/Pubblica/ricerca.aspx')
    titoli = []
    descrizioni = []
    date = []
    chrome.find_element_by_id('cercaSemplice').click()  # cerca tutti gli
    # atti

    for i in range(0, n):
        for dt in chrome.find_elements_by_tag_name('dt'):  # titoli
            testo = dt.text
            match = re.search(r'(\d+/\d+/\d+)', testo)  # date
            date.append(match.group(1))
            titoli.append(testo)

        for dd in chrome.find_elements_by_tag_name('dd'):  # descrizioni
            descrizioni.append(dd.text)

        chrome.find_element_by_name(
            'navigazione$ctl06').click()  # successiva
        WebDriverWait(chrome, 10).until(
            ec.visibility_of_all_elements_located(
                (By.CLASS_NAME, 'body-burvet-search-result-item')))
    chrome.quit()
    return pd.DataFrame(
        {'Data:': date, 'Titolo': titoli, 'Descrizione': descrizioni})


df = atti_veneto(2)
df.to_excel(
    r'C:\Users\giach\Desktop\TESI\output_scraping\atti_veneto.xlsx',
    index=False, header=True)


def bandi_friuli(n):
    chrome = webdriver.Chrome()
    chrome.get(
        'http://www.regione.fvg.it/rafvg/cms/RAFVG/MODULI/bandi_avvisi/')
    pubs = []
    scads = []
    titolo = []
    strutt = []
    chrome.find_element_by_link_text('OK').click()
    i = 1

    while i < n + 1:
        risultati = WebDriverWait(chrome, 10).until(
            ec.visibility_of_all_elements_located(
                (By.CLASS_NAME, 'box-link.box.box-bando')))
        for ris in risultati:
            # date pubblicazione e scadenza
            testo_con_date = ris.find_element_by_class_name(
                'box-header-left').text  # es.'22.07.2020 - scadenza
            # 06.08.2020'

            date = re.findall(r'(\d+\.\d+\.\d+)', testo_con_date)
            pub = date[0]  # pubblicazione c'è sempre
            if len(date) > 1:  # se ci sono due date, la seconda è scadenza
                scad = date[1]
            else:
                scad = None
            pubs.append(pub)
            scads.append(scad)
            titolo.append(ris.find_element_by_tag_name('h3').text)
            strutt.append(ris.find_element_by_class_name('box-campo').text)

        i += 1
        try:
            chrome.find_element_by_link_text(
                str(i))  # pagina successiva
        except:
            break
        chrome.find_element_by_link_text(str(i)).click()

    chrome.quit()
    return pd.DataFrame(
        {'Pubblicazione': pubs, 'Scadenza': scads, 'Descrizione': titolo,
         'Struttura': strutt})


df = bandi_friuli(2)
df.to_excel(
    r'C:\Users\giach\Desktop\TESI\output_scraping\bandi_friuli.xlsx',
    index=False, header=True)


def atti_friuli(n, m):
    if n < 1999 or m > 2020 or n > m:
        print('Date sbagliate, inserire solo nell\'intervallo 1999-2020')
        return None
    chrome = webdriver.Chrome()
    anni = []
    titoli = []
    date = []

    for a in range(n, m + 1):
        if a > 2006:
            anni.append(
                'http://bur.regione.fvg.it/newbur/archivioBollettini?anno'
                '=' + str(a))
        else:
            anni.append(
                'http://www.regione.fvg.it/asp/bur/ricerca/archivio2'
                '/archivio.asp?anno=' + str(a))
    anni.reverse()

    for anno in anni:
        chrome.get(anno)
        yy = int(anno[-4:-1] + anno[-1])  # ricavo anno dall query string
        li = chrome.find_elements_by_tag_name('li')
        pagine = int(li[-2].text)  # il numero di pagine è presente nel
        # penultimo 'li'

        for i in range(1,
                       pagine + 1):  # iteratore delle pagine del dato anno
            if yy > 2006:
                chrome.get(anno + '&num_pag=' + str(i))
            else:
                chrome.get(
                    'http://www.regione.fvg.it/asp/bur/ricerca/archivio2'
                    '/archivio.asp?pag=' + str(i))

            t = chrome.find_elements_by_class_name('box-titolo')
            for ti in t:
                titoli.append(ti.text)
            d = chrome.find_elements_by_class_name('box-header-left')
            for data in d:
                date.append(data.text)
    chrome.quit()
    return pd.DataFrame({'Data': date, 'Titolo': titoli})


df = atti_friuli(2006,2007)
df.to_excel(
    r'C:\Users\giach\Desktop\TESI\output_scraping\atti_friuli.xlsx',
    index=False, header=True)


def bandi_trentino(n):
    chrome = webdriver.Chrome()
    chrome.get(
        'https://trentinosviluppo.it/it/Principale/Bandi_e_Appalti'
        '/Bandi_in_corso/Bandi_in_corso.aspx')
    pubb = []
    scad = []
    titoli = []
    risultati = chrome.find_elements_by_tag_name('tr')  # bandi attivi
    for d in risultati:
        titoli.append(d.find_element_by_tag_name('a').text)
        s = d.find_element_by_tag_name('p').text
        match = re.search(r'(\d+/\d+/\d+)', s)  # cerco la prima data
        pubb.append(match.group(1))
        match = re.search(r'(\d+/\d+/\d+.\d+:\d+)', s)  # cerco seconda:
        scad.append(match.group(1))

    chrome.find_element_by_link_text('Bandi scaduti').click()
    i = 1
    while i < n + 1:  # bandi scaduti
        risultati = WebDriverWait(chrome, 5).until(
            ec.visibility_of_all_elements_located((By.TAG_NAME, 'td')))
        for d in risultati:
            titoli.append(d.find_element_by_tag_name('a').text)
            paragrafi = d.find_elements_by_tag_name('p')
            testo = ''
            for p in paragrafi:
                testo = testo + p.text  # testo di tutti i paragrafi,
                # capita ce ne sia più di uno
            match = re.search(r'(\d+/\d+/\d+)',
                              testo)  # cerco la prima data
            pubb.append(match.group(1))
            match = re.search(r'(\d+/\d+/\d+.\d+:\d+)', testo)  # cerco
            scad.append(match.group(1))

        i += 1
        try:
            chrome.find_element_by_link_text(str(i)).click() #pagina succ
        except:
            break

    chrome.quit()
    return pd.DataFrame({'Pubblicaz.':pubb,'Scadenza': scad,
                         'Titolo': titoli})

df = bandi_trentino(2)
df.to_excel(
    r'C:\Users\giach\Desktop\TESI\output_scraping\bandi_trentino.xlsx',
    index=False, header=True)


def atti_trentino(n,m):
    chrome = webdriver.Chrome()
    chrome.get('http://www.regione.taa.it/burtaa/it/Ricerca123.aspx')
    date = []
    titoli = []
    descrizione = []

    for anno in range(n, m+1):
        selezione = Select(
            chrome.find_element_by_id('ctl00_ContentPlaceHolder1col_dAnno'))
        selezione.select_by_visible_text(str(anno))
        chrome.find_element_by_id(
            'ctl00_ContentPlaceHolder1col_lkCerca').click()
        # scrapo pagine
        i = 1
        while i<3:  # max pagine per anno
            WebDriverWait(chrome, 5).until(
                ec.presence_of_all_elements_located((By.TAG_NAME, 'li')))
            risultati = chrome.find_elements_by_class_name(
                'u-color-grey-90.u-padding-right-xxl.u-padding-r-all')
            for ris in risultati:
                titolo = ris.find_element_by_tag_name('strong').text
                titoli.append(titolo)
                testo = ris.find_element_by_class_name(
                    'u-lineHeight-l.u-text-r-xs.u-textSmooth.u-padding-r'
                    '-right').text
                match_descr = re.search(r'(\n.+\n)', testo)
                descrizione.append(match_descr.group(1).strip())
                match_data = re.search(r'(\d\d \w+ \d\d\d\d)', titolo)
                date.append(match_data.group(1))
            i += 1

            try:
                chrome.find_element_by_link_text(
                    'Pagina successiva').click()
            except:
                break

    chrome.quit()
    return pd.DataFrame(
        {'Data': date, 'Titolo': titoli, 'Descrizione': descrizione})
df = atti_trentino(2019,2020)
df.to_excel(
    r'C:\Users\giach\Desktop\TESI\output_scraping\atti_trentino.xlsx',
    index=False, header=True)

def bandi_bolzano(n):
    chrome = webdriver.Chrome()
    chrome.get(
        'https://www.ausschreibungen-suedtirol.it/index/index/locale/it_IT')
    oggetto = []
    tipo = []
    cig = []
    importo = []
    stato = []
    data = []
    diz = {0: oggetto, 1: tipo, 2: cig, 3: importo, 4: stato, 5: data}
    chrome.find_element_by_xpath(
        '/html/body/div/div[1]/div[2]/nav/div/div/div/table/tbody/tr/td['
        '2]/input').click()
    chrome.refresh()
    i = 1

    while i < n+1:
        righe = WebDriverWait(chrome, 5).until(
            ec.visibility_of_all_elements_located((By.TAG_NAME, 'tr')))
        del righe[:1]
        for riga in righe:
            col = riga.find_elements_by_tag_name('td')
            del col[0]
            for c in range(0,6):  # riempio le liste corrispondenti ad ogni
                # colonna
                diz[c].append(col[c].text)
        i += 1
        try:
            chrome.find_element_by_link_text(str(i))  #pagina successiva
        except:
            break
        chrome.find_element_by_link_text(str(i)).click()
    chrome.quit()
    l = ['Oggetto','Tipo', 'Cig', 'Importo', 'Stato', 'Pubbl.']
    di = {l[k]:v for (k,v) in diz.items()}
    return pd.DataFrame(di)

df = bandi_bolzano(2)
df.to_excel(
    r'C:\Users\giach\Desktop\TESI\output_scraping\bandi_bolzano.xlsx',
    index=False, header=True)
