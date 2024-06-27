## Run dev

## Run tests

```properties
/lups/fast python -m unittest discover -s ./tests
```

[//]: # (### Frontend)

[//]: # (```console)

[//]: # (cd lups)

[//]: # (ng serve)

[//]: # (```)

[//]: # ()
[//]: # (### Database + Backend &#40;debug&#41;)

[//]: # (```console)

[//]: # (docker-compose -f docker-compose.dev.yaml up -d)

[//]: # (python flaskr\run_server.py)

[//]: # (```)

[//]: # (<details>)

[//]: # (<summary>Notes</summary>)

[//]: # (Celery can only be tested in docker else it can't connect to Flask)

[//]: # (</details>  )

[//]: # ()
[//]: # (### Database + Backend &#40;Prod&#41;)

[//]: # (```console)

[//]: # (docker-compose up -d)

[//]: # (```)

[//]: # ()
[//]: # (## Run Prod)

[//]: # ()
[//]: # (### SSH into server)

[//]: # (```console)

[//]: # (ssh user@ip -i pem_file)

[//]: # (ssh erik@52.174.181.107 -i C:\Users\erik\desktop\erikfinal.pem)

[//]: # (```)

[//]: # ()
[//]: # (### Stop service &#40;server&#41;)

[//]: # (```console)

[//]: # (sudo systemctl stop nginx)

[//]: # (cd /var/www)

[//]: # (docker compose down)

[//]: # (```)

[//]: # ()
[//]: # (### Build and transfer &#40;local machine&#41;)

[//]: # (```console)

[//]: # (cd lups)

[//]: # (ng build)

[//]: # (cd ..)

[//]: # (python transfer_all.py)

[//]: # (```)

[//]: # ()
[//]: # (### Start service &#40;server&#41;)

[//]: # (```console)

[//]: # (docker compose up -d)

[//]: # (sudo systemctl start nginx)

[//]: # (```)

[//]: # ()
[//]: # (### &#40;optional&#41; Build tables &#40;server&#41;)

[//]: # (```console)

[//]: # (docker ps)

[//]: # (```)

[//]: # (Flask's container name should be **www-flask-1**)

[//]: # (```console)

[//]: # (docker exec -it www-flask-1 bash)

[//]: # (flask --app run_server:create_app cli create_tables)

[//]: # (```)

[//]: # (<details>)

[//]: # (<summary>Notes</summary>)

[//]: # (This resets database and deletes all files)

[//]: # (</details>)

[//]: # ()
[//]: # (### &#40;optional&#41; Database access &#40;server&#41;)

[//]: # (```console)

[//]: # (docker exec -it www-mysql-1 mysql -u erik -p)

[//]: # (use erik_db;)

[//]: # (select * from users;)

[//]: # (```)