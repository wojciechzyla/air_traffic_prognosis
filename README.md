# air_traffic_prognosis

## Packages

data_gathering - web scrapping w celu pobrania danych o lotach i zapisywanie ich do plików json
machine_learning - preprocessing danych z plików json oraz tworzenie modeli sieci neuronowych

## Package data_gathering

Package ten zawiera następujące moduły:

*data_controler.py
*common_functions.py
*destination_data.py
*origin_data.py
*runways_coordinates.py



# Moduł data_controler.py

Jest on odpowiedzialny za wywoływanie funkcji z innych modułów. Stanowi on swego rodzaju interfejs użytkownika. 
Funkcja data_controler przyjmuje dwa parametry: 

*datę w formacie takim jak na liście przylotów/odlotów na stronie www.flightradar24.com (na przykład: “Tuesday, Oct 13”),

*nazwa pliku do jakiego będą zapisywane loty (na przykład “flights1.json”).

Z pliku airports.txt są wczytywane kody lotnisk, z których program będzie miał pobrać dane. 
Jeżeli program był już włączany danego dnia to w pliku this_day_airports.json znajdują się dane na temat pogody i ruchu lotniczego lotnisk, które program zdążył sprawdzić. Pomaga to zaoszczędzić czas gdyż nie trzeba kilkukrotnie pobierać ze strony danych dla tego samego lotniska.

W pętli przechodzącej po lotniskach są wykonywane następujące czynności:
*Tworzony jest obiekt klasy DestinationData z modułu destination_data.py. Jego atrybut dest_data jest listą lotów przylatujących na dane lotnisko. Każdy lot zawiera informacje o planowanej godzinie przylotu, prawdziwej godzinie przylotu, numerze lotu, warunkach pogodowych oraz operacjach lotniczych panujących w oknie czasu +/- 30min od planowanej godziny przylotu, opóźnieniu. 

*Dla każdego lotniska jest wykonywana pętla po przylatujących lotach. 

  *Dla każdego lotu jest tworzony obiekt klasy OriginData z modułu origin_data.py. 

  *Sprawdzane jest, czy lotnisko, z którego samolot przyleciał już wystąpiło danego dnia. Jeśli tak, to dane na temat ruchu na lotnisku jak i i pogody są pobierane ze zmiennej przechowującej dane z this_day_airports.json. W przeciwnym razie jest wywoływana metoda get_from_web() obiektu klasy OriginData w celu pobrania tych danych z internetu. Następnie dane pobrane przy pomocy tej metody są zapisywane do pliku this_day_airports.json.

*Po wywołaniu metody get_origin_data() obiektu klasy OriginData są obliczane oraz zwracane ruch oraz pogoda na lotnisku początkowym w oknie czasu +/- 30min od planowanego wylotu samolotu i informacja czy samolot był opóźniony przy poprzednim locie.  

*Dane na temat lotu są aktualizowane o dane z lotniska początkowego. 

*Na koniec dane lotu są aktualizowane o ilości oraz kierunek pasów startowych na lotnisku początkowym i docelowym, współrzędne geograficzne obu lotnisk oraz dystans między lotniskami.


# Moduł destination_data.py

Moduł ten zawiera klasę DestinationData. Przy tworzeniu obiektu trzeba podać następujące dane: ścieżkę do chromedriver, kod lotniska oraz datę.
W metodzie __init__ są wywoływane dwie metody klasowe. Pierwsza z nich get_destination_airport_data() zwraca krotkę z listą przylotów, listą odlotów oraz listą z danymi pogodowymi. Druga metoda destination_data() zwraca listę z informacjami o przylatujących lotach (pogodzie, ruchu lotniczym w momencie przylotu) w oparciu o dane zebrane przez metodę get_destination_airport_data().
 
Metoda get_destination_airport_data(): 
Otwierana jest zakładka Arrivals dla danego lotniska. Pobierane są następnie informacje o wszystkich przylotach z danego dnia. Następnie program przechodzi do zakładki Departures na stronie i pobiera dane o odlotach danego dnia. Na koniec z zakładki Weather są pobierane dane dotyczące pogody. Metoda zwraca krotkę zawierającą trzy listy: arrivals, departure, weather.
 
Metoda destination_data():

Wykonywana jest pętla po wszystkich lotach przylatujących. Zapisywane są tylko loty posiadające informację o numerze rejestracyjnym oraz czasie lądowania. Pozostałe są wciąż używane do obliczenia ruchu na lotnisku.  Ruch na lotnisku dla każdego lotu jest równy ilości planowanych lądowań oraz startów w okresie czasu +/- 30 min od godziny planowanego lądowania. Poszczególne parametry pogodowe dla każdego lotu to średnia tych parametrów mieszczących się w czasie +/- 30 min od czasu planowanego lądowania. Jeśli w tym okresie nie ma dostępnych danych pogodowych to jest wyciągana średnia z dwóch pomiarów - najbliższy przed planowanym lądowaniem oraz najbliższy po planowanym lądowaniu. Metoda zwraca listę słowników z informacjami dotyczącymi pogody i ruchu lotniczego w godzinie przylotu, opóźnieniu, godzinie przylotu, planowanej godzinie przylotu, numerze lotu, numerze rejestracji samolotu.




