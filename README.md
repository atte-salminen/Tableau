Tässä projektissa analysoidaan Traficomin avointa ajoneuvodataa. Painopisteenä on seurata autokannan sähköistymistä ja CO2-päästöjen kehitystä.

Dashboardin sisältö
-  Käyttövoimatrendi: Käyttövoimien markkinaosuuksien muutos aikasarjana.
-  Päästöanalyysi: Uusien autojen keskimääräisten CO2-päästöjen kehityskaari.
-  Interaktiivisuus: Automerkkikohtainen suodatin, joka päivittää kaikki dashboardin näkymät.
-  Yhteenvetotaulukot: Tarkat lukumäärät ja summatulokset eri kategorioista.

Datan esikäsittely (Python & Pandas)
Ennen visualisointia raakadata siivottiin ja muokattiin Pythonilla. Esikäsittelyssä tehtiin seuraavat vaiheet:
-  Datan koon optimointi: Poistettiin analyysin kannalta tarpeettomat sarakkeet
-  Puuttuvien arvojen käsittely: Siivottiin ja yhtenäistettiin havainnot, joista puuttui kriittistä tietoa (kuten päästöt tai kunta).
-  Kategorioiden ryhmittely: Useat kymmenet polttoaineluokat tiivistettiin neljään pääryhmään (Bensiini, Diesel, Sähkö ja Muut/Hybridit).
-  Tyypinmuunnokset: Päivämäärät ja numeeriset arvot muunnettiin formaattiin, jota Tableau osaa käsitellä aikasarjoina.

Käytetyt työkalut
-  Python (Pandas): Datan puhdistus ja esikäsittely.
-  Tableau Public: Visualisointi ja interaktiivinen dashboard.

Visualisointi: https://public.tableau.com/app/profile/atte.salminen7529/viz/Autodata_17741978703720/Dashboard1
