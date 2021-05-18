# BPMN-Models

## Struktura
- [app.py]() - główny plik programu
- [reading_from_file]() - ładowanie danych z pliku
- [getting_relations]() - odkrywanie relacji
- [graph.py]() - tworzenie modelu w postaci grafu

## Instalacja
1. Flask
  `$ pip install flask`
2. OpyenXes
  `$ pip install opyenxes`
3. PyGraphviz
  Zgodnie z instrukcjami na [stronie](https://pygraphviz.github.io/documentation/stable/install.html#install)

## Uruchomienie
1. W konsoli:
  `$ python app.py`
2. Następnie w przeglądarce:
  `http://localhost:5000/`
  
## Obsługa
Wszystkie pliki powinny znajdować się w katalogu _resources_.
Należy wybrać plik za pomocą przycisku _Przeglądaj..._, a następnie potwierdzić przyciskiem "Załaduj". 
Zostanie wyświetlony model zbudowany na podstawie logów z pliku.
