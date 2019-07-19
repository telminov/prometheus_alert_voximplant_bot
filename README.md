# prometheus_alert_voximplant_bot
Сервис для оповещения голосом через voximplant по заданию prometheus alertmanager 

## Подготовка voximplant
1. Создаем учетку https://manage.voximplant.com/
2. Создаем приложение
3. Создаем сценарий (копируем из проекта vox_scenario.js). Меняем в нем значение переменной caller_id 
на проверенный voximplant номер телефона (https://manage.voximplant.com/settings/caller_ids)
4. Создаем роль. Прописываем ID роли в VOX_RULE_ID в settings.py 
5. Прописываем VOX_ACCOUNT_ID и VOX_API_KEY из  (https://manage.voximplant.com/settings/api_keys) в settings.py 
Статья по теме: https://voximplant.com/docs/references/articles/quickstart/apps-scenarios-rules-and-users

## Настройка тестовой инсталяции Prometheus
Чтобы проверить что voximplant настроен правильно, и оповещение работает, можно поднять упращенную инсталяцию prometheus.

Меняем в prometheus_test/alert.rules параметр phones на разделенные запятыми номера телефонов, 
на которые хотим получить звонок.

Запускаем сервис
```bash
sudo docker build -t prometheus_alert_voximplant_bot .
sudo docker run --rm -ti \
        --name voximplant_bot \
        -v <project_path>/settings.py:/conf/settings.py \
        -p 8000:8000 \
        prometheus_alert_voximplant_bot
```

Запускаем alert manager
```bash
sudo mkdir -p /var/docker/prometheus_alertmanager/conf
sudo cp <project_path>/prometheus_test/alertmanager.yml /var/docker/prometheus_alertmanager/conf
sudo docker run --rm -ti \
        --name prometheus-alertmanager \
        -v /var/docker/prometheus_alertmanager/conf/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
        --link voximplant_bot:voximplant_bot \
        prom/alertmanager:v0.8.0 \
            -config.file=/etc/alertmanager/alertmanager.yml
```

Запускаем Prometheus
```bash
sudo mkdir -p /var/docker/prometheus/conf
sudo mkdir -p /var/docker/prometheus/data
sudo cp <project_path>/prometheus_test/prometheus.yml /var/docker/prometheus/conf
sudo cp <project_path>/prometheus_test/alert.rules /var/docker/prometheus/conf
sudo docker run --rm -ti \
        --name prometheus \
        -v /var/docker/prometheus/conf/prometheus.yml:/etc/prometheus/prometheus.yml \
        -v /var/docker/prometheus/conf/alert.rules:/etc/prometheus/alert.rules \
        -v /var/docker/prometheus/data:/data \
        -p 9090:9090 \
        --link voximplant_bot:voximplant_bot \
        --link prometheus-alertmanager:alertmanager \
        prom/prometheus:v1.7.1 \
            -storage.local.path='/data' -config.file=/etc/prometheus/prometheus.yml -alertmanager.url=http://alertmanager:9093
```

Проверяем:
 1. http://127.0.0.1:9090/status: в Alertmanagers должен появится endpoint http://alertmanager:9093/api/v1/alerts
 2. http://127.0.0.1:9090/targets: должен появится http://voximplant_bot:8000/metrics
 3. http://127.0.0.1:9090/alerts: должен сработать alert "ServiceDown"
 4. В консоле с сервисом должны увидеть вызов 
 ```
 ...
 alert
{'description': 'Упал тестовый сервис.', 'phones': '79991234567', 'summary': 'Тестовый сервим лежит'}
...
```