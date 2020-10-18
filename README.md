# air_traffic_prognosis
Celem tego projektu jest nauczenie sieci neuronowej przewidywać czy samolot przyleci przed czasem, na czas czy spóźni się. Dane są zbierane z internetu ze strony flightradar24.com oraz Wikipedii. 
# Korzystanie ze skryptu

Aby uruchomić zbieranie danych o samolotach najpierw należy w pliku airports.txt wpisać kody IATA lotnisk oddzielone spacją bez żadnych dodatkowych znaków. Jeśli skrypt jest uruchamiany po raz pierwszy dla podanej daty należy upewnić się, że plik this_day_airports.json jest wyczyszczony i w razie potrzeby usunąć jego zawartość. Następnie, należy wywołać funkcję data_gathering.data.controler.data_controler oraz jako argumenty podać ścieżkę do pliku chromedriver, datę w odpowiednim formacie (na przykład "Wednesday, Oct 14”) oraz plik do którego należy zapisać dane (na przykład “flights1.json”). Wszystkie pliki z rozszerzeniem .json znajdują się w folderze json.

Aby rozpocząć proces uczenia sieci, najpierw należy załadować dane za pomocą funkcji machine_learning.data_preprocessing.load_data a następnie załadowane dane przekazać do odpowiedniej funkcji z modułu data_preprocessing w zależności od rodzaju modelu jaki będzie stosowany (w module data_preprocessing znajdują się komentarze wyjaśniające działanie funkcji). Moduł models.py zawiera natomiast funkcje zwracające konkretne modele sieci neuronowych.  

# Paczki

* data_gathering - web scrapping w celu pobrania danych o lotach i zapisywanie ich do plików json
* machine_learning - preprocessing danych z plików json oraz tworzenie modeli sieci neuronowych

# Paczka data_gathering

Package ten zawiera następujące moduły:

* data_controler.py
* common_functions.py
* destination_data.py
* origin_data.py
* runways_coordinates.py

## Moduł data_controler.py

Jest on odpowiedzialny za wywoływanie funkcji z innych modułów. Stanowi on swego rodzaju interfejs użytkownika. Funkcja data_controler przyjmuje dwa parametry: 

* datę w formacie takim jak na liście przylotów/odlotów na stronie www.flightradar24.com (na przykład: “Tuesday, Oct 13”),

* nazwa pliku do jakiego będą zapisywane loty (na przykład “flights1.json”).

Z pliku airports.txt są wczytywane kody lotnisk, z których program będzie miał pobrać dane. 
Jeżeli skrypt był już włączany dla danej daty to w pliku this_day_airports.json znajdują się dane na temat pogody i ruchu lotniczego lotnisk, 
które program zdążył sprawdzić. Pomaga to zaoszczędzić czas gdyż nie trzeba kilkukrotnie pobierać ze strony danych dla tego samego lotniska.

W pętli przechodzącej po lotniskach są wykonywane następujące czynności:
1. Tworzony jest obiekt klasy DestinationData z modułu destination_data.py. Jego atrybut dest_data jest listą lotów przylatujących na dane lotnisko. Każdy lot zawiera informacje o planowanej godzinie przylotu, prawdziwej godzinie przylotu, numerze lotu, warunkach pogodowych oraz operacjach lotniczych panujących w oknie czasu +/- 30min od planowanej godziny przylotu, opóźnieniu.

2. Dla każdego lotniska jest wykonywana pętla po przylatujących lotach.
     * Dla każdego lotu jest tworzony obiekt klasy OriginData z modułu origin_data.py.
     * Sprawdzane jest, czy lotnisko, z którego samolot przyleciał już wystąpiło danego dnia. Jeśli tak, to dane na temat ruchu na lotnisku jak i i pogody są pobierane    ze zmiennej przechowującej dane z this_day_airports.json. W przeciwnym razie jest wywoływana metoda get_from_web() obiektu klasy OriginData w celu pobrania tych  danych z internetu. Następnie dane pobrane przy pomocy tej metody są zapisywane do pliku this_day_airports.json.

3. Po wywołaniu metody get_origin_data() obiektu klasy OriginData są obliczane oraz zwracane ruch oraz pogoda na lotnisku początkowym w oknie czasu +/- 30min od planowanego wylotu samolotu i informacja czy samolot był opóźniony przy poprzednim locie. 

4. Dane na temat lotu są aktualizowane o dane z lotniska początkowego.

5. Na koniec dane lotu są aktualizowane o ilości oraz kierunek pasów startowych na lotnisku początkowym i docelowym, współrzędne geograficzne obu lotnisk oraz dystans między lotniskami.


## Moduł destination_data.py

Moduł ten zawiera klasę DestinationData. Przy tworzeniu obiektu trzeba podać następujące dane: ścieżkę do chromedriver, kod lotniska oraz datę.
W metodzie __init__ są wywoływane dwie metody klasowe. Pierwsza z nich get_destination_airport_data() zwraca krotkę z listą przylotów, listą odlotów oraz listą z danymi pogodowymi. Druga metoda destination_data() zwraca listę z informacjami o przylatujących lotach (pogodzie, ruchu lotniczym w momencie przylotu) w oparciu o dane zebrane przez metodę get_destination_airport_data().<br /><br />

**Metoda get_destination_airport_data():**

Na stronie flightradar24.com otwierana jest zakładka Arrivals dla danego lotniska. Pobierane są następnie informacje o wszystkich przylotach z danego dnia. Następnie program przechodzi do zakładki Departures na stronie i pobiera dane o odlotach danego dnia. Na koniec z zakładki Weather są pobierane dane dotyczące pogody z danego dnia. Metoda zwraca krotkę zawierającą trzy listy: arrivals, departure, weather.<br /><br />

**Metoda destination_data():**

Wykonywana jest pętla po wszystkich lotach przylatujących. Zapisywane są tylko loty posiadające informację o numerze rejestracyjnym oraz czasie lądowania. Pozostałe są wciąż używane do obliczenia ruchu na lotnisku. Ruch na lotnisku dla każdego lotu jest równy ilości planowanych lądowań oraz startów w okresie czasu +/- 30 min od godziny planowanego lądowania. Poszczególne parametry pogodowe dla każdego lotu to średnia tych parametrów mieszczących się w czasie +/- 30 min od czasu planowanego lądowania. Jeśli w tym okresie nie ma dostępnych danych pogodowych to jest wyciągana średnia z dwóch pomiarów - najbliższy przed planowanym lądowaniem oraz najbliższy po planowanym lądowaniu. Metoda zwraca listę słowników z informacjami dotyczącymi pogody i ruchu lotniczego w godzinie przylotu, opóźnieniu, godzinie przylotu, planowanej godzinie przylotu, numerze lotu, numerze rejestracji samolotu.

## Moduł origin_data.py

Moduł ten zawiera klasę klasę OriginData oraz dwie funkcje będące dekoratorami funkcji z modułu common_functions.py . 
Przy tworzeniu obiektu klasy OriginData trzeba podać ścieżkę do chromedriver, kod lotniska, datę, numer lotu, numer rejestracyjny samolotu, oraz planowaną godzinę przylotu do lotniska docelowego. Klasa ta posiada dwie metody: get_from_web() oraz get_origin_data().<br /><br />

**Metoda get_from_web():**

Najpierw skrypt na serwisie flightradar24.com wchodzi na podstronę z historią lotów danego samolotu. Następnie jest sprawdzane z jakiego lotniska przyleciał i skrypt wchodzi na podstronę tego lotniska. Z zakładki Arrivals są zbierane jedynie godziny przylotów poszczególnych samolotów. Tak samo jest z lotami odlatującymi w zakładce Departures. Z zakładki Weather są zbierane dane dotyczące pogody w danym dniu. Metoda zwraca krotkę zwierającą listy arrivals, departures, weather.<br /><br />

**Metoda get_origin_data(arrivals, departures, weather_departure):**

Najpierw na serwisie flightradar24.com zostaje włączona podstrona z historią lotów danego samolotu. Znajdywany jest rekord z interesującym nas lotem. Skrypt sprawdza planowaną i prawdziwą godzinę przylotu na poprzednie lotnisko aby obliczyć czy już wtedy nie był opóźniony. Następnie obliczana jest ilość samolotów przylatujących i odlatujących w okresie czasu +/- 30 min od planowanej godziny wylotu tak samo jak warunki pogodowe w tym oknie czasowym. Metoda zwraca słownik z informacjami o pogodzie i ruchu w godzinie odlotu oraz informacja o opóźnieniu w poprzednim locie.<br /><br />

## Moduł common_functions.py

Moduł zawiera funkcje używane w innych modułach. W komentarzach w kodzie jest wyjaśnione co robi każda funkcja.

## Moduł runways_coordinates.py

W module znajdują się funkcje odpowiedzialne za wyszukiwanie informacji o współrzędnych oraz ilości i kierunkach pasów startowych na lotniskach. Znajduje się tu również kilka pomocniczych funkcji, których działanie można zrozumieć dzięki komentarzom w kodzie źródłowym.<br /><br />

**Funkcja runways_coordinates(path_to_chromedriver, airports_codes:, airports):**

Funkcja ta dla każdego lotniska z listy airports_codes wyszukuje na Wikipedii informacji o pasach startowych oraz współrzędnych lotniska. Następnie te dane są dodawane do lotnisk w liście airports. Zwracana zostaje zaktualizowana lista airports.<br /><br />

**Funkcja update_flight_info(flight_json_data, airports):**

Funkcja ta dla każdego lotu z listy flight_json_data dodaje informacje dotyczące lotniska początkowego i lotniska docelowego. Te informacje to współrzędne, kierunki pasów startowych oraz dystans między dwoma lotniskami Zwracana zostaje zaktualizowana lista flight_json_data.<br /><br />

**Funkcja get_runways_and_distance(path_to_chromedriver, flights_json_data):**

(Funkcja może przyjmować listę lotów flights_json_data lecz w praktyce jest to jednoelementowa lista)

Najpierw następuje próba wczytania pliku airport_data.json . Następnie jest sprawdzane czy lotniska początkowe lub docelowe lotów z listy flights_json_data znajdują się wśród wczytanych lotnisk. Jeśli nie, takie lotnisko jest dodawane do listy nowych lotnisk. Wszystkie nowe lotniska są przekazywane do funkcji runways_coordinates(). Dzięki temu nowe lotniska z dodanymi informacjami o współrzędnych i pasach startowych będą mogły zostać dodane do pliku airport_data.json . Loty z listy flights_json_data są aktualizowane o informacje lotniskowe poprzez wywołanie funkcji update_flight_info(). 

Jeśli nie udało się odczytać danych z pliku airport_data.json to funkcja runways_coordinates jest wywoływana dla każdego niepowtarzającego się lotniska wśród lotów z listy flights_json_data, po czym zostają zapisane do pliku airport_data.json . Loty są następnie aktualizowane przez funkcję update_flight_info(). 

Funkcja zwraca zaktualizowaną listę flights_json_data.

# Paczka machine_learning

Package ten zawiera następujące moduły:
* data_preprocessing.py
* models.py

## Moduł data_preprocessing.py

Moduł ten zawiera funkcje dokonujące standaryzacji wartości zmiennych wprowadzanych do sieci neuronowej tak, aby miały mieściły się one w przedziale [0-1]. Następnie funkcje zmieniają listy na tablice ndarray o odpowiednich kształtach w zależności od tego, dla jakiego rodzaju sieci neuronowej są przygotowywane te dane.

## Moduł data_preprocessing.py

Moduł ten zwiera funkcje zwracające konkretne modele sieci neuronowych
