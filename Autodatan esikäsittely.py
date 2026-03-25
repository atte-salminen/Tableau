"""
Tekijä: Atte Salminen, atte.salminen@tuni.fi

"""
import pandas as pd
import json
import sqlite3


def prosessoi_ajoneuvodata():
    # 1. Tiedoston lukeminen
    filename = "TieliikenneAvoinData_31_12_2025.csv"
    df = pd.read_csv(filename, sep=';', encoding='latin-1', low_memory=False)


    # 2. Perussuodatukset
    # Jätetään M1 ja M1G, yksityiskäyttö (1.0), tietyt korityypit ja ne joilla on käyttövoima
    sallitut_korityypit = ['AA', 'AB', 'AC', 'AD', 'AE', '1.7']
    df = df[df['ajoneuvoluokka'].isin(['M1', 'M1G'])]
    df = df[df['ajoneuvonkaytto'] == 1.0]
    df = df[df['korityyppi'].isin(sallitut_korityypit)]
    df = df.dropna(subset=['kayttovoima'])

    # 3. Sarakkeiden valinta
    valitut_sarakkeet = [
        'ensirekisterointipvm', 'kayttoonottopvm', 'vari', 'omamassa',
        'ajonKokPituus', 'ajonLeveys', 'kayttovoima', 'merkkiSelvakielinen',
        'mallimerkinta', 'kaupallinenNimi', 'kunta', 'NEDC_Co2',
        'matkamittarilukema'
    ]
    df = df[valitut_sarakkeet]

    # 4. Kuntatietojen käsittely
    with open('kuntakoodit.json', 'r', encoding='utf-8') as f:
        kuntadata = json.load(f)

    # 2. Luodaan sanakirja käyttämällä indeksejä [0] ja [1]
    # item[0] on koodi (esim. "020") ja item[1] on nimi (esim. "Akaa")
    kuntakoodit_dict = {int(item[0]): item[1] for item in kuntadata}


    df['kunta_koodi'] = pd.to_numeric(df['kunta'], errors='coerce')

    # 3. Tehdään map-operaatio
    df['kunta_nimi'] = df['kunta_koodi'].map(kuntakoodit_dict)

    osuma_maara = df['kunta_nimi'].notna().sum()

    # 4. Poistetaan ne, joilta puuttuu kuntatieto (NaN) tai nimi on kielletty
    kielletyt = ["Tuntematon", "Ulkomaat", "Pohjoismaat"]
    df = df.dropna(subset=['kunta'])
    df = df[~df['kunta'].isin(kielletyt)]

    df['kunta'] = df['kunta_nimi']
    df = df.dropna(subset=['kunta'])


    # 5. Päivämäärien käsittely
    def korjaa_pvm(pvm):
        # Jos arvo on tyhjä, palautetaan se sellaisenaan
        if pd.isna(pvm) or pvm == '':
            return pvm

        # Muutetaan tekstiksi ja poistetaan mahdolliset .0 päätteet (jos float-luku)
        pvm_str = str(pvm).strip()
        if pvm_str.endswith('.0'):
            pvm_str = pvm_str[:-2]

        # Jos päivämäärässä on jo pisteitä (esim. 02.10.2003), se on jo hyvä.
        # Tehtävän 0000-korjaus koskee vain YYYYMMDD-muotoista dataa.
        if '.' in pvm_str:
            return pvm_str

        # Jos pvm on pituudeltaan 8 merkkiä ja loppuu 0000 (esim. 20030000)
        # niin asetetaan päiväksi ensimmäinen tammikuuta (0101)
        if len(pvm_str) == 8 and pvm_str.endswith('0000'):
            return pvm_str[:4] + '0101'

        return pvm_str

    # Korjataan YYYY0000 -> YYYY0101 ja muutetaan datetime-muotoon
    for col in ['ensirekisterointipvm', 'kayttoonottopvm']:
        # Korjataan 0000-muodot ensin tekstinä
        df[col] = df[col].apply(korjaa_pvm)

        # Muutetaan datetimeksi. dayfirst=True auttaa suomalaisten päivämäärien kanssa.
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce', format='mixed')

    # Poistetaan rivit, joilta puuttuu jompikumpi päivämäärä
    df = df.dropna(subset=['ensirekisterointipvm', 'kayttoonottopvm'])

    # 6. Sähköautojen CO2 ja väriarvon korjaus
    df['kayttovoima'] = df['kayttovoima'].astype(str).str.strip()

    # Listataan kaikki mahdolliset tekstimuodot koodille 4
    sahko_koodit = ['4', '4.0', '04']
    df.loc[df['kayttovoima'].isin(sahko_koodit), 'NEDC_Co2'] = 0

    # --- VÄRI ---
    # Muutetaan -1 (tekstinä tai numerona) muotoon pd.NA
    df.loc[df['vari'].astype(str).str.contains('-1'), 'vari'] = pd.NA

    # 7. Merkkien puhdistus ja yhdenmukaistaminen

    # Erikoistapaukset kaupallisen nimen mukaan
    df.loc[df['kaupallinenNimi'].isin(
        ['SEBRING', 'CROSSFIRE']), 'merkkiSelvakielinen'] = 'Chrysler'
    df.loc[(df['kaupallinenNimi'] == 'XJ') &
           (df['merkkiSelvakielinen'] == 'Daimler'), 'merkkiSelvakielinen'] = 'Jaguar'

    # Sanakirjapohjaiset korvaukset
    korvaukset = {
        "QUATTRO": "Audi", "Quattro": "Audi",
        "ALPINA": "BMW", "Alpina": "BMW", "BMW Alpina": "BMW", "BMW i": "BMW",
        "BWW": "BMW",
        "GM Daewoo": "Daewoo",
        "FORD-CNG-TECHNIK": "Ford", "Ford-TEC": "Ford",
        "Hundai": "Hyundai",
        "Jaguar Land Rover Limited": "Jaguar",
        "Lada-Vaz": "Lada", "Niva": "Lada",
        "DaimlerChrysler": "Mercedes-Benz", "Daimler": "Mercedes-Benz",
        "MERCEDES-AMG": "Mercedes-Benz", "Mercedes-AMG": "Mercedes-Benz",
        "Mercedes-Benz-CI": "Mercedes-Benz",
        "BMW MINI": "Mini",
        "POLESTAR": "Polestar",
        "SALEEN": "Saleen",
        "SKD": "Skoda", "Skida": "Skoda",
        "TESLA MOTORS": "Tesla", "Tesla Motors": "Tesla",
        "THINK": "Think",
        "TOYOTA": "Toyota",
        "VOLKSWAGEN": "Volkswagen", "VW": "Volkswagen",
        "Volkswagen, VW": "Volkswagen"
    }
    df['merkkiSelvakielinen'] = df['merkkiSelvakielinen'].replace(korvaukset)

    # 8. Lopullinen merkkien karsinta
    sallitut_merkit = [
        "Acura", "Alfa Romeo", "Aston Martin", "Audi", "BMW", "Bentley",
        "Buick", "Cadillac",
        "Chevrolet", "Chrysler", "Citroen", "Cupra", "DS", "Dacia", "Daewoo",
        "Daihatsu",
        "Dodge", "Ferrari", "Fiat", "Ford", "Honda", "Hyundai", "Infiniti",
        "Jaguar",
        "Jeep", "Kia", "Lada", "Lamborghini", "Lancia", "Land Rover", "Lexus",
        "Lincoln",
        "Lotus", "MAN", "MCC", "MG", "MINI", "Maserati", "Maybach", "Mazda",
        "Mercedes-Benz",
        "Mini", "Mitsubishi", "Morgan", "Nissan", "Opel", "Peugeot",
        "Plymouth", "Pontiac",
        "Porsche", "Range-Rover", "Renault", "Rolls-Royce", "Rover", "Saab",
        "Saleen",
        "Scion", "Seat", "Skoda", "Smart", "Ssangyong", "Subaru", "Suzuki",
        "Tesla",
        "Think", "Toyota", "Vauxhall", "Volkswagen", "Volvo"
    ]
    df = df[df['merkkiSelvakielinen'].isin(sallitut_merkit)]

    valitut_sarakkeet = [
        'ensirekisterointipvm', 'kayttoonottopvm', 'vari', 'omamassa',
        'ajonKokPituus', 'ajonLeveys', 'kayttovoima', 'merkkiSelvakielinen',
        'mallimerkinta', 'kaupallinenNimi', 'kunta', 'NEDC_Co2',
        'matkamittarilukema'
    ]

    df = df[valitut_sarakkeet]


    conn = sqlite3.connect('autodata.db')
    df.to_sql('rekisteroinnit', conn, if_exists='replace', index=False)
    conn.close()


if __name__ == "__main__":
    prosessoi_ajoneuvodata()
