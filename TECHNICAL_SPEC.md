# Техническое задание: boostylib

## 1. Общие сведения

| Параметр | Значение |
|---|---|
| Название | `boostylib` |
| Язык | Python 3.14+ |
| Пакетный менеджер | uv |
| Тип | Асинхронная библиотека (async/await) |
| Лицензия | MIT |
| Целевая аудитория | Разработчики ботов, сервисов автоматизации, интеграций с Boosty.to |

## 2. Цель проекта

Создать production-ready Python-библиотеку для полноценной работы с неофициальным API Boosty.to. Библиотека должна покрывать:

- Аутентификацию и автоматическое обновление токенов
- Верификацию подписок и оплат
- Управление постами (CRUD) с гибкой настройкой уровней доступа
- Отслеживание донатов
- Систему авто-ответов на события (донаты, подписки, комментарии)
- Управление уровнями подписок, целями, витриной

## 3. Архитектурные принципы

### 3.1 Никакого хардкода

- **Все URL, таймауты, лимиты, retry-параметры** — через конфигурацию (`Settings`), не вшиты в код
- **Все модели данных** — Pydantic v2 с валидацией, без `dict`/`Any` там, где структура известна
- **Все строковые константы** (типы контента, статусы, уровни) — через `Enum`
- **Конфигурация** загружается каскадно: defaults → config file (TOML/JSON) → env vars → runtime override
- **Dependency Injection** — внешние зависимости (HTTP-клиент, логгер, хранилище токенов) инжектируются через протоколы/абстракции

### 3.2 Качество кода (уровень Senior)

- Строгая типизация: `mypy --strict`
- Форматирование: `ruff format`
- Линтинг: `ruff check`
- Тесты: `pytest` + `pytest-asyncio` + `respx` (мок HTTP)
- 80%+ покрытие тестами
- Документация: docstrings (Google style), MkDocs + mkdocstrings
- Semver, changelog

## 4. Стек технологий

| Назначение | Библиотека |
|---|---|
| HTTP-клиент | `httpx` (async) |
| Модели данных | `pydantic` v2 |
| Конфигурация | `pydantic-settings` |
| Тестирование | `pytest`, `pytest-asyncio`, `respx`, `pytest-cov` |
| Линтинг / форматирование | `ruff` |
| Типизация | `mypy` |
| Документация | `mkdocs-material`, `mkdocstrings` |
| Сборка | `uv`, `hatchling` |

## 5. Структура проекта

```
boostylib/
├── pyproject.toml
├── uv.lock
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── index.md
│   ├── quickstart.md
│   ├── configuration.md
│   └── api/
├── src/
│   └── boostylib/
│       ├── __init__.py              # Публичный API: BoostyClient, models, enums
│       ├── py.typed                  # PEP 561 marker
│       ├── client.py                # Главный клиент (фасад)
│       ├── config.py                # Settings (pydantic-settings)
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── manager.py           # AuthManager: хранение, refresh токенов
│       │   ├── storage.py           # Протокол + реализации хранения токенов
│       │   └── models.py            # AuthCredentials, TokenPair
│       ├── http/
│       │   ├── __init__.py
│       │   ├── transport.py         # HTTPTransport: обёртка над httpx
│       │   ├── retry.py             # RetryPolicy, экспоненциальный backoff
│       │   ├── rate_limiter.py      # RateLimiter (token bucket)
│       │   └── exceptions.py        # Иерархия HTTP-исключений
│       ├── api/
│       │   ├── __init__.py
│       │   ├── base.py              # BaseAPI — общая логика для endpoint-групп
│       │   ├── users.py             # UsersAPI: /user/current, /user/subscriptions
│       │   ├── blogs.py             # BlogsAPI: /blog/{username}
│       │   ├── posts.py             # PostsAPI: CRUD постов
│       │   ├── comments.py          # CommentsAPI: CRUD комментариев
│       │   ├── subscriptions.py     # SubscriptionsAPI: уровни, верификация
│       │   ├── donations.py         # DonationsAPI: отслеживание донатов
│       │   ├── targets.py           # TargetsAPI: цели (goals)
│       │   ├── showcase.py          # ShowcaseAPI: витрина
│       │   └── media.py             # MediaAPI: загрузка файлов, изображений, видео
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py              # User, UserProfile
│       │   ├── blog.py              # Blog, BlogInfo
│       │   ├── post.py              # Post, PostContent, ContentBlock, AccessLevel
│       │   ├── comment.py           # Comment, CommentThread
│       │   ├── subscription.py      # SubscriptionLevel, UserSubscription
│       │   ├── donation.py          # Donation, DonationEvent
│       │   ├── target.py            # Target (goal)
│       │   ├── showcase.py          # ShowcaseItem
│       │   ├── media.py             # MediaFile, SignedURL
│       │   └── pagination.py        # PaginatedResponse[T], Cursor
│       ├── enums.py                 # ContentType, SubscriptionTier, PostAccess, ...
│       ├── events/
│       │   ├── __init__.py
│       │   ├── poller.py            # EventPoller: polling-based event detection
│       │   ├── dispatcher.py        # EventDispatcher: routing событий к хэндлерам
│       │   ├── handlers.py          # Протокол EventHandler
│       │   └── models.py            # Event, EventType enum
│       ├── builders/
│       │   ├── __init__.py
│       │   └── post_builder.py      # PostBuilder: fluent API для создания постов
│       └── _compat.py               # Утилиты совместимости (если нужно)
└── tests/
    ├── conftest.py                  # Фикстуры: mock client, credentials
    ├── test_auth/
    ├── test_api/
    ├── test_events/
    ├── test_builders/
    └── fixtures/                    # JSON-фикстуры ответов API
        ├── post_response.json
        ├── subscription_levels.json
        └── ...
```

## 6. Модули — детальное описание

---

### 6.1 Конфигурация (`config.py`)

```python
from pydantic_settings import BaseSettings

class BoostySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BOOSTY_",
        toml_file="boosty.toml",
    )

    base_url: str = "https://api.boosty.to/v1"
    timeout: float = 30.0
    max_retries: int = 3
    retry_backoff_factor: float = 0.5
    rate_limit_requests: int = 60
    rate_limit_period: float = 60.0
    poll_interval: float = 30.0
    token_refresh_margin: int = 300  # секунд до истечения
```

Все параметры переопределяются через:
- `BOOSTY_BASE_URL`, `BOOSTY_TIMEOUT`, ... (env vars)
- файл `boosty.toml`
- аргументы конструктора `BoostyClient(settings=...)`

---

### 6.2 Аутентификация (`auth/`)

#### Протокол хранения токенов

```python
from typing import Protocol

class TokenStorage(Protocol):
    async def load(self) -> TokenPair | None: ...
    async def save(self, tokens: TokenPair) -> None: ...
    async def clear(self) -> None: ...
```

#### Встроенные реализации

| Класс | Описание |
|---|---|
| `FileTokenStorage` | Хранение в JSON-файле (по умолчанию `~/.boosty/auth.json`) |
| `MemoryTokenStorage` | In-memory, для тестов и одноразовых скриптов |
| `EnvTokenStorage` | Чтение из переменных окружения `BOOSTY_ACCESS_TOKEN`, `BOOSTY_REFRESH_TOKEN`, `BOOSTY_DEVICE_ID` |

#### AuthManager

- Автоматический refresh токена при 401 или за N секунд до истечения
- Thread-safe / asyncio-safe через `asyncio.Lock`
- Retry на refresh с экспоненциальным backoff
- Событие `on_token_refreshed` для подписки

---

### 6.3 HTTP-транспорт (`http/`)

#### HTTPTransport