Moduł origin_data.py

Moduł ten zawiera klasę klasę OriginData oraz dwie funkcje będące dekoratorami funkcji z modułu common_functions.py . 
Przy tworzeniu obiektu klasy OriginData trzeba podać ścieżkę do chromedriver, kod lotniska, datę, numer lotu, numer rejestracyjny samolotu, oraz planowaną godzinę przylotu do lotniska docelowego. Klasa ta posiada dwie metody: get_from_web() oraz get_origin_data().
 
Metoda get_from_web():

Najpierw program wchodzi na podstronę z historią lotów danego samolotu. Następnie jest sprawdzane z jakiego lotniska przyleciał i program wchodzi na podstronę tego lotniska. Z zakładki Arrivals są zbierane jedynie godziny przylotów poszczególnych samolotów. Tak samo jest z lotami odlatującymi w zakładce Departures. Z zakładki weather są zbierane dane dotyczące pogody w danym dniu. Metoda zwraca krotkę zwierającą listy arrivals, departures, weather.
 
Metoda get_origin_data(arrivals, departures, weather_departure): 
Najpierw zostaje włączona podstrona z historią lotów danego samolotu. Znajdywany jest rekord z interesującym nas lotem. Program sprawdza planowaną i prawdziwą godzinę przylotu na poprzednie lotnisko aby zobaczyć czy już wtedy nie był opóźniony. Następnie obliczana jest ilość samolotów przylatujących i odlatujących w okresie czasu +/- 30 min od planowanej godziny wylotu tak samo jak warunki pogodowe w tym oknie czasowym. Metoda zwraca słownik z informacjami o pogodzie i ruchu w godzinie odlotu oraz informacja o opóźnieniu w poprzednim locie.



Moduł common_functions.py

Moduł zawiera funkcje używane w innych modułach. W komentarzach w kodzie jest wyjaśnione co robi każda funkcja.  

Moduł runways_coordinates.py

W module znajdują się funkcje odpowiedzialne za wyszukiwanie informacji o współrzędnych oraz ilości i kierunkach pasów startowych na lotniskach.



Funkcja runways_coordinates(path_to_chromedriver, airports_codes:, airports): 
Funkcja ta dla każdego lotniska z listy airports_codes wyszukuje na Wikipedii informacji o pasach startowych oraz współrzędnych lotniska. Następnie te dane są dodawane do lotnisk w liście airports.


Funkcja update_flight_info(flight_json_data, airports):

Funkcja ta dla każdego lotu z listy flight_json_data dodaje informacje dotyczące lotniska początkowego i lotniska docelowego. Te informacje to współrzędne, kierunki pasów startowych oraz dystans między dwoma lotniskami.


Funkcja get_runways_and_distance(path_to_chromedriver, flights_json_data):
(Funkcja może przyjmować listę lotów flights_json_data lecz w praktyce jest to jednoelementowa lista)

Najpierw następuje próba wczytania pliku airport_data.json . Następnie jest sprawdzane czy lotniska początkowe lub docelowe lotów z listy flights_json_data znajdują się wśród wczytanych lotnisk. Jeśli nie, takie lotnisko jest dodawane do listy nowych lotnisk. Wszystkie nowe lotniska są przekazywane do funkcji runways_coordinates(). Dzięki temu nowe lotniska będą mogły zostać dodane do pliku airport_data.json . Loty z listy flights_json_data są aktualizowane o informacje lotniskowe poprzez wywołanie funkcji update_flight_info(). 

Jeśli nie udało się odczytać danych z pliku airport_data.json to funkcja runways_coordinates jest wywoływana dla każdego niepowtarzającego się lotniska wśród lotów z listy flights_json_data, po czym zostają zapisane do pliku airport_data.json . Loty są następnie aktualizowane przez funkcję update_flight_info(). 

Funkcja zwraca zaktualizowaną listę flights_json_data.json .


W tym module znajduje się również kilka pomocniczych funkcji, których działanie można zrozumieć dzięki komentarzom w kodzie źródłowym.





Package machine_learning


Package ten zawiera następujące moduły: 
data_preprocessing.py 
models.py 
Moduł data_preprocessing.py

Moduł ten zawiera funkcje dokonujące standaryzacji wartości zmiennych wprowadzanych do sieci neuronowej tak, aby miały mieściły się one w przedziale [0-1]. Następnie funkcje zmieniają listy na tablice ndarray o odpowiednich kształtach w zależności od tego, dla jakiego rodzaju sieci neuronowej są przygotowywane te dane. Funkcje zwracają zestawy treningowe, testowe.


Moduł data_preprocessing.py

Moduł ten zwiera funkcje zwracające konkretne modele sieci neuronowych
