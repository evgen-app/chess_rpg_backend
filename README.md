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

### Описание команд сокетов
```python
# подключиние к очереди(ws://room/)  
{
    "type": "connect",
    "deck_id": int
}

# коннект к комнате (сообщение от сервера)
{
    "type": "INFO",
    "opponent_score": int,
    "coordinates" : [(x: int, y: int, type: str, model_url: url, your: bool), ...],
    "opponent_online": true,
    "first": bool
}

# состояние оппонента в комнате(сообщение от сервера)
{
    "type": "INFO",
    "message": "opponent is online" / "opponent is offline"
}
```
