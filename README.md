## Run dev

### Frontend
```console
cd lups
ng serve
```

### Database + Backend (debug)
```console
docker-compose -f docker-compose.dev.yaml up -d
flask --app flaskr/run_server:create_app run --debug
```
<details>
<summary>Notes</summary>
Celery can only be tested in docker else it can't connect to Flask
</details>  

### Database + Backend (Prod)
```console
docker-compose up -d
```

## Run Prod

### SSH into server
```console
ssh user@ip -i pem_file
ssh erik@52.174.181.107 -i C:\Users\erik\desktop\erikfinal.pem
```

### Stop service (server)
```console
sudo systemctl stop nginx
cd /var/www
docker compose down
```

### Build and transfer (local machine)
```console
cd lups
ng build
cd ..
python transfer_all.py
```

### Start service (server)
```console
docker compose up -d
sudo systemctl start nginx
```

### (optional) Build tables (server)
```console
docker ps
```
Flask's container name should be **www-flask-1**
```console
docker exec -it www-flask-1 bash
flask --app run_server:create_app cli create_tables
```
<details>
<summary>Notes</summary>
This resets database and deletes all files
</details>

### (optional) Database access (server)
```console
docker exec -it www-mysql-1 mysql -u erik -p
use erik_db;
select * from users;
```