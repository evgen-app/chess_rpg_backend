# chess_rpg_backend
Backend for chess rpg game

### installation
```shell
$ python3 manage.py makemigrations & python3 manage.py migrate
$ docker run -p 6379:6379 -d redis:5
```

### run
```shell
$ python3 manage.py runserver 0.0.0.0:8000  
```