- Обёртка над `httpx.AsyncClient`
- Автоматическая подстановка `Authorization: Bearer <token>` через middleware
- Retry с настраиваемой политикой (`RetryPolicy`)
- Rate limiting (token bucket)
- Логирование запросов/ответов (DEBUG-уровень)
- Корректный `async with` lifecycle

#### Иерархия исключений

```
BoostyError
├── BoostyAuthError          # 401, невалидный токен
├── BoostyForbiddenError     # 403, нет доступа
├── BoostyNotFoundError      # 404
├── BoostyRateLimitError     # 429
├── BoostyServerError        # 5xx
└── BoostyNetworkError       # Таймауты, DNS, connection errors
```

---

### 6.4 API-модули (`api/`)

Каждый модуль наследуется от `BaseAPI` и получает доступ к `HTTPTransport`.

#### 6.4.1 UsersAPI

| Метод | Описание |
|---|---|
| `get_current_user()` | Текущий авторизованный пользователь |
| `get_subscriptions(limit, with_follow)` | Подписки текущего пользователя |

#### 6.4.2 BlogsAPI

| Метод | Описание |
|---|---|
| `get_blog(username)` | Информация о блоге |
| `get_blacklist(blog_url)` | Чёрный список |

#### 6.4.3 PostsAPI — CRUD постов

| Метод | Описание |
|---|---|
| `list_posts(username, *, limit, offset, level_id, tags_ids, from_ts, to_ts)` | Список постов с фильтрацией |
| `get_post(username, post_id)` | Получить пост |
| `create_post(username, post: PostCreateRequest)` | Создать пост |
| `update_post(username, post_id, post: PostUpdateRequest)` | Обновить пост |
| `delete_post(username, post_id)` | Удалить пост |
| `get_deferred_access(username, post_id)` | Настройки отложенного доступа |
| `set_deferred_access(username, post_id, config)` | Установить отложенный доступ |

#### 6.4.4 PostBuilder — Fluent API для создания постов

```python
post = (
    PostBuilder()
    .title("Эксклюзивный контент")
    .text("Привет, подписчики!")
    .image(file_path="/path/to/img.png")
    .video(url="https://...")
    .audio(file_path="/path/to/track.mp3")
    .file(file_path="/path/to/archive.zip")
    .link(url="https://example.com", title="Ссылка")
    .access_level(level_id="abc123")           # Доступ по уровню подписки
    .minimum_donation(amount=500, currency="RUB")  # Доступ за донат
    .free()                                     # Бесплатный пост
    .teaser("Этот контент доступен подписчикам...")  # Превью для не-подписчиков
    .tags(["gamedev", "devlog"])
    .scheduled_at(datetime(2026, 4, 1, 12, 0))  # Отложенная публикация
    .build()
)

await client.posts.create_post("my_blog", post)
```

**Уровни доступа поста:**

| Метод | Описание |
|---|---|
| `.free()` | Бесплатный для всех |
| `.access_level(level_id=...)` | Доступен подписчикам указанного уровня и выше |
| `.minimum_donation(amount, currency)` | Доступен за единоразовый донат |
| `.subscribers_only()` | Любым подписчикам |

#### 6.4.5 SubscriptionsAPI

| Метод | Описание |
|---|---|
| `get_levels(username, *, show_free)` | Список уровней подписки блога |
| `verify_subscription(username, user_id) → SubscriptionStatus` | Проверить подписку конкретного пользователя |
| `get_subscribers(username, *, level_id, limit, offset)` | Список подписчиков с фильтрацией по уровню |

**`SubscriptionStatus`** — модель результата верификации:

```python
class SubscriptionStatus(BaseModel):
    is_subscribed: bool
    level: SubscriptionLevel | None
    expires_at: datetime | None
    is_paid: bool
    price: int | None
    currency: str | None
```

#### 6.4.6 DonationsAPI

| Метод | Описание |
|---|---|
| `get_donations(username, *, limit, offset, from_ts, to_ts)` | Список донатов с фильтрацией по дате |
| `get_donation(username, donation_id)` | Детали доната |

#### 6.4.7 CommentsAPI

| Метод | Описание |
|---|---|
| `get_comments(username, post_id, *, limit, offset, order)` | Комментарии к посту |
| `create_comment(username, post_id, text, *, reply_to)` | Создать комментарий/ответ |

#### 6.4.8 TargetsAPI

| Метод | Описание |
|---|---|
| `get_targets(username)` | Цели блога |
| `create_target(username, description, target_sum, target_type)` | Создать цель |
| `update_target(target_id, ...)` | Обновить цель |
| `delete_target(target_id)` | Удалить цель |

#### 6.4.9 ShowcaseAPI

| Метод | Описание |
|---|---|
| `get_showcase(username)` | Элементы витрины |
| `set_showcase_status(username, status)` | Переключить видимость |

#### 6.4.10 MediaAPI — загрузка и отправка файлов

| Метод | Описание |
|---|---|
| `upload_image(file: Path \| BinaryIO, *, content_type)` | Загрузить изображение, получить URL |
| `upload_file(file: Path \| BinaryIO, *, filename)` | Загрузить файл (архив, документ и т.д.) |
| `upload_video(file: Path \| BinaryIO)` | Загрузить видео |
| `upload_audio(file: Path \| BinaryIO)` | Загрузить аудио |
| `get_signed_url(media_id)` | Получить подписанный URL для скачивания |

**Как это работает:**

Boosty использует двухэтапную загрузку:
1. Загружаем файл через `MediaAPI.upload_*()` → получаем `MediaFile` с `media_id` и `url`
2. Ссылаемся на `media_id` в контент-блоке поста или комментария

**Пример: создание поста с файлом-архивом**

```python
async with BoostyClient(credentials=creds) as client:
    # Загружаем файл
    media = await client.media.upload_file(
        Path("./project_source.zip"),
        filename="project_source.zip",
    )

    # Создаём пост с файлом, доступный только Premium
    post = (
        PostBuilder()
        .title("Исходники проекта")
        .text("Скачивайте архив с полными исходниками:")
        .file(media_id=media.id, filename=media.filename, size=media.size)
        .access_level(level_id=premium_level.id)
        .build()
    )
    await client.posts.create_post("my_blog", post)
```

**Пример: ответ файлом через пост по событию доната**

```python
@client.on(EventType.NEW_DONATION)
async def send_archive_on_donation(event: DonationEvent):
    if event.amount >= 1000:
        media = await client.media.upload_file(
            Path("./bonus_pack.zip"),
            filename="bonus_pack.zip",
        )
        post = (
            PostBuilder()
            .title(f"Бонус для {event.user.name}")
            .text("Спасибо за щедрый донат! Вот ваш бонусный архив:")
            .file(media_id=media.id, filename=media.filename, size=media.size)
            .minimum_donation(amount=1000, currency="RUB")
            .build()
        )
        await client.posts.create_post("my_blog", post)
```

**Модель MediaFile:**

```python
class MediaFile(BaseModel):
    id: str
    url: str
    signed_url: str | None
    filename: str | None
    size: int | None          # в байтах
    content_type: str | None  # MIME-type
    width: int | None         # для изображений/видео
    height: int | None        # для изображений/видео
    duration: float | None    # для аудио/видео, секунды
```

**PostBuilder поддерживает файлы двумя способами:**

```python
# Способ 1: через media_id (файл уже загружен)
.file(media_id="abc123", filename="data.zip", size=1024000)

# Способ 2: через file_path (автозагрузка — PostBuilder вызовет MediaAPI)
.file(file_path=Path("./data.zip"))
```

> **Примечание:** Комментарии Boosty API поддерживают текстовые блоки.
> Для отправки файлов в ответ пользователю — создавайте пост с ограниченным доступом
> (по уровню подписки или минимальному донату) и дайте ссылку на него в комментарии.

---

### 6.5 Система событий (`events/`)

