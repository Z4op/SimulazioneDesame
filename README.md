# Simulazione d'esame

## 1). Creare un ambiente virtual in python3
*creo l'ambiente virtuale*
```
python3 -m venv .env
```
*attivare l'ambiente virtuale*
#### *Windows*
```
.\.env\Scripts\activate.ps1
```
#### *Linux/MacOS*
```
source .env/bin/activate
```

## 2). installo le dipendenze
```
python3 -m pip install -r requiremets.txt
```

## 3). installo docker
dipende a seconda del sistema operativo
```
https://www.docker.com/products/docker-desktop/
```

## 4). Attivo il DataBase
attivo il database mysql aperto sulla porta 3305 del localhost
```
docker run --name SimulazioneEsame \
    -d -e MYSQL_ROOT_PASSWORD=SimulazioneEsame \
    -e MYSQL_DATABASE=SimulazioneEsame \
    -p 3305:3306 mysql:latest
```

## 4). faccio il setup del database
quindi vado nella directory SetUpDB eseguo lo script query_db.py
```
cd SetUpDB
```
esecuzione
```
python3 query_db.py
```
torno alla main directory
```
cd ..
```


## 5). avvio l'applicazione con interfaccia web
```
python3 app.py
```

## 6). apro un browser e vedo il risultato
```
http://localhost:5000/
```

*P.S. per una visione del databe completa utilizzare il software beekeeper o quasiasi altro software desiderato per la visione dei database*
