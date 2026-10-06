# Аналитика AI Media Client: пакет для отдельного хоста

Пакет предназначен для **self-hosted PostHog и продуктовой аналитики**. ClickHouse — внутреннее хранилище PostHog. ClickStack и сбор технических логов AI Media Client в задачу не входят. Код AI Media Client этот репозиторий не меняет.

В репозитории лежат байтовые снимки upstream `docker-compose.base.yml` и `docker-compose.yml` (исходный `docker-compose.hobby.yml`) для коммита из `POSTHOG_VERSION`. `prepare` сверяет их с точным Git checkout и копирует из него `.env.services` без личных секретов. Лицензия upstream приложена в `POSTHOG_LICENSE`.

## Требования и ограничения

- Выделенный Linux-хост с Docker Engine, Docker Compose v2.33+ (`!reset`), Git, Python 3.12+, curl и brotli. Нужны достаточные CPU, RAM и свободное место для 38 сервисов, их образов и резервных копий; вместимость определите на staging. Нужен исходящий доступ к GitHub, Docker Hub, GHCR, прочим реестрам из Compose, GeoIP CDN и ACME CA. Проверьте архитектуру CPU и наличие образов для неё.
- Домен с корректной DNS A-записью; AAAA публикуйте только при рабочем IPv6. Для стандартного ACME Caddy откройте извне TCP 80 и 443 и проверьте их доступность снаружи. SSH открывайте только через VPN или узкий allowlist, а доступ к Docker daemon — только доверенным администраторам. Правила UFW сами по себе не гарантируют блокировку опубликованных Docker-портов: проверьте firewall и правила у провайдера.
- `POSTHOG_VERSION` — точный Git-коммит. `lock-images` **один раз по явной команде на целевом хосте** скачивает все образы и фиксирует digest для его платформы. Зафиксируйте `image-lock.json` и `docker-compose.images.json` отдельным коммитом после проверки. `up` использует только сохранённые digest с `--pull missing --no-build`: на новом хосте он скачает отсутствующие digest, но не обновит их вслед за `master`/`latest`. Перед production проверьте комбинацию образов на staging: равенство Git-коммита не гарантирует совместимость плавающих upstream-тегов на момент lock.
- Не запускайте upstream `bin/deploy-hobby`: он автоматически подтягивает образы и отправляет телеметрию установки.

## Первый запуск

```bash
python3 analyticsctl.py init --domain analytics.your-domain.net
python3 analyticsctl.py prepare
python3 analyticsctl.py check
docker compose -f docker-compose.yml -f docker-compose.security.yml -f docker-compose.images.json config --quiet
python3 analyticsctl.py up
```

`init` создаёт `.env` со случайными секретами и не перезаписывает его. `prepare` получает закреплённый коммит, сверяет Compose-файлы, создаёт служебные файлы и скачивает GeoIP; контейнеры не запускает. Digest-файлы уже зафиксированы для Linux/amd64. Только при создании **нового** lock на другой платформе и после проверки совместимости запускайте `python3 analyticsctl.py lock-images`; команда откажется перезаписывать существующие lock-файлы. Не коммитьте `.env`, `.env.services`, `posthog/`, GeoIP, ключи, резервные копии и пользовательские данные. Полный вывод `docker compose config` может содержать секреты; используйте `--quiet` либо не публикуйте вывод.

На 2026-09-30 на Debian 13/amd64 выполнены `init`, `prepare`, `lock-images` и `check`; скачаны 24 уникальных образа, 38 сервисов привязаны к digest. Итоговая модель публикует только 80/443 у `proxy`, не содержит `build` и анонимных томов. Caddy получил сертификат Let’s Encrypt для тестового имени `analytics-195-209-221-217.sslip.io`. Полный запуск 38 сервисов на VPS с 2 vCPU/4 ГБ RAM/40 ГБ диска занял всю RAM и добавленные 2 ГБ swap до готовности веб-сервиса. UI, `/_health` с HTTP 200, smoke, backup и restore этим запуском не подтверждены.

## Экспериментальный POC на 4 ГБ

`docker-compose.poc.yml` уменьшает Redpanda до одного ядра и 1 ГБ памяти, а веб-сервис до одного Granian-воркера. `up-poc` запускает только `proxy`, `capture`, `ingestion-general`, `plugins`, `feature-flags` и их зависимости (17 сервисов на проверенном снимке). Это состав для проверки продуктовой аналитики, а не подтверждённая production-конфигурация. Session replay, технические логи, Temporal и остальные необязательные службы не запускаются. Все образы остаются привязаны к тем же digest; наружу по-прежнему выходят только 80/443.

