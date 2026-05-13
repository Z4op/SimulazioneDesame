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
```

## 4). Attivo il DataBase
```
docker run --name SimulazioneEsame \
    -d -e MYSQL_ROOT_PASSWORD=SimulazioneEsame \
    -e MYSQL_DATABASE=SimulazioneEsame \
    -p 3305:3306 mysql:latest
```

## 4). faccio il setup del database
quindi vado nella
```

```
