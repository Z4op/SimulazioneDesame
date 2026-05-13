





docker run --name SimulazioneEsame \
    -d -e MYSQL_ROOT_PASSWORD=SimulazioneEsame \
    -e MYSQL_DATABASE=SimulazioneEsame \
    -p 3306:3306 mysql:latest