```bash
python3 analyticsctl.py check-poc
python3 analyticsctl.py up-poc
docker compose -f docker-compose.yml -f docker-compose.security.yml -f docker-compose.images.json -f docker-compose.poc.yml ps
curl --fail --show-error https://analytics.your-domain.net/_health
```

Первый POC-прогон с Redpanda 1 ГБ, но ещё с четырьмя веб-воркерами, прошёл первичные миграции и затем исчерпал RAM/swap при старте Granian. Ограничение до одного веб-воркера проверено через `docker compose config` и локальные тесты, но фактический повторный старт и HTTP 200 пока не проверены. После образов и первых томов на 40-ГБ VPS оставалось около 6,6 ГБ: для длительного хранения событий и локальных резервных копий увеличьте диск либо вынесите зашифрованные копии на отдельное хранилище.

После `up` проверьте `docker compose -f docker-compose.yml -f docker-compose.security.yml -f docker-compose.images.json ps`. Дождитесь HTTP 200 от `https://analytics.your-domain.net/_health`: первые миграции могут идти несколько минут. Проверьте сертификат в браузере. Войдите в PostHog, создайте проект `production`, отключите в настройках проекта Autocapture и Session replay и проверьте сохранённые значения. При необходимости создайте отдельный `staging`. До приёмки не отправляйте события продукта.

Ключ **проекта** введите в текущую сессию терминала без сохранения в файле или истории:

```bash
read -rs POSTHOG_PROJECT_KEY; export POSTHOG_PROJECT_KEY; echo
python3 analyticsctl.py smoke
unset POSTHOG_PROJECT_KEY
```

`smoke` отправляет только синтетическое `analytics_smoke` по HTTPS и ждёт его появления в ClickHouse через `docker compose exec`; база остаётся внутри Docker-сети. Скрипт напечатает UUID. Найдите то же событие в PostHog Live events по времени и `distinct_id=smoke:<UUID>`, зафиксируйте подтверждение UI. Исключите `analytics_smoke` из продуктовых панелей. Приёмка: здоровые контейнеры, корректный HTTPS, защищённый вход администратора, событие в UI и ClickHouse.

## Конфигурация и защита

`docker-compose.security.yml` сбрасывает публикацию внутренних портов и upstream `build`, оставляет только TCP 80/443 у Caddy, ограничивает его заданным доменом, исправляет пути монтирования `db` и заменяет анонимные тома Caddy/Elasticsearch именованными. `check` сверяет overlay с закреплённым upstream, требует digest и `pull_policy: never`, запрещает анонимные тома и публикацию внутренних служб. Итоговый Compose проверен локальным парсером v2.39.4; запуск контейнеров требует отдельного Linux-хоста.

Для защиты административного интерфейса при обычном ACME оставьте Caddy доступным по 80/443 для проверки сертификата, используйте личные учётные записи PostHog с сильными паролями, MFA/SSO если эта версия их поддерживает, и закройте свободную регистрацию после создания администратора. Если нужен сетевой запрет доступа к UI, поставьте перед PostHog внешний identity-aware reverse proxy, который сам обслуживает ACME (или DNS-01) и пропускает к UI только авторизованных администраторов; маршруты будущего ingestion проверьте отдельно. Не закрывайте 80/443 перед Caddy без замены схемы ACME. В upstream hobby Compose есть публично известные внутренние пароли по умолчанию: сервер должен быть выделенным и доверенным, с шифрованием диска и ограниченным доступом к Docker. Административный токен PostHog нельзя помещать в браузерный код.

## Резервное копирование и восстановление

Во время окна обслуживания выполните **холодную** копию на Linux-хосте. Скрипт убеждается, что необходимые тома и основные сервисы существуют, останавливает стек, сохраняет все тома с меткой Compose, конфигурацию и SHA-256, затем снова запускает закреплённую конфигурацию. Нужен root-доступ к каталогам томов Docker. При ошибке копия остаётся помеченной `INCOMPLETE`; при ошибке повторного запуска команда завершается ошибкой. Копия содержит персональные данные, ключи Caddy и секреты `.env`: шифруйте её и храните вне сервера с ограниченным доступом.

```bash
BACKUP_DIR="backups/$(date -u +%Y%m%dT%H%M%SZ)"
sudo python3 analyticsctl.py backup "$BACKUP_DIR"
```