Поскольку Boosty **не предоставляет вебхуки**, реализуем polling + event dispatch.

#### EventPoller

- Периодический опрос endpoint'ов (интервал настраивается через `BoostySettings.poll_interval`)
- Детектирует новые события путём сравнения с предыдущим состоянием
- Использует `asyncio.Task` для фоновой работы

#### EventDispatcher — декораторный API

```python
from boostylib import BoostyClient, EventType

client = BoostyClient(...)

@client.on(EventType.NEW_DONATION)
async def handle_donation(event: DonationEvent):
    if event.amount >= 1000:
        await client.comments.create_comment(
            event.blog_username, event.post_id,
            f"Спасибо за донат {event.amount} {event.currency}!"
        )

@client.on(EventType.NEW_SUBSCRIPTION)
async def handle_subscription(event: SubscriptionEvent):
    await client.comments.create_comment(
        event.blog_username, event.welcome_post_id,
        f"Добро пожаловать, {event.user.name}!"
    )

@client.on(EventType.SUBSCRIPTION_RENEWED)
async def handle_renewal(event: SubscriptionEvent):
    ...

@client.on(EventType.NEW_COMMENT)
async def handle_comment(event: CommentEvent):
    ...

# Запуск polling
async with client:
    await client.start_polling()
```

#### Типы событий (`EventType`)

| Событие | Описание |
|---|---|
| `NEW_DONATION` | Новый донат |
| `NEW_SUBSCRIPTION` | Новая подписка |
| `SUBSCRIPTION_RENEWED` | Продление подписки |
| `SUBSCRIPTION_CANCELLED` | Отмена подписки |
| `SUBSCRIPTION_LEVEL_CHANGED` | Смена уровня подписки |
| `NEW_COMMENT` | Новый комментарий |
| `NEW_POST` | Новый пост в блоге |

---

### 6.6 Модели данных (`models/`)

Все модели — Pydantic v2 `BaseModel` с:
- `model_config = ConfigDict(frozen=True)` для иммутабельности
- `alias_generator` для маппинга camelCase → snake_case из API
- Валидация типов и бизнес-правил
- Сериализация/десериализация JSON

#### Ключевые модели

```python
class Post(BaseModel):
    id: str
    title: str
    content: list[ContentBlock]
    created_at: datetime
    updated_at: datetime | None
    access_level: AccessLevel
    tags: list[str]
    comments_count: int
    is_published: bool

class ContentBlock(BaseModel):
    type: ContentType  # TEXT, IMAGE, VIDEO, AUDIO, FILE, LINK, LIST
    content: str | None
    url: str | None
    signed_url: str | None
    modifications: dict[str, Any] | None  # форматирование текста

class AccessLevel(BaseModel):
    level_id: str | None
    name: str
    price: int
    currency: str
    is_free: bool

class Donation(BaseModel):
    id: str
    user: User
    amount: int
    currency: str
    message: str | None
    created_at: datetime

class PaginatedResponse[T](BaseModel):  # Python 3.12+ generic syntax
    data: list[T]
    cursor: str | None
    is_last: bool
    total: int | None
```

---

### 6.7 Главный клиент (`client.py`)

Фасад, объединяющий все модули:

```python
class BoostyClient:
    def __init__(
        self,
        *,
        # Аутентификация — один из вариантов:
        access_token: str | None = None,
        credentials: AuthCredentials | None = None,
        token_storage: TokenStorage | None = None,

        # Конфигурация:
        settings: BoostySettings | None = None,

        # Опционально:
        http_client: httpx.AsyncClient | None = None,
    ): ...

    # API-модули как свойства
    users: UsersAPI
    blogs: BlogsAPI
    posts: PostsAPI
    comments: CommentsAPI
    subscriptions: SubscriptionsAPI
    donations: DonationsAPI
    targets: TargetsAPI
    showcase: ShowcaseAPI

    # Events
    def on(self, event_type: EventType) -> Callable: ...
    async def start_polling(self) -> None: ...
    async def stop_polling(self) -> None: ...

    # Lifecycle
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *args) -> None: ...
    async def close(self) -> None: ...
```

---

## 7. Сценарии использования

### 7.1 Верификация подписки

```python
async with BoostyClient(access_token="...") as client:
    status = await client.subscriptions.verify_subscription("my_blog", user_id="12345")

    if status.is_subscribed and status.is_paid:
        print(f"Подписан: уровень {status.level.name}, до {status.expires_at}")
    else:
        print("Подписка не активна")
```

### 7.2 Создание поста для определённого уровня подписки

```python
async with BoostyClient(credentials=creds) as client:
    levels = await client.subscriptions.get_levels("my_blog")
    premium = next(l for l in levels if l.name == "Premium")

    post = (
        PostBuilder()
        .title("Только для Premium")
        .text("Секретный контент...")
        .image(file_path="./secret.png")
        .access_level(level_id=premium.id)
        .teaser("Доступно подписчикам Premium и выше")
        .build()
    )

    created = await client.posts.create_post("my_blog", post)
    print(f"Пост создан: {created.id}")
```

### 7.3 Пост за донат

```python
post = (
    PostBuilder()
    .title("Эксклюзив за донат")
    .text("Этот контент доступен тем, кто задонатил 500₽+")
    .minimum_donation(amount=500, currency="RUB")
    .build()
)
```

### 7.4 Авто-ответ на донаты

```python
client = BoostyClient(credentials=creds)

@client.on(EventType.NEW_DONATION)
async def on_donation(event: DonationEvent):
    messages = {
        range(100, 500): "Спасибо за поддержку! ❤️",
        range(500, 1000): "Щедрый донат! Огромное спасибо!",
        range(1000, 100_000): "ВАУ! Ты легенда! 🎉",
    }
    for amount_range, msg in messages.items():
        if event.amount in amount_range:
            await client.comments.create_comment(
                event.blog_username, event.post_id, msg
            )
            break

@client.on(EventType.NEW_SUBSCRIPTION)
async def on_subscribe(event: SubscriptionEvent):
    await client.comments.create_comment(
        event.blog_username, event.welcome_post_id,
        f"Добро пожаловать на уровень {event.level.name}, {event.user.name}!"
    )

async with client:
    await client.start_polling()
```

### 7.5 Интеграция с Telegram-ботом

```python
from aiogram import Bot, Router
from boostylib import BoostyClient

router = Router()
boosty = BoostyClient(credentials=creds)

@router.message(Command("check"))
async def check_subscription(message: Message):
    # Маппинг telegram_id → boosty_user_id через вашу БД
    boosty_user_id = await db.get_boosty_id(message.from_user.id)
    status = await boosty.subscriptions.verify_subscription("my_blog", boosty_user_id)

    if status.is_subscribed:
        await message.answer(f"Подписка активна: {status.level.name}")
    else:
        await message.answer("Подписка не найдена. Оформите на boosty.to/my_blog")
```

---

## 8. Пагинация

Все методы, возвращающие списки, поддерживают два режима:

### Ручная пагинация

```python
page = await client.posts.list_posts("blog", limit=10)
while not page.is_last:
    for post in page.data:
        process(post)
    page = await client.posts.list_posts("blog", limit=10, offset=page.cursor)
```

### Async-итератор

```python
async for post in client.posts.iter_posts("blog", limit=10):
    process(post)
```

Реализовано через `AsyncIterator` с ленивой подгрузкой следующей страницы.

---

## 9. Обработка ошибок

```python
from boostylib.http.exceptions import BoostyAuthError, BoostyRateLimitError

try:
    post = await client.posts.get_post("blog", "123")
except BoostyAuthError:
    # Токен невалиден и refresh не помог
    await re_authenticate()
except BoostyRateLimitError as e:
    # Автоматический retry уже исчерпан
    print(f"Rate limit, retry after {e.retry_after}s")
except BoostyError as e:
    print(f"Ошибка Boosty API: {e}")
```

