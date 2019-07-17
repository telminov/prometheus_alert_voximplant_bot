# prometheus_alert_voximplant_bot
Сервис для оповещения голосом через voximplant по заданию prometheus alertmanager 

## Подготовка voximplant
1. Создаем учетку https://manage.voximplant.com/
2. Создаем приложение
3. Создаем сценарий (копируем из проекта vox_scenario.js)
4. Создаем роль. Прописываем ID роли в VOX_RULE_ID в settings.py 
5. Прописываем VOX_ACCOUNT_ID и VOX_API_KEY из  (https://manage.voximplant.com/settings/api_keys) в settings.py 
Статья по теме: https://voximplant.com/docs/references/articles/quickstart/apps-scenarios-rules-and-users

