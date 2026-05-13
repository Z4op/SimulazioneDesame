# Simulazione d'esame

## 1). creare un ambiente virtual in python3
--creo l'ambiente virtuale
```
python3 -m venv .env
```
--attivare l'ambiente virtuale
```

```

## 2).
```

```

## 3). 
```
docker run --name SimulazioneEsame \
    -d -e MYSQL_ROOT_PASSWORD=SimulazioneEsame \
    -e MYSQL_DATABASE=SimulazioneEsame \
    -p 3306:3306 mysql:latest
```