---

## 10. Тестирование

### 10.1 Стратегия

Три уровня тестов, каждый уровень запускается отдельным pytest-маркером:

| Уровень | Маркер | Что тестируем | Инструменты |
|---|---|---|---|
| Unit | `@pytest.mark.unit` | Модели, билдеры, retry, rate limiter, config parsing | `pytest`, `pytest-asyncio` |
| Integration (мок) | `@pytest.mark.integration` | API-модули с мокнутым HTTP, полный цикл auth | `respx`, `pytest-asyncio` |
| E2E (live) | `@pytest.mark.e2e` | Реальные запросы к Boosty API | `pytest`, env credentials |

### 10.2 Структура тестов

```
tests/
├── conftest.py                      # Общие фикстуры, настройка маркеров
├── factories.py                     # Фабрики моделей для генерации тестовых данных
├── fixtures/                        # JSON-снапшоты реальных ответов API
│   ├── user_current.json
│   ├── blog_info.json
│   ├── post_single.json
│   ├── post_list.json
│   ├── subscription_levels.json
│   ├── donation_list.json
│   ├── comments.json
│   └── error_responses/
│       ├── 401_unauthorized.json
│       ├── 403_forbidden.json
│       ├── 404_not_found.json
│       └── 429_rate_limit.json
├── unit/
│   ├── test_config.py               # Загрузка из env, toml, override, defaults
│   ├── test_models/
│   │   ├── test_post.py             # Парсинг, валидация, сериализация Post
│   │   ├── test_subscription.py     # SubscriptionLevel, SubscriptionStatus
│   │   ├── test_donation.py         # Donation model
│   │   ├── test_content_block.py    # ContentBlock, ContentType enum
│   │   └── test_pagination.py       # PaginatedResponse, cursor parsing
│   ├── test_builders/
│   │   ├── test_post_builder.py     # Все варианты: free, level, donation, scheduled
│   │   └── test_post_builder_validation.py  # Ошибки: пустой title, невалидный level
│   ├── test_auth/
│   │   ├── test_token_storage.py    # FileTokenStorage, MemoryTokenStorage, EnvTokenStorage
│   │   └── test_auth_manager.py     # Refresh логика, expiry detection, lock
│   ├── test_http/
│   │   ├── test_retry.py            # RetryPolicy: backoff, max retries, retryable statuses
│   │   └── test_rate_limiter.py     # Token bucket: burst, refill, wait
│   └── test_events/
│       ├── test_dispatcher.py       # Регистрация хэндлеров, dispatch по типу
│       └── test_poller.py           # Детекция новых событий, дедупликация
├── integration/
│   ├── conftest.py                  # mock_transport фикстура с respx
│   ├── test_users_api.py            # GET /user/current, /user/subscriptions
│   ├── test_blogs_api.py            # GET /blog/{username}
│   ├── test_posts_api.py            # CRUD: list, get, create, update, delete
│   ├── test_subscriptions_api.py    # get_levels, verify_subscription
│   ├── test_donations_api.py        # get_donations с фильтрацией
│   ├── test_comments_api.py         # get_comments, create_comment
│   ├── test_targets_api.py          # CRUD targets
│   ├── test_auth_flow.py            # Полный цикл: token expired → refresh → retry request
│   ├── test_pagination.py           # Автопагинация через async iterator
│   └── test_error_handling.py       # 401 → BoostyAuthError, 429 → retry → BoostyRateLimitError
└── e2e/
    ├── conftest.py                  # Реальные credentials из env, skip если нет
    ├── test_smoke.py                # get_current_user, get_blog — базовая связность
    └── test_post_lifecycle.py       # create → get → update → delete поста
```

### 10.3 Ключевые фикстуры (`conftest.py`)

```python
import pytest
from boostylib import BoostyClient, BoostySettings
from boostylib.auth import MemoryTokenStorage, TokenPair

@pytest.fixture
def settings() -> BoostySettings:
    return BoostySettings(
        base_url="https://api.boosty.to/v1",
        timeout=5.0,
        max_retries=1,
        rate_limit_requests=1000,
    )

@pytest.fixture
def token_pair() -> TokenPair:
    return TokenPair(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        device_id="test-device-id",
        expires_at=9999999999,
    )

@pytest.fixture
def memory_storage(token_pair: TokenPair) -> MemoryTokenStorage:
    storage = MemoryTokenStorage()
    storage._tokens = token_pair
    return storage

@pytest.fixture
async def client(settings, memory_storage) -> AsyncIterator[BoostyClient]:
    async with BoostyClient(
        token_storage=memory_storage,
        settings=settings,
    ) as c:
        yield c
```

### 10.4 Пример: unit-тест PostBuilder

```python
import pytest
from boostylib.builders import PostBuilder
from boostylib.enums import ContentType

class TestPostBuilder:
    def test_free_post(self):
        post = (
            PostBuilder()
            .title("Test")
            .text("Hello world")
            .free()
            .build()
        )
        assert post.title == "Test"
        assert post.access_level.is_free is True
        assert len(post.content) == 1
        assert post.content[0].type == ContentType.TEXT

    def test_post_with_subscription_level(self):
        post = (
            PostBuilder()
            .title("Premium only")
            .text("Secret")
            .access_level(level_id="level_123")
            .build()
        )
        assert post.access_level.level_id == "level_123"
        assert post.access_level.is_free is False

    def test_post_with_minimum_donation(self):
        post = (
            PostBuilder()
            .title("Donation post")
            .text("Content")
            .minimum_donation(amount=500, currency="RUB")
            .build()
        )
        assert post.access_level.price == 500
        assert post.access_level.currency == "RUB"

    def test_builder_requires_title(self):
        with pytest.raises(ValueError, match="title"):
            PostBuilder().text("No title").build()

    def test_builder_requires_content(self):
        with pytest.raises(ValueError, match="content"):
            PostBuilder().title("No content").build()

    def test_multiple_content_blocks(self):
        post = (
            PostBuilder()
            .title("Multi")
            .text("Intro")
            .image(file_path="/path/to/img.png")
            .text("Outro")
            .free()
            .build()
        )
        assert len(post.content) == 3
        assert post.content[0].type == ContentType.TEXT
        assert post.content[1].type == ContentType.IMAGE
        assert post.content[2].type == ContentType.TEXT

    def test_scheduled_post(self):
        from datetime import datetime, timezone
        dt = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)
        post = (
            PostBuilder()
            .title("Scheduled")
            .text("Later")
            .free()
            .scheduled_at(dt)
            .build()
        )
        assert post.scheduled_at == dt
```

### 10.5 Пример: integration-тест с respx

