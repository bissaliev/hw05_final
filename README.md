# Yatube :globe_with_meridians:

## Описание проекта :arrow_double_down:

### Cоциальная сеть Yatube. Учебный проект

Сеть для публикации постов пользователями, с возможностью подписки на понравившихся авторов. Реализован такой функционал:

- :one: Просмотр всех публикаций неавторизованным пользователем
- :two: Добавление (с возможностью добавления изображений) и удаление публикаций только авторизированным пользователем
- :three: Редактирование публикаций только его автором
- :four: Создание групп для объединения публикаций по общей тематике только администратором
- :five: Просмотр публикаций по определенной группе
- :six: Возможность подписки на определенного автора только авторизованным пользователем и просмотр его ленты публикаций. Также можно отписаться от автора
- :seven: Возможность оставлять комментарии на публикацию только авторизованным пользователем

На  сайте подключены пагинация, кеширование, регистрация и авторизация пользователей. Также можно сменить пароль указав адрес электронной почты на который будет отправлено письмо. Также сайт поддерживает API. Аутентификация осуществляется по JWT-токену. Предоставляет данные в формате Json. Функциональные возможности на API такие же как указано выше. При запущенном проекте документация доступна [ЗДЕСЬ](http://localhost:8000/redoc/) :page_with_curl:.

### Технологии :wrench:

- Python 3.10
- Django 2.2.16
- Django RestFramework 3.12.4
- Djoser 2.1.0

### Как запустить проект: :balloon:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone git@github.com:bissaliev/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 manage.py migrate
```

Запустить проект:

```bash
python3 manage.py runserver
```

[Перейти на сайт](http://localhost:8000/) :rocket:

### Эндпоинты для API

Регистрация пользователя:
POST

```bash
http://127.0.0.1:8000/api/v1/users/
```

Формат ввода:

```json
{
    "username": "Ваш_юзернайм",
    "password": "Ваш_пароль"
}
```

Получить токен:
POST

```bash
http://127.0.0.1:8000/api/v1/token/login/
```

Формат ввода:

```json
{
"username": "string",
"password": "string"
}
```

Остальные эндпоинты описаны в документации:

```bash
http://localhost:8000/redoc/
```

### Автор

[Биссалиев Олег](https://github.com/bissaliev)
