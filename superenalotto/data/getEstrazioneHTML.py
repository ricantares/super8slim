from bs4 import BeautifulSoup
import requests
import re

mesi = {
    'gennaio': '01',
    'febbraio': '02',
    'marzo': '03',
    'aprile': '04',
    'maggio': '05',
    'giugno': '06',
    'luglio': '07',
    'agosto': '08',
    'settembre': '09',
    'ottobre': '10',
    'novembre': '11',
    'dicembre': '12'
}

def getHTMLdocument(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to retrieve URL: {url} with status code {response.status_code}")


def getEstrazioniSuperenalotto(url_base, url_anno, url_mese):
    url = url_base + url_anno + "/" + url_mese 
    html_doc = getHTMLdocument(url)
    soup = BeautifulSoup(html_doc, 'html.parser')

    table = soup.find('table')
    table_body = table.find('tbody')

    rows = []
    for row in table.find_all('tr')[1:]:  
        cells = [td.text.strip() for td in row.find_all('td')]
        if len(cells) > 1:
            rows.append(cells) # non considera le righe vuote
    
    estrazioni = []
    for r in reversed(rows):
        data_concorso = (r[0].replace('\r\n', '')).split()
        data_gg = data_concorso[4] if len(data_concorso[4]) > 1 else '0' + data_concorso[4]
        data_mm = mesi[data_concorso[5].lower()]
        data_aaaa = data_concorso[6]
        estrazione = r[1].replace('\n\n', ';')
        if estrazione != 'In programmazione':
            estrazioni.append(data_aaaa + data_mm + data_gg + ';' + estrazione)    # estrazione    
        
    return estrazioni


def addEstrazioniToDataFile(data_file, estrazioni):
    with open(data_file, 'r', encoding='utf-8', newline='') as file:
        lines = file.readlines()

    if not lines:
        raise ValueError(f"Data file has no header: {data_file}")

    existing_dates = {
        line.partition(';')[0].strip()
        for line in lines[1:]
        if line.partition(';')[0].strip().isdigit()
    }

    line_ending = '\r\n' if lines[0].endswith('\r\n') else '\n'
    new_rows = []
    for row in sorted(estrazioni, key=lambda extraction: extraction.partition(';')[0]):
        date, separator, _ = row.partition(';')
        date = date.strip()
        if not separator or len(date) != 8 or not date.isdigit():
            raise ValueError(f"Invalid extraction row: {row!r}")
        if date in existing_dates:
            continue

        new_rows.append(row.rstrip('\r\n') + line_ending)
        existing_dates.add(date)

    if not new_rows:
        return 0

    header = lines[0]
    if not header.endswith(('\n', '\r')):
        header += line_ending

    with open(data_file, 'w', encoding='utf-8', newline='') as file:
        file.writelines([header, *reversed(new_rows), *lines[1:]])

    return len(new_rows)
###################################################################################################################################################################################
    
# Run as script
if __name__ == "__main__":        

    def main():
        
        import configparser
    
        # Configuration
        config = configparser.ConfigParser()
        config.read("config.ini")

        url_base = config.get('web_scraping', 'url')
        url_anno = config.get('web_scraping', 'year')
        first_month = int(config.get('web_scraping', 'ini_month'))
        last_month = int(config.get('web_scraping', 'last_month'))
        data_file = config.get('hystorical_data', 'data_file')
        for url_mese, mm in mesi.items():
            if first_month <= int(mm) <= last_month:
                print(url_mese, mm)
                estrazioni = getEstrazioniSuperenalotto(url_base, url_anno, url_mese)
                addEstrazioniToDataFile(data_file, estrazioni)
                # file_estrazioni = out_file_prefix + url_anno + "_" + url_mese + ".csv"
                # np.savetxt(file_estrazioni, estrazioni, delimiter=';', fmt='%s')

        return 0
    
    # Run main if executed directly
    if __name__ == "__main__":
        main()