```python
import httpx
import respx
import pytest
from boostylib import BoostyClient

@pytest.mark.integration
class TestPostsAPI:
    @respx.mock
    async def test_list_posts(self, client: BoostyClient):
        respx.get("https://api.boosty.to/v1/blog/testblog/post/").mock(
            return_value=httpx.Response(200, json={
                "data": [
                    {
                        "id": "post_1",
                        "title": "First post",
                        "createdAt": 1710000000,
                        "content": [{"type": "text", "content": "Hello"}],
                        "accessLevel": {"levelId": None, "name": "Free", "price": 0, "isFree": True},
                        "tags": [],
                        "commentsCount": 0,
                        "isPublished": True,
                    }
                ],
                "extra": {"offset": None, "isLast": True},
            })
        )

        result = await client.posts.list_posts("testblog", limit=10)
        assert len(result.data) == 1
        assert result.data[0].id == "post_1"
        assert result.data[0].title == "First post"
        assert result.is_last is True

    @respx.mock
    async def test_create_post(self, client: BoostyClient):
        respx.post("https://api.boosty.to/v1/blog/testblog/post/").mock(
            return_value=httpx.Response(201, json={
                "id": "new_post_1",
                "title": "Created post",
                "createdAt": 1710000000,
                "content": [{"type": "text", "content": "Body"}],
                "accessLevel": {"levelId": "lvl_1", "name": "Premium", "price": 500, "isFree": False},
                "tags": ["test"],
                "commentsCount": 0,
                "isPublished": True,
            })
        )

        from boostylib.builders import PostBuilder
        post = PostBuilder().title("Created post").text("Body").access_level(level_id="lvl_1").tags(["test"]).build()
        created = await client.posts.create_post("testblog", post)
        assert created.id == "new_post_1"
        assert created.access_level.level_id == "lvl_1"

    @respx.mock
    async def test_auth_refresh_on_401(self, client: BoostyClient):
        """Первый запрос — 401, refresh токена, повторный запрос — 200."""
        call_count = 0

        def side_effect(request):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(401, json={"error": "unauthorized"})
            return httpx.Response(200, json={"data": [], "extra": {"isLast": True}})

        respx.get("https://api.boosty.to/v1/blog/testblog/post/").mock(side_effect=side_effect)
        respx.post("https://api.boosty.to/v1/oauth/token/").mock(
            return_value=httpx.Response(200, json={
                "access_token": "new_token",
                "refresh_token": "new_refresh",
                "expires_at": 9999999999,
            })
        )

        result = await client.posts.list_posts("testblog")
        assert call_count == 2  # 401 → refresh → retry → 200

    @respx.mock
    async def test_rate_limit_error(self, client: BoostyClient):
        respx.get("https://api.boosty.to/v1/blog/testblog/post/").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "30"})
        )

        from boostylib.http.exceptions import BoostyRateLimitError
        with pytest.raises(BoostyRateLimitError) as exc_info:
            await client.posts.list_posts("testblog")
        assert exc_info.value.retry_after == 30
```

### 10.6 Пример: E2E-тест

```python
import os
import pytest
from boostylib import BoostyClient
from boostylib.auth import EnvTokenStorage

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.getenv("BOOSTY_ACCESS_TOKEN"),
        reason="BOOSTY_ACCESS_TOKEN not set",
    ),
]

class TestSmoke:
    async def test_get_current_user(self):
        async with BoostyClient(token_storage=EnvTokenStorage()) as client:
            user = await client.users.get_current_user()
            assert user.id is not None
            assert user.name is not None

    async def test_get_blog(self):
        blog_username = os.environ["BOOSTY_TEST_BLOG"]
        async with BoostyClient(token_storage=EnvTokenStorage()) as client:
            blog = await client.blogs.get_blog(blog_username)
            assert blog.owner is not None
```

### 10.7 Конфигурация pytest

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests (models, builders, pure logic)",
    "integration: Integration tests with mocked HTTP",
    "e2e: End-to-end tests against real Boosty API",
]
filterwarnings = ["error"]
addopts = "-v --tb=short --strict-markers"

# Запуск по уровням:
# uv run pytest -m unit
# uv run pytest -m integration
# uv run pytest -m "unit or integration"
# uv run pytest -m e2e  (требует env vars)
```

### 10.8 Покрытие

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src/boostylib"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@overload",
]
```

---

## 11. Сборка и публикация на PyPI

### 11.1 Конфигурация пакета (`pyproject.toml`)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "boostylib"
version = "0.1.0"
description = "Async Python library for Boosty.to API"
readme = "README.md"
license = "MIT"
requires-python = ">=3.14"
authors = [
    { name = "Your Name", email = "you@example.com" },
]
keywords = ["boosty", "api", "async", "donations", "subscriptions"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Framework :: AsyncIO",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Typing :: Typed",
]

dependencies = [
    "httpx>=0.27",
    "pydantic>=2.7",
    "pydantic-settings>=2.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "respx>=0.22",
    "ruff>=0.5",
    "mypy>=1.11",
]
docs = [
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.25",
]

[project.urls]
Homepage = "https://github.com/yourname/boostylib"
Documentation = "https://yourname.github.io/boostylib"
Repository = "https://github.com/yourname/boostylib"
Issues = "https://github.com/yourname/boostylib/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/boostylib"]
```

### 11.2 Команды сборки и публикации

```bash
# Установка зависимостей для разработки
uv sync --extra dev

# Линтинг и типизация
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

# Тесты
uv run pytest -m "unit or integration" --cov
uv run pytest -m e2e  # опционально, с реальными credentials

# Сборка sdist + wheel
uv build
# → dist/boostylib-0.1.0.tar.gz
# → dist/boostylib-0.1.0-py3-none-any.whl

# Публикация на TestPyPI (проверка)
uv publish --index-url https://test.pypi.org/simple/

# Публикация на PyPI (продакшен)
uv publish
```

### 11.3 GitHub Actions CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - run: uv sync --extra dev
      - run: uv run ruff check src/ tests/
      - run: uv run ruff format --check src/ tests/
      - run: uv run mypy src/

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.14"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
          python-version: ${{ matrix.python-version }}
      - run: uv sync --extra dev
      - run: uv run pytest -m "unit or integration" --cov --cov-report=xml
      - uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  publish:
    needs: [lint, test]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    permissions:
      id-token: write  # trusted publisher (PyPI)
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - run: uv build
      - run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
```

### 11.4 Релизный процесс

```bash
# 1. Обновить версию в pyproject.toml
# 2. Обновить CHANGELOG.md
# 3. Коммит и тег
git add pyproject.toml CHANGELOG.md
git commit -m "release: v0.2.0"
git tag v0.2.0
git push origin main --tags
# → CI автоматически соберёт и опубликует на PyPI

# Установка пользователем:
pip install boostylib
# или
uv add boostylib
```

### 11.5 Версионирование

