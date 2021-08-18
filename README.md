[![codecov](https://codecov.io/gh/nkiryanov/foodgram-project-react/branch/master/graph/badge.svg?token=4JQKCSOYE8)](https://codecov.io/gh/nkiryanov/foodgram-project-react)
[![production backend build and deploy](https://github.com/nkiryanov/foodgram-project-react/actions/workflows/production_deploy.yaml/badge.svg)](https://github.com/nkiryanov/foodgram-project-react/actions/workflows/production_deploy.yaml)
# Продуктовый помощник. Скромный диплом курса python Я.Парктикум

## Адрес развернутого проекта: [foodgram.kiryanov.ru](https://foodgram.kiryanov.ru)

### Что можно сделать
- регистрироваться (пользователь доступен сразу после регистрации)
- чужие рецепты — смотреть, добавлять в избранное или в корзину покупок
- создавать и редактировать свои рецепты
- подписываться на другого автора
- загружать список ингредиентов для рецептов в корзине (PDF)
- есть админка, где администратор может создавать новые сущности: меры измерения, теги, ингредиенты, подписывать пользователей, добавлять в избранное и прочее

### Из чего состоит
Фронт: написан на react, подготовлен разработчиками курса. \
Задача бэка — написать API по подготовленной документации. Настроить CI/CD.

Для удобства добавил:
- генерацию тестовых данных
- management команды для заполнения тестовыми данными
- покрытие тестами
- интеграция с codecov
- pre-commit и хуки для него: проверка линтерами, генерация зависимостей
- вместо контейнера nginx используется [swag](https://docs.linuxserver.io/general/swag). Так безопаснее и сразу с HTTPS

## Технологии и требования
```
Python 3.9+
Django 3.2
Django REST Framework 3.12
Django Filters
Factory Boy
Poetry
Docker
Swag
```
## Структура проекта
```
├── README.md
├── backend
├── docs
├── frontend
└── infra
```

1. ├ backend : здесь бэк. Управление зависимостями - Poetry (об этом ниже)
2. ├ docs : файлы с изначальной документацией. Подключаются при деплое проекта
3. ├ frontend : фронт. Тут код проекта и уже сбилженный билд для добавления в контейнер
4. └ infra : файлы docker-compose для запуска в проде, для подготовки фронта

## Как развернуть проект на сервере

На сервере должен быть установлен Docker, docker-compose совместимых версий

1. Склонируйте папку проекта на сервер
    ```shell
    git clone git@github.com:nkiryanov/foodgram-project-react.git
    cd foodgram-project-react
    ```

2. Задайте переменные окружения. Какие именно переменные нужны и как их задавать в папке '**.envs example**' Обратите внимание, переменные нужно класть в папку **.envs** в папку **infra/production** \
    Секретный ключ удобно сгенерировать локально. Если перейти в папку backend и выполнить команду  ``make gen-secretkey``, то будет показан на экране.
    ```
    └── infra
        └── production
            ├── .envs
            │   ├── .django
            │   ├── .postgre
            ├── .envs\ example
            │   ├── .django
            │   ├── .postgre
            ├── docker-compose.yaml
            └── swag_nginx.conf
    ```


3. В github создайте **environment** назвав его "production_environment" и задайте ключи доступа к github и серверу
    - DOCKER_PASSWORD
    - DOCKER_USERNAME
    - HOST
    - SSH_KEY
    - USERNAME
    - SITE_URL - Адрес сайта, используется Swag для сертификта SSL
    - SSL_EMAIL - Swag настроен для ZeroSSL. Почта это логин в ZeroSSL

4. При следующем пуше в ветку "master", если тесты пройдены успешно проект будет выгружен на сервер и перезапущен
5. При первом запуске создать суперюзера:
    ```shell
    docker-compose exec django bash
    python manage.py createsuperuser
    ```
6. Если потребуется заполнение тестовыми данными, смотри ниже


## Как разрабатывать или вносить изменения в бэк

Зависимости управляются **poetry**. Детальное описание в [документации poetry](https://python-poetry.org/docs/cli/). Файлы **requirements** генерируются через pre-commit хуки. Редактировать вручную не требуется.

1. Склонируйте проект, перейдите в папку backend
    ```shell
    git clone git@github.com:nkiryanov/foodgram-project-react.git
    cd foodgram-project-react
    cd backend
    ```
2. Убедитесь что poetry установлен. Активируйте виртуальное окружение. Установите зависимости
    ```shell
    poetry shell
    poetry install
    ```
3. В IDE скорее всего потребуется указать путь до интерпретатора
    ```shell
    poetry env info --path
    ```
4. Установить pre-commit хуки
    ```shell
    pre-commit install --all
    ```
5. Локальные настройки не требуют переменных окружения. Если они потребуются:
    - раскоментируйте подключение **.env** в файле настроек **config.settings.local**
    - добавьте файл **.env** в корень папки **backend**
6. Локальные настройками предполагают БД postgres. Чтоб не устанавливать отдельное приложении используйте local.yaml для создания докер образа.
    ```
    docker-compose -f local.yaml up -d
    ```
7. Остановка, удаление и все остальные команды как с любым контейнером docker
    - Остановить контейнер с БД:
        ```shell
        docker-compose -f local.yaml down
        ```
    - Остановить контейнер с БД удалив данные:
        ```shell
        docker-compose -f local.yaml down --volumes
        ```

### Полезные команды:
- добавить пакет в список зависимостей для **Production**
    ```shell
    poetry add {название пакета}
    ```
- установить пакет в **окружение разработки** (dev):
    ```shell
    poetry add --dev {название пакета}
    ```
- обновить список зависимостей:
    ```shell
    poetry update
    ```
- выполнить pre-commit хуки локально:
    ```shell
    pre-commit install --all
    ```
- обновить версии репозиториев с pre-commit хуками:
    ```shell
    pre-commit autoupdate
    ```

## Как заполнить тестовыми данными.
Предполагается, что у вас уже установлено рабочее окружение и зависимости.

1. Заполнить фикстуры с ингредиентами
    ```python
    python manage.py loaddata data/ingredients_updated.json
    ```
2. Создать пользователей. Первой трете пользователей будут созданы подписки на друг друга
    ```python
    python manage.py fill_users 50
    ```
3. Создать рецепты, а также связанные объекты добавления в избранное или в корзину покупок (для 1/3 рецептов). Обратите внимание на ключ **realimages**. Он необязательный, но если указан картинки для рецептов будут загружаться из https://picsum.photos
    ```python
    python manage.py fill_recipes 120 --realimages
    ```

Для генерации тестовых данных используется **factory_boy**. Если это production сервере, то этого пакета нет в зависимостях, нужно установить:
```shell
docker-compose exec django bash
pip install factory_boy
```

## Запуск тестов
Тесты используют unittest, но удобно запускать и менеджерить через pytest

```shell
pytest
```