Для ограниченного POC используйте `sudo python3 analyticsctl.py backup "$BACKUP_DIR" --poc`: команда перезапустит только POC-состав. Режим записывается в манифест копии; после `restore` запускайте `python3 analyticsctl.py check-poc` и `python3 analyticsctl.py up-poc`. На текущем VPS копирование и восстановление ещё не проверены.

Проверку восстановления выполняйте на **отдельной чистой VM с отдельным Docker daemon** и закрытым внешним доступом. Имя Compose-проекта в `.env` фиксировано, поэтому другой каталог на production-хосте не является изоляцией. `restore` проверяет хеши и отказывается работать при существующих контейнерах или любом существующем целевом томе. Перенесите каталог копии и тот же коммит этого репозитория на VM, затем выполните:

```bash
BACKUP_DIR=/secure/path/to/transferred-backup
sudo python3 analyticsctl.py restore "$BACKUP_DIR"
python3 analyticsctl.py check
python3 analyticsctl.py up
docker compose -f docker-compose.yml -f docker-compose.security.yml -f docker-compose.images.json ps
docker compose -f docker-compose.yml -f docker-compose.security.yml -f docker-compose.images.json exec -T clickhouse clickhouse-client --query "SELECT count() FROM posthog.events WHERE event = 'analytics_smoke' AND distinct_id = 'smoke:<UUID_ИЗ_PRODUCTION>'"
DOMAIN=$(sed -n 's/^DOMAIN=//p' .env)
curl --fail --show-error --silent --resolve "$DOMAIN:443:127.0.0.1" "https://$DOMAIN/_health"
```

Сохраните исходный домен и `.env`: в копии находятся сертификат и ключ Caddy. Для проверки UI направьте этот домен на IP VM только на администраторской машине; не меняйте публичный DNS. Сверьте исторический `analytics_smoke` по UUID в UI и ClickHouse, число событий за выбранный день и права контейнеров на восстановленные файлы. Новое `smoke` на VM запускайте только после проверки, что её DNS для домена указывает на саму VM, иначе событие уйдёт в production. Зафиксируйте длительность восстановления. Успешный `backup` без этой репетиции не доказывает восстановимость.

## Обновление

1. Сделайте копию и репетицию восстановления. Сохраните текущие `POSTHOG_VERSION`, lock-файлы и Compose-снимки.
2. В отдельном staging checkout поменяйте `POSTHOG_VERSION` и `POSTHOG_APP_TAG` в секретном `.env` на один и тот же проверенный upstream-коммит. Пересоздайте upstream-снимки и lock-файлы там, затем повторите `prepare`, `lock-images`, `check`, `up`, `smoke`. Просмотрите изменения Compose, миграций и digest. Не запускайте автоматический upstream upgrade на production.
3. Сравните основные отчёты до переноса в production. Откат может потребовать восстановления соответствующей копии томов: миграции БД обычно необратимы.

## Облачный ежедневный отчёт и графики

Подготовлены [инструкция установки и приёмки](docs/scheduled-analytics.md),
[промпт облачной задачи на 09:00 по Москве](reporting/daily-task-prompt.md),
MCP с OAuth и только фиксированными агрегатными запросами, а также два
дашборда с восемью графиками. Процесс отчётов размещается на VPS, анализ —
в облачной задаче ChatGPT. Компьютер пользователя для этой схемы не нужен,
но поддержку подключённого инструмента нужно подтвердить фактическим
облачным запуском. Это не локальная автоматизация Codex.

В этом изменении подготовлены файлы и локальные проверки; reporting service,
панели и облачная задача ещё не установлены. Рабочий PostHog:
`https://analytics-195-209-221-217.sslip.io`, проект 1. Не публикуйте базы
или MCP без OAuth. Инструкция содержит отдельную проверку живых запросов,
HTTPS, OAuth, повторного создания панелей, token refresh и резервирования
секретов/состояния службы.

## Интеграция в продукт позже

В исходном AI Media Client документ `docs/product-analytics.md` содержит каталог событий, карту точек, правила согласия, PostgreSQL outbox и рецепты панелей. Подключайте продукт отдельной задачей только после приёмки PostHog; начните с новых событий, не отправляйте промпты и персональные данные без согласованного контракта. Autocapture и Session replay оставьте выключенными.

Источники: [upstream PostHog](https://github.com/PostHog/posthog), [Caddy Automatic HTTPS](https://caddyserver.com/docs/automatic-https), [Docker и firewall](https://docs.docker.com/engine/network/packet-filtering-firewalls/).
