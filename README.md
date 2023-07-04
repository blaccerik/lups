1) stop service
```console
sudo systemctl stop nginx
```
2) build frontend
```console
ng build
```
3) transfer files
```console
python transfer_all.py
```
4) build docker  
!!!!!!!!! MAKE SURE THERE ISN'T ANYTHING COMMENTED OUT!!!!!!!!!!!!!!!!!!!!!!!
```console
docker compose up -d --build
```
5) (optional) go into docker container and build tables
```console
docker exec -it www-flask-1 bash
flask --app run_server:create_app cli create_tables
```
6) start service
```console
sudo systemctl start nginx
```

database access (if needed)
```console
docker exec -it www-mysql-1 mysql -u erik -p
use erik_db;
```