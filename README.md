## Тестовое задание, Торубаров Игорь

Сборка
```
docker build -t <image-name> .
```

Запуск
```
docker run -p 127.0.0.1:8000:8000 --name <container-name> <image-name>
```

Unit-тесты
```
docker exec <container-name> python test.py
```

Использование
```
curl -X GET -H "Content-type: application/json" -d '{"date":"31.01.2021", "periods": 3, "rate": 6.0, "amount": 10000}' "127.0.0.1:8000"
```