Используем [Semantic Versioning](https://semver.org/):

| Фаза | Версия | Значение |
|---|---|---|
| Alpha | `0.1.x` | Ядро + базовые API (breaking changes возможны) |
| Beta | `0.x.0` | Все модули, API стабилизируется |
| Stable | `1.0.0` | Публичный API зафиксирован, breaking changes = major bump |

---

## 12. Дорожная карта реализации

> См. актуальную версию в **разделе 24**.

---

## 13. README

Файл `README.md` в корне проекта. Он же отображается на PyPI и GitHub.

### Структура README

```markdown
# boostylib

Async Python library for Boosty.to API.

[![PyPI](https://img.shields.io/pypi/v/boostylib)](https://pypi.org/project/boostylib/)
[![Python](https://img.shields.io/pypi/pyversions/boostylib)](https://pypi.org/project/boostylib/)
[![Tests](https://img.shields.io/github/actions/workflow/status/yourname/boostylib/ci.yml)](...)
[![Coverage](https://img.shields.io/codecov/c/github/yourname/boostylib)](...)
[![License](https://img.shields.io/pypi/l/boostylib)](LICENSE)

---

## Features

- Полностью асинхронный (async/await)
- Автоматическое обновление токенов
- Pydantic v2 модели с валидацией
- Создание постов с контролем доступа (уровни подписки, донаты)
- Верификация подписок
- Система событий с декораторным API (`@client.on(...)`)
- Отслеживание донатов
- Управление целями, витриной, комментариями
- Typed — PEP 561, mypy strict

## Installation

pip install boostylib
# или
uv add boostylib

## Quick Start

### Получение токенов

1. Войдите на boosty.to
2. Откройте DevTools (F12) → Application → Local Storage
3. Скопируйте `auth` (access_token, refresh_token) и `_clentId` (device_id)

### Пример: проверка подписки

    from boostylib import BoostyClient

    async with BoostyClient(access_token="...") as client:
        status = await client.subscriptions.verify_subscription("blog", "user_id")
        print(status.is_subscribed, status.level.name)

### Пример: создание поста для Premium-подписчиков

    from boostylib import BoostyClient
    from boostylib.builders import PostBuilder

    async with BoostyClient(credentials=creds) as client:
        post = (
            PostBuilder()
            .title("Только для Premium")
            .text("Секретный контент")
            .access_level(level_id="...")
            .build()
        )
        await client.posts.create_post("my_blog", post)

### Пример: авто-ответ на донаты

    from boostylib import BoostyClient, EventType

    client = BoostyClient(credentials=creds)

    @client.on(EventType.NEW_DONATION)
    async def on_donation(event):
        await client.comments.create_comment(
            event.blog_username, event.post_id,
            f"Спасибо за {event.amount} {event.currency}!"
        )

    async with client:
        await client.start_polling()

## Configuration

Через переменные окружения:

    export BOOSTY_ACCESS_TOKEN=...
    export BOOSTY_REFRESH_TOKEN=...
    export BOOSTY_DEVICE_ID=...
    export BOOSTY_TIMEOUT=30
    export BOOSTY_POLL_INTERVAL=60

Или через файл `boosty.toml`:

    [boosty]
    timeout = 30.0
    max_retries = 3
    poll_interval = 60.0

Или программно:

    from boostylib import BoostyClient, BoostySettings

    settings = BoostySettings(timeout=10.0, max_retries=5)
    client = BoostyClient(settings=settings, access_token="...")

## Documentation

Полная документация: https://yourname.github.io/boostylib

## License

MIT
```

---

## 14. Документация (MkDocs)

### 14.1 Стек

| Инструмент | Назначение |
|---|---|
| `mkdocs-material` | Тема и движок |
| `mkdocstrings[python]` | Авто-генерация API reference из docstrings |
| `mkdocs-gen-files` | Автоматическая генерация страниц API |
| `mkdocs-literate-nav` | Навигация из markdown |

### 14.2 Конфигурация (`mkdocs.yml`)

```yaml
site_name: boostylib
site_description: Async Python library for Boosty.to API
repo_url: https://github.com/yourname/boostylib
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: deep-orange
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: deep-orange
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - content.code.copy
    - content.tabs.link
    - navigation.sections
    - navigation.expand
    - search.highlight

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true
            members_order: source
            docstring_style: google

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Authentication: getting-started/authentication.md
    - Quick Start: getting-started/quickstart.md
  - User Guide:
    - Configuration: guide/configuration.md
    - Working with Posts: guide/posts.md
    - Subscription Verification: guide/subscriptions.md
    - Donation Tracking: guide/donations.md
    - Event System: guide/events.md
    - Pagination: guide/pagination.md
    - Error Handling: guide/errors.md
  - API Reference:
    - Client: api/client.md
    - Models: api/models.md
    - Builders: api/builders.md
    - Events: api/events.md
    - Exceptions: api/exceptions.md
    - Config: api/config.md
  - Examples:
    - Telegram Bot: examples/telegram-bot.md
    - Discord Bot: examples/discord-bot.md
    - Auto-Responder: examples/auto-responder.md
  - Contributing: contributing.md
  - Changelog: changelog.md

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - admonition
  - pymdownx.details
```

### 14.3 Структура `docs/`

```
docs/
├── index.md                           # Обзор библиотеки, badges, ссылки
├── getting-started/
│   ├── installation.md                # pip/uv install, системные требования
│   ├── authentication.md             # Получение токенов, виды хранилищ
│   └── quickstart.md                  # Первый запрос за 5 минут
├── guide/
│   ├── configuration.md               # Все параметры BoostySettings, env vars, toml
│   ├── posts.md                       # CRUD постов, PostBuilder, уровни доступа
│   ├── subscriptions.md              # Верификация, уровни, подписчики
│   ├── donations.md                   # Отслеживание донатов, фильтрация
│   ├── events.md                      # EventPoller, @client.on(), EventType
│   ├── pagination.md                  # Ручная, async iterator
│   └── errors.md                      # Иерархия исключений, retry, обработка
├── api/
│   ├── client.md                      # ::: boostylib.BoostyClient
│   ├── models.md                      # ::: boostylib.models
│   ├── builders.md                    # ::: boostylib.builders.PostBuilder
│   ├── events.md                      # ::: boostylib.events
│   ├── exceptions.md                  # ::: boostylib.http.exceptions
│   └── config.md                      # ::: boostylib.config.BoostySettings
├── examples/
│   ├── telegram-bot.md                # Полный пример с aiogram
│   ├── discord-bot.md                 # Полный пример с discord.py
│   └── auto-responder.md             # Standalone скрипт авто-ответов
├── contributing.md                    # Как контрибьютить, dev setup
└── changelog.md                       # Версии, изменения
```

### 14.4 Пример страницы API Reference (`docs/api/client.md`)

```markdown
# BoostyClient

::: boostylib.BoostyClient
    options:
      members:
        - __init__
        - users
        - blogs
        - posts
        - comments
        - subscriptions
        - donations
        - targets
        - showcase
        - on
        - start_polling
        - stop_polling
        - close
```

### 14.5 Пример страницы User Guide (`docs/guide/posts.md`)

```markdown
# Working with Posts

## Listing posts

... code example ...

## Creating a post

### Free post
### Post for subscription level
### Post for donation
### Scheduled post
### Post with multiple content types

## Updating a post
## Deleting a post
## Deferred access
```

### 14.6 Команды

```bash
# Установка зависимостей документации
uv sync --extra docs

# Локальный сервер с hot-reload
uv run mkdocs serve

# Сборка статики
uv run mkdocs build

# Деплой на GitHub Pages
uv run mkdocs gh-deploy
```

### 14.7 CI для документации

```yaml
# .github/workflows/docs.yml
name: Docs

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --extra docs
      - run: uv run mkdocs gh-deploy --force
```

---

## 15. Логирование и отладка

### 15.1 Подход

Используем стандартный `logging` модуль Python (без внешних зависимостей типа `structlog`). Пользователь подключает любой handler/formatter на свой вкус.

```python
import logging

# Включить debug-логи boostylib
logging.getLogger("boostylib").setLevel(logging.DEBUG)
```

### 15.2 Логгеры по модулям

| Логгер | Что логирует |
|---|---|
| `boostylib.http` | Запросы/ответы: метод, URL, статус, время ответа |
| `boostylib.auth` | Refresh токена, истечение, ошибки аутентификации |
| `boostylib.events` | Polling-циклы, обнаруженные события, ошибки хэндлеров |
| `boostylib.retry` | Retry-попытки: причина, номер попытки, задержка |
| `boostylib.rate_limiter` | Ожидание при достижении лимита |

### 15.3 Маскирование секретов

Токены **никогда** не попадают в логи в открытом виде:

```
DEBUG boostylib.http: GET /v1/blog/test Authorization: Bearer a1b2...f9e8
DEBUG boostylib.auth: Token refreshed, new expiry: 2026-04-01T12:00:00Z
```

Реализация — `SecretStr` из Pydantic для хранения + кастомный `logging.Filter` для маскирования.

### 15.4 Debug-режим

```python
client = BoostyClient(
    settings=BoostySettings(debug=True),
    ...
)
```

В debug-режиме:
- Полный дамп тела запроса и ответа (с маскированием токенов)
- Замер времени каждого запроса
- Трейсинг retry-цепочек

---

## 16. Кеширование

### 16.1 Зачем

Некоторые данные меняются редко (уровни подписок, информация о блоге, профиль пользователя). Кеширование снижает нагрузку на API и ускоряет работу.

### 16.2 Протокол

```python
from typing import Protocol

class CacheBackend(Protocol):
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, *, ttl: int | None = None) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def clear(self) -> None: ...
```

### 16.3 Встроенные реализации

| Класс | Описание |
|---|---|
| `MemoryCache` | In-memory `dict` с TTL (по умолчанию) |
| `NullCache` | Кеш отключён — pass-through |

Пользователь может реализовать `CacheBackend` для Redis, SQLite и т.д.

### 16.4 Конфигурация

```python
class BoostySettings(BaseSettings):
    ...
    cache_enabled: bool = True
    cache_ttl_blog: int = 300        # 5 мин — информация о блоге
    cache_ttl_levels: int = 600      # 10 мин — уровни подписок
    cache_ttl_user: int = 120        # 2 мин — профиль пользователя
    cache_ttl_default: int = 60      # 1 мин — всё остальное
```

### 16.5 Использование

```python
# Кеш включён по умолчанию (MemoryCache)
client = BoostyClient(access_token="...")

# Отключить кеш
client = BoostyClient(
    access_token="...",
    settings=BoostySettings(cache_enabled=False),
)

# Свой backend
client = BoostyClient(
    access_token="...",
    cache=RedisCacheBackend(redis_url="redis://localhost"),
)

# Принудительно обойти кеш для одного запроса
levels = await client.subscriptions.get_levels("blog", use_cache=False)
```

### 16.6 Инвалидация

- Автоматическая — по TTL
- Ручная — `await client.cache.clear()` или `await client.cache.delete("blog:my_blog")`
- При write-операциях — кеш связанных ресурсов сбрасывается автоматически (создал пост → инвалидация списка постов)

---

## 17. Синхронная обёртка

### 17.1 Зачем

Не весь код async. Скрипты, CLI-утилиты, Django views, Jupyter-ноутбуки — всем нужен синхронный доступ.

### 17.2 API

```python
from boostylib.sync import SyncBoostyClient

with SyncBoostyClient(access_token="...") as client:
    user = client.users.get_current_user()
    levels = client.subscriptions.get_levels("my_blog")

    post = (
        PostBuilder()
        .title("Sync post")
        .text("Created from sync code")
        .free()
        .build()
    )
    client.posts.create_post("my_blog", post)
```

### 17.3 Реализация

- Отдельный `asyncio.EventLoop` в фоновом потоке
- Каждый sync-метод делает `loop.run_coroutine_threadsafe(coro).result()`
- Все API-модули проксируются автоматически — `SyncBoostyClient` генерируется из `BoostyClient`
- Polling событий в sync-режиме: `client.run_polling()` (блокирующий)

### 17.4 Структура

```
src/boostylib/
├── sync/
│   ├── __init__.py
│   ├── client.py          # SyncBoostyClient
│   └── _wrapper.py        # Утилита для генерации sync-прокси из async
```

---

## 18. Middleware / хуки запросов

### 18.1 Концепция

Pluggable пайплайн для перехвата HTTP-запросов и ответов. Позволяет пользователю добавлять кастомную логику без модификации библиотеки.

### 18.2 Протокол

```python
from typing import Protocol

class Middleware(Protocol):
    async def on_request(self, request: Request) -> Request:
        """Вызывается перед отправкой запроса. Может модифицировать request."""
        return request

    async def on_response(self, response: Response) -> Response:
        """Вызывается после получения ответа. Может модифицировать response."""
        return response

    async def on_error(self, request: Request, error: Exception) -> None:
        """Вызывается при ошибке запроса."""
        ...
```

### 18.3 Примеры middleware

```python
# Метрики (Prometheus, StatsD, etc.)
class MetricsMiddleware:
    async def on_request(self, request: Request) -> Request:
        request.extensions["start_time"] = time.monotonic()
        return request

    async def on_response(self, response: Response) -> Response:
        elapsed = time.monotonic() - response.request.extensions["start_time"]
        metrics.histogram("boosty_api_duration", elapsed, tags={"endpoint": request.url.path})
        metrics.counter("boosty_api_requests", tags={"status": response.status_code})
        return response

# Кастомные заголовки
class CustomHeadersMiddleware:
    def __init__(self, headers: dict[str, str]):
        self.headers = headers

    async def on_request(self, request: Request) -> Request:
        request.headers.update(self.headers)
        return request

# Аудит-лог
class AuditMiddleware:
    async def on_response(self, response: Response) -> Response:
        if response.request.method in ("POST", "PUT", "DELETE"):
            await audit_log.write(
                method=response.request.method,
                url=str(response.request.url),
                status=response.status_code,
            )
        return response
```

### 18.4 Подключение

```python
client = BoostyClient(
    access_token="...",
    middleware=[
        MetricsMiddleware(),
        CustomHeadersMiddleware({"X-Request-Source": "my-bot"}),
        AuditMiddleware(),
    ],
)
```

Middleware выполняются в порядке регистрации (on_request) и в обратном порядке (on_response).

---

## 19. CLI-утилита

### 19.1 Назначение

Быстрые операции из терминала без написания кода. Полезно для отладки, мониторинга и скриптов.

### 19.2 Установка

```bash
pip install boostylib[cli]
# или
uv add boostylib[cli]
```

Дополнительная зависимость: `click` (или `typer`).

### 19.3 Команды

```bash
# Аутентификация — сохранить токены
boosty auth setup
# → Интерактивный ввод access_token, refresh_token, device_id
# → Сохраняет в ~/.boosty/auth.json

boosty auth status
# → Показывает: токен валиден, expires_at, device_id

# Информация о блоге
boosty blog info <username>
# → Имя, подписчики, уровни подписок, количество постов

# Посты
boosty posts list <username> [--limit 10] [--level premium]
boosty posts get <username> <post_id>
boosty posts create <username> --title "..." --text "..." --level <level_id>
boosty posts delete <username> <post_id>

# Подписчики
boosty subscribers list <username> [--level premium] [--format json|csv|table]
boosty subscribers check <username> <user_id>

# Донаты
boosty donations list <username> [--from 2026-01-01] [--to 2026-03-21] [--format json|csv|table]

# Экспорт данных
boosty export subscribers <username> -o subscribers.csv
boosty export donations <username> --from 2026-01-01 -o donations.json
boosty export posts <username> -o posts.json
```

### 19.4 Форматы вывода

Все команды поддерживают `--format`:

| Формат | Описание |
|---|---|
| `table` | Человекочитаемая таблица (по умолчанию) |
| `json` | JSON (для пайпов и скриптов) |
| `csv` | CSV (для Excel, аналитики) |

### 19.5 Структура

```
src/boostylib/
├── cli/
│   ├── __init__.py
│   ├── app.py              # Корневая click/typer группа
│   ├── auth.py             # boosty auth ...
│   ├── blog.py             # boosty blog ...
│   ├── posts.py            # boosty posts ...
│   ├── subscribers.py      # boosty subscribers ...
│   ├── donations.py        # boosty donations ...
│   ├── export.py           # boosty export ...
│   └── formatters.py       # table, json, csv форматирование
```

```toml
# pyproject.toml
[project.scripts]
boosty = "boostylib.cli.app:main"

[project.optional-dependencies]
cli = ["click>=8.1", "rich>=13.0"]  # rich для красивых таблиц
```

---

## 20. Экспорт данных

### 20.1 Программный API

```python
from boostylib.export import Exporter, ExportFormat

async with BoostyClient(access_token="...") as client:
    exporter = Exporter(client)

    # Экспорт подписчиков в CSV
    await exporter.subscribers(
        "my_blog",
        format=ExportFormat.CSV,
        output=Path("subscribers.csv"),
    )

    # Экспорт донатов в JSON за период
    await exporter.donations(
        "my_blog",
        format=ExportFormat.JSON,
        output=Path("donations.json"),
        from_date=date(2026, 1, 1),
        to_date=date(2026, 3, 21),
    )

    # Экспорт постов в SQLite
    await exporter.posts(
        "my_blog",
        format=ExportFormat.SQLITE,
        output=Path("blog_archive.db"),
    )
```

### 20.2 Поддерживаемые форматы

| Формат | Назначение |
|---|---|
| `CSV` | Excel, Google Sheets, аналитика |
| `JSON` | Интеграции, бэкапы |
| `JSONL` | Потоковая обработка больших объёмов |
| `SQLITE` | Локальная аналитика, SQL-запросы |

### 20.3 Структура

```
src/boostylib/
├── export/
│   ├── __init__.py
│   ├── exporter.py        # Exporter — фасад
│   ├── formats.py         # ExportFormat enum
│   ├── writers/
│   │   ├── __init__.py
│   │   ├── csv.py
│   │   ├── json.py
│   │   ├── jsonl.py
│   │   └── sqlite.py
│   └── _protocol.py       # Writer protocol
```

---

## 21. Безопасность

### 21.1 Хранение токенов

- `FileTokenStorage` создаёт `~/.boosty/auth.json` с правами `600` (только владелец) на Unix
- На Windows — ACL, доступ только текущему пользователю
- Библиотека предупреждает (`logging.WARNING`), если файл токенов имеет слишком широкие права

### 21.2 Логирование

- Токены маскируются везде: логи, repr моделей, трейсбеки
- `access_token`, `refresh_token`, `device_id` хранятся как `pydantic.SecretStr`
- В debug-режиме тело запроса/ответа выводится, но `Authorization` header маскирован

### 21.3 Защита от бана

- Встроенный rate limiter (token bucket) — по умолчанию 60 req/min (настраивается)
- Экспоненциальный backoff при 429
- Настраиваемый `User-Agent`
- Рекомендация в документации: не делать polling чаще 30 секунд

### 21.4 Транспорт

- Все запросы только через HTTPS
- Валидация SSL-сертификатов включена (httpx default)
- Никаких `verify=False` по умолчанию

### 21.5 Зависимости

- Минимальное количество зависимостей (httpx, pydantic, pydantic-settings)
- Регулярный аудит через `pip-audit` / `uv audit` в CI

---

## 22. Plugin-система

### 22.1 Зачем

Позволяет расширять библиотеку без форков. Кастомные API-модули, обработчики событий, форматы экспорта.

### 22.2 Регистрация

```python
from boostylib.plugins import Plugin

class AnalyticsPlugin(Plugin):
    name = "analytics"

    def on_register(self, client: BoostyClient) -> None:
        """Вызывается при подключении к клиенту."""
        self.client = client

    async def get_stats(self, username: str) -> BlogStats:
        """Кастомная аналитика поверх базовых API."""
        posts = []
        async for post in self.client.posts.iter_posts(username):
            posts.append(post)
        return BlogStats(
            total_posts=len(posts),
            avg_comments=sum(p.comments_count for p in posts) / len(posts),
            ...
        )

# Подключение
client = BoostyClient(access_token="...")
analytics = AnalyticsPlugin()
client.register_plugin(analytics)

stats = await analytics.get_stats("my_blog")
```

### 22.3 Хуки плагинов

```python
class Plugin(Protocol):
    name: str
    def on_register(self, client: BoostyClient) -> None: ...
    def on_unregister(self) -> None: ...
    async def on_event(self, event: Event) -> None: ...  # опционально
```

---

## 23. Примеры проектов

### 23.1 Структура

```
examples/
├── telegram_bot/
│   ├── README.md            # Инструкция по запуску
│   ├── pyproject.toml       # Зависимости: boostylib, aiogram
│   ├── bot.py               # Telegram-бот с верификацией подписки
│   └── .env.example         # Шаблон переменных окружения
├── discord_bot/
│   ├── README.md
│   ├── pyproject.toml       # Зависимости: boostylib, discord.py
│   ├── bot.py               # Discord-бот с ролями по уровню подписки
│   └── .env.example
├── auto_responder/
│   ├── README.md
│   ├── pyproject.toml
│   ├── responder.py         # Standalone авто-ответчик на донаты/подписки
│   └── config.toml.example  # Шаблон конфигурации с правилами ответов
├── export_analytics/
│   ├── README.md
│   ├── export.py            # Скрипт экспорта подписчиков + донатов в CSV
│   └── analyze.py           # Jupyter-friendly аналитика
└── fastapi_webhook/
    ├── README.md
    ├── pyproject.toml
    ├── app.py               # FastAPI-сервер с эндпоинтами для проверки подписки
    └── .env.example
```

### 23.2 Пример: Telegram-бот (кратко)

```python
"""
Telegram-бот, выдающий доступ к закрытому каналу
по верификации подписки на Boosty.
"""
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from boostylib import BoostyClient
from boostylib.auth import EnvTokenStorage

router = Router()
boosty = BoostyClient(token_storage=EnvTokenStorage())

@router.message(Command("verify"))
async def verify(message):
    boosty_id = await db.get_boosty_id(message.from_user.id)
    if not boosty_id:
        await message.answer("Привяжите Boosty: /link <ваш_username>")
        return

    status = await boosty.subscriptions.verify_subscription("my_blog", boosty_id)
    if status.is_subscribed and status.level.price >= 500:
        invite = await bot.create_chat_invite_link(PRIVATE_CHANNEL_ID, member_limit=1)
        await message.answer(f"Подписка подтверждена! Вот ваша ссылка: {invite.invite_link}")
    else:
        await message.answer("Нужна подписка от 500₽ на boosty.to/my_blog")
```

---

## 24. Обновлённая дорожная карта

### Фаза 1 — Ядро (MVP)
1. Конфигурация (`config.py`)
2. HTTP-транспорт (`http/`) — retry, rate limiting, исключения
3. Аутентификация (`auth/`) — token storage, auto-refresh
4. Модели данных (`models/`)
5. Логирование с маскированием секретов
6. `BoostyClient` — фасад

### Фаза 2 — API Read
7. `UsersAPI`, `BlogsAPI`, `PostsAPI` (чтение), `SubscriptionsAPI`, `CommentsAPI`
8. Пагинация + async-итераторы
9. Кеширование (MemoryCache)

### Фаза 3 — API Write + Media
10. `PostsAPI` (создание, обновление, удаление) + `PostBuilder`
11. `MediaAPI` — загрузка файлов, изображений, видео, аудио
12. `CommentsAPI` (создание), `TargetsAPI`, `ShowcaseAPI`

### Фаза 4 — События и автоматизация
13. `EventPoller` + `EventDispatcher` с декораторным API
14. Middleware-система
15. Синхронная обёртка (`SyncBoostyClient`)

### Фаза 5 — CLI и экспорт
16. CLI-утилита (`boosty` команда)
17. Экспорт данных (CSV, JSON, JSONL, SQLite)

### Фаза 6 — Production Readiness
18. Plugin-система
19. Документация (MkDocs)
20. README, CHANGELOG
21. CI/CD pipeline
22. Публикация на PyPI
23. Примеры проектов (Telegram, Discord, FastAPI, авто-ответчик)

---

## 25. Ограничения и риски

| Риск | Митигация |
|---|---|
| API неофициальный, может измениться | Все endpoint'ы и модели изолированы; адаптеры легко обновить |
| Нет вебхуков | Polling с настраиваемым интервалом; архитектура готова к вебхукам, если появятся |
| Токены получаются только вручную | Документация с пошаговой инструкцией; CLI `boosty auth setup` упрощает процесс |
| Rate limits неизвестны | Консервативный rate limiter по умолчанию; настраивается через конфиг |
| Нет эндпоинта для списка донатов напрямую | Polling через доступные эндпоинты, детекция по изменениям |
| Блокировка при агрессивном polling | Rate limiter + backoff + рекомендации в документации |
