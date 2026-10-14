# Gjenerator Fjalëkalimesh

Aplikacion web lokal për gjenerimin e fjalëkalimeve dhe vlerësimin e forcës së tyre. Ndërfaqja është në shqip dhe përdor vetëm HTML, CSS dhe JavaScript vanilla. Nuk ka databazë: historiku i gjenerimeve ruhet vetëm në `localStorage` të shfletuesit.

## Veçoritë

- Gjenerim Random, Passphrase dhe PIN; gjenerim në grup deri në 50 rezultate unike.
- Përjashtime dhe kufizime të karaktereve për gjenerimin Random.
- Analizë e forcës me kontroll për fjalëkalime të njohura, sekuenca, modele tastiere, përsëritje, data dhe fjalë të zakonshme.
- Historik lokal i maskuar si parazgjedhje, kopjim dhe përpjekje për pastrim të clipboard-it pas 30 sekondash.
- Modalitet i errët automatik sipas preferencës së sistemit dhe zgjedhje manuale.
- Politika bazë sigurie për përgjigjet HTTP; përgjigjet API nuk ruhen në cache.

## Kërkesat

- Python 3.10 ose më i ri.
- Flask për aplikacionin dhe pytest për testet. Varësitë e runtime-it dhe të testimit janë të ndara në `requirements.txt`.

## Instalimi

Nga direktoria e projektit:

```bash
python -m venv .venv
```


```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Instalo Flask:

```bash
python -m pip install -r requirements.txt
```

Për instalimin e varësisë së testimit:

```bash
python -m pip install -r requirements-dev.txt
```

## Nisja

```bash
python app.py
```

Hap [http://127.0.0.1:5000](http://127.0.0.1:5000) në shfletues. Serveri lidhet vetëm në loopback (`127.0.0.1`), jo në rrjetin publik.

## Testet

```bash
python -m pytest -q
```

## API

Të gjitha rrugët API kthejnë JSON, header-in `Cache-Control: no-store`, dhe përgjigje gabimi `{"error": "..."}` me status `400` për input të pavlefshëm.

### Gjenero një fjalëkalim Random

```bash
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"mode":"random","length":20,"use_lower":true,"use_upper":true,"use_digits":true,"use_symbols":true}'
```

### Gjenero Passphrase

```bash
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"mode":"passphrase","count":3,"words":4,"separator":"-","capitalize":"first","add_number":true}'
```

### Gjenero PIN

```bash
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"mode":"pin","length":6,"no_repeat":true,"no_sequences":true,"no_all_same":true}'
```

### Analizo fjalëkalim

```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"password":"Example-Password-2026!","user_inputs":["example"]}'
```

### Numri i fjalëve të passphrase

```bash
curl http://127.0.0.1:5000/api/wordlist/info
```

## Privatësia dhe siguria

- Gjenerimi i vlerave të rastësishme përdor modulin standard `secrets`; aplikacioni nuk përdor `random`.
- Fjalëkalimet e analizuara përpunohen në kërkesën lokale dhe nuk shkruhen në log-e apo databazë.
- Historia e fjalëkalimeve ruhet në `localStorage` dhe nuk dërgohet në server. Përdor “Fshi të gjitha” për ta hequr përmbajtjen lokale të `localStorage`.
- API-ja dërgon `Cache-Control: no-store`; të gjitha përgjigjet përfshijnë CSP, `X-Content-Type-Options: nosniff` dhe `X-Frame-Options: DENY`.
- Vlerësimet e kohës së thyerjes janë vlerësime teorike, jo garanci. Rezultati i kontrolluesit nuk zëvendëson një menaxher fjalëkalimesh apo praktika të sigurta autentikimi.

## Struktura

```text
app.py
core/
  charsets.py
  common_data.py
  generator.py
  strength.py
  wordlist.py
static/
  app.js
  style.css
templates/
  index.html
```
