# Ежедневный облачный отчёт и панели PostHog

## Подготовлено и что ещё не проверено

Схема: облачная задача ChatGPT → HTTPS MCP с OAuth на VPS → Query API проекта 1 PostHog. В облако уходят агрегаты и названия моделей/провайдеров. Сырые события и идентификаторы людей не возвращаются. Анализ агрегатов выполняется в облаке OpenAI; это не полностью локальная обработка.

Подготовлены два дашборда с восемью графиками, установка отдельного процесса и [промпт задачи](../reporting/daily-task-prompt.md). В этом изменении процесс **не развёрнут**, дашборды **не созданы в рабочем проекте**, облачная задача **не зарегистрирована**. Проверены локальные тесты MCP/Compose и схемы восьми графиков из закреплённого upstream. HogQL, OAuth и графики на живом API требуют проверки ниже.

При диагностике 2026-10-06 на VPS было около 814 МиБ доступной RAM и занято 1849 из 2047 МиБ swap. Это моментальный замер, а не доказательство причины зависания UI. Перед установкой повторите `free -m`, `vmstat 1 5`, `df -h /` и `docker stats --no-stream`; сначала обеспечьте запас памяти/диска. Сервис ограничен 384 МиБ RAM и половиной одного CPU; это ограничение, а не гарантированное потребление. Шесть запросов отчёта выполняются последовательно. Новые тяжёлые проверки Django при дефиците ресурсов не запускайте.

## Панели

| Дашборд | Графики |
| --- | --- |
| Product overview | Активные идентичности; принятые и терминальные генерации; success/(success+fail); P95 длительности успешных генераций; модели/провайдеры |
| Funnels and retention | Вход → принятие → успех за 7 дней; модель → цена → принятие за 1 день; возврат к успешной генерации D0–D7 |

Окно панелей — последние 30 дней. Часовой пояс проекта в Settings → Customization установите `Europe/Moscow`, чтобы дневные графики совпадали с отчётом. Воронки сопоставляют одну идентичность, а не все `v_` с `u_`. Незрелые когорты retention и отсутствующие события не трактуйте как отток. Native графики считают capture-события, отчёт считает уникальные UUID; проверяйте повторы. Autocapture, heatmaps, web vitals и Session replay оставьте выключенными. Отчёт не получает данные воронок/retention автоматически: он даёт ссылки для просмотра человеком.

## 1. Перенести исходники и установить зависимости

Команды ниже выполняются **на Linux VPS** из `/home/debianuser/ai-media-client-analytics`. Перенесите изменённые `analyticsctl.py`, `docker-compose.security.yml` и каталог `reporting/` из этого коммита. Не переносите локальные `.env`, виртуальное окружение или каталог upstream поверх рабочих файлов. SSH: `debianuser@195.209.221.217`; ключ остаётся на вашем компьютере.

```bash
sudo apt-get update
sudo apt-get install -y python3-venv
python3 -m venv .local-tools/report-venv
.local-tools/report-venv/bin/python -m pip install -r reporting/requirements.txt
.local-tools/report-venv/bin/python -m reporting.setup_dashboards > /tmp/analytics-dashboard-plan.json
```

Последняя команда печатает определения и ничего не меняет в PostHog. Закреплены версии FastMCP и tzdata; транзитивные зависимости разрешает pip, полноценного Linux lockfile пока нет.

## 2. Проверить и создать графики

Создайте **временный personal API key** в настройках пользователя PostHog, с доступом только к проекту 1 и scopes `project:read`, `query:read`, `dashboard:read`, `dashboard:write`, `insight:read`, `insight:write`. Это административный ключ подготовки, он не используется MCP и не сохраняется в конфиге службы. `phc_...` — ключ отправки событий, он здесь не подходит.

```bash
export REPORT_POSTHOG_ORIGIN=https://analytics-195-209-221-217.sslip.io
export REPORT_PROJECT_ID=1
read -rsp 'Temporary setup key: ' REPORT_SETUP_TOKEN
export REPORT_SETUP_TOKEN
printf '\n'
.local-tools/report-venv/bin/python -m reporting.check
# Только если все 6 агрегатных запросов и 8 источников графиков прошли проверку:
.local-tools/report-venv/bin/python -m reporting.setup_dashboards --apply
# Повторный запуск обязан вернуть те же ссылки, без новых объектов:
.local-tools/report-venv/bin/python -m reporting.setup_dashboards --apply
unset REPORT_SETUP_TOKEN
```

Откройте обе ссылки, проверьте графики и фильтры. Сохраните возвращённый JSON ссылок для `REPORT_DASHBOARD_LINKS`. Отзовите временный ключ. Создатель панелей добавляет только отсутствующие объекты со своим маркером; существующие запросы не перезаписывает. Не запускайте два создателя одновременно. Дубли маркеров или ручное удаление принадлежности insight дашборду требуют ручного разбора; автоматической перезаписи нет. Частично выполненный запуск можно повторить после исправления причины.

## 3. Подготовить OAuth без передачи токенов в промпт

Выбран новый адрес `https://reports-195-209-221-217.sslip.io`; это **планируемый адрес**, его DNS/HTTPS ещё не приняты. До установки проверьте A-запись на `195.209.221.217` и исходящий/входящий ACME.

В браузере, будучи залогиненным администратором PostHog, откройте `/api/users/@me/`, возьмите числовое поле `id` вашего пользователя. Не путайте с `uuid`. Скрипт проверяет роль администратора организации и наличие scope ceilings в реальном runtime; при несовместимости он останавливается. Не заменяйте его приложением с широкими правами.

```bash
read -rp 'PostHog owner numeric id: ' REPORT_OWNER_USER_ID
docker exec -i -u 0 \
  -e REPORT_OWNER_USER_ID="$REPORT_OWNER_USER_ID" \
  -e REPORT_PROJECT_ID=1 \
  -e REPORT_POSTHOG_ORIGIN=https://analytics-195-209-221-217.sslip.io \
  -e REPORT_PUBLIC_ORIGIN=https://reports-195-209-221-217.sslip.io \
  -e REPORT_BOOTSTRAP_OUTPUT=/tmp/analytics-report-bootstrap.env \
  ai-media-analytics-web-1 python - < reporting/register_oauth.py
sudo install -d -m 700 /root/analytics-report-bootstrap
sudo docker cp ai-media-analytics-web-1:/tmp/analytics-report-bootstrap.env /root/analytics-report-bootstrap/report.env
sudo chmod 600 /root/analytics-report-bootstrap/report.env
sudo docker exec ai-media-analytics-web-1 rm /tmp/analytics-report-bootstrap.env
```

Создаётся одно confidential OAuth-приложение с `query:read`, `project:read`. Секреты пишутся исключительно в файл с правами 0600, не печатаются. Повторный запуск при существующем приложении/файле отказывается заменять секреты. Если приложение уже создано, используйте сохранённый файл; ротация — отдельная операция. Само создание приложения не выдаёт доступ к данным: пользователь далее подтверждает OAuth в браузере и выбирает **только проект 1**.

## 4. Установить MCP и HTTPS

Узнайте IP Docker bridge, доступный из контейнера Caddy:

```bash
docker network inspect bridge --format '{{(index .IPAM.Config 0).Gateway}}'
```

Обычно это `172.17.0.1`, но используйте **фактическое значение**. В приватном `/root/analytics-report-bootstrap/report.env` через `sudoedit` установите `REPORT_BIND` в этот IP, `REPORT_DASHBOARD_LINKS` в JSON полученных ссылок. JSON в EnvironmentFile оборачивайте одинарными кавычками:

```text
REPORT_BIND=172.17.0.1
REPORT_DASHBOARD_LINKS='{"overview":"https://analytics-195-209-221-217.sslip.io/project/1/dashboard/ID1","journey":"https://analytics-195-209-221-217.sslip.io/project/1/dashboard/ID2"}'
REPORT_REDIRECT_URIS='["https://chatgpt.com/connector_platform_oauth_redirect"]'
```

`ID1/ID2` заменяются реальными ID. `REPORT_REDIRECT_URIS` должен совпадать с **точным OAuth callback**, показанным ChatGPT при добавлении подключения. Никаких wildcard. Исходный callback указан как типичный; если UI показывает другой — измените конфиг до подключения. Callback PostHog-приложения — отдельный адрес `https://reports-195-209-221-217.sslip.io/auth/callback`.

```bash
sudo bash reporting/install.sh /root/analytics-report-bootstrap/report.env
sudo systemctl enable --now ai-media-analytics-report
sudo systemctl status ai-media-analytics-report --no-pager
```

Установка сама службу не запускает, не меняет PostHog и отказывается перезаписывать отличный существующий `/etc/ai-media-analytics-report.env`. В дальнейшем редактируйте этот файл через `sudoedit`, затем перезапускайте только reporting service. У пользователя `analytics-report` нет Docker и ключа записи в PostHog.

В существующий игнорируемый `.env` PostHog добавьте блок, подставив фактический bridge IP. Если `CADDY_EXTRA_CONFIG` уже есть, объедините с ним, не теряя прежние маршруты:

```dotenv
CADDY_EXTRA_CONFIG='reports-195-209-221-217.sslip.io {
    reverse_proxy 172.17.0.1:8765
}'
```

Обновлённый security overlay передаёт этот блок в штатный Caddy. HTTPS/ACME обслуживает тот же прокси; порт 8765 не публикуется Compose и не должен слушать `0.0.0.0` или публичный IP. Проверьте firewall: разрешите обращение Docker-подсети к bridge IP:8765, сохранив запрет внешнего доступа. Не публикуйте PostgreSQL/ClickHouse. 80/443 оставьте доступны для ACME; API требует OAuth независимо от открытого HTTPS.

```bash
python3 analyticsctl.py check-poc
docker compose -f docker-compose.yml -f docker-compose.security.yml -f docker-compose.images.json -f docker-compose.poc.yml up -d --no-build --pull never --no-deps proxy
curl --fail --show-error https://reports-195-209-221-217.sslip.io/.well-known/oauth-authorization-server
# Без Bearer ожидается HTTP 401, а не данные:
curl -i -X POST https://reports-195-209-221-217.sslip.io/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
curl --fail --show-error https://analytics-195-209-221-217.sslip.io/_health
```

Не выполняйте `lock-images`, upstream upgrade или сброс томов ради установки отчётов. Если проверка конфигурации/HTTPS/OAuth не проходит, не создавайте расписание до исправления. Подтвердите отсутствие внешнего доступа к IP:8765 с другого хоста, стабильную работу PostHog и ресурсный запас при запросах.

## 5. Подключить к ChatGPT и создать облачную задачу

В ChatGPT включите доступную вашему аккаунту настройку developer mode/custom MCP, добавьте HTTPS MCP `https://reports-195-209-221-217.sslip.io/mcp` с **OAuth**. Настройку приложения может ограничивать план/политика аккаунта. Завершите OAuth лично, проверьте scopes и выбранный проект. Не вставляйте personal API key, `phc_...`, SSH-ключ или содержимое env в промпт задачи. Если UI просит OAuth client ID/secret для регистрации клиента самого MCP, не подставляйте upstream PostHog secret: мост предоставляет dynamic client registration.

В новом облачном чате с этим подключением сначала попросите вызвать `analytics_daily_report` и `analytics_dashboard_links`. Убедитесь, что пришли реальные агрегаты проекта 1, `complete=true` и рабочие ссылки. В инструменте всего два чтения; он не принимает SQL, project ID или имена полей от модели.

В том же **облачном интерфейсе «Запланировано»**, который показан в задаче «Цены конкурентов KIE», создайте задачу:

- название: `AI Media Client — ежедневная аналитика`;
- инструкция: текст [daily-task-prompt.md](../reporting/daily-task-prompt.md), без заголовка;
- повтор: ежедневно, **09:00**, часовой пояс **Москва / Europe/Moscow**;
- выполнение: один чат для всех запусков;
- подключение: созданный MCP с завершённой OAuth-авторизацией;
- модель: доступная облачная модель с поддержкой инструментов.

Не выбирайте локальный проект/рабочую папку в настройке автоматизации. Если в настройках **облачной** задачи подключение недоступно, эта схема в текущем интерфейсе не работает: сначала проверьте поддержку custom tools для этой задачи, не заменяйте её локальной автоматизацией. Наличие расписания само по себе не подтверждает выполнение инструментов.

Выполните «Запустить сейчас», проверьте фактический вызов MCP и отчёт. После этого проверьте следующий запуск в 09:00 с выключенным компьютером. Проверьте обновление OAuth после истечения access token и работу после перезапуска службы. Пока эти проверки не пройдены, независимость от ПК и ежедневная доставка не считаются подтверждёнными. Для этой схемы не нужен отдельный Anthropic/OpenAI API key на VPS: VPS выполняет запросы, облачная задача выполняет анализ в рамках доступных функций аккаунта.

## Обслуживание, резервные копии и откат

`/etc/ai-media-analytics-report.env` и `/var/lib/ai-media-analytics-report` содержат OAuth credentials, signing key, ключ шифрования и зашифрованные refresh tokens. Не коммитьте и не отправляйте их в чат. Ключи должны сохраняться между рестартами. Потеря состояния/ключей означает повторную OAuth-авторизацию.

`analyticsctl backup` сохраняет конфиг и тома PostHog, но **не эту systemd-службу**. В отдельное окно остановите reporting, создайте закрытый архив и сразу зашифруйте его/перенесите в утверждённое приватное хранилище:

```bash
sudo systemctl stop ai-media-analytics-report
sudo test ! -e /root/analytics-report-bootstrap/reporting-private.tar.gz
sudo tar -czf /root/analytics-report-bootstrap/reporting-private.tar.gz \
  -C / etc/ai-media-analytics-report.env var/lib/ai-media-analytics-report
sudo chmod 600 /root/analytics-report-bootstrap/reporting-private.tar.gz
sudo systemctl start ai-media-analytics-report
```

При ошибке копирования перезапустите только reporting service и разберите ошибку, не заменяя существующий архив. После безопасного шифрования удалите временный незашифрованный архив. При восстановлении на отдельном окружении заранее проверьте, что целевые env/state отсутствуют; не извлекайте поверх рабочих данных. Установите тот же код, восстановите root:root 0600 для env и `analytics-report:analytics-report` 0700 для state, восстановите сеть/домен/callback и проверьте OAuth заново. Изолированная копия не должна использовать рабочие refresh tokens против production OAuth: для теста понадобится отдельный PostHog и новое подключение; перенесённое зашифрованное состояние можно проверить без сетевого обращения. Полное восстановление и token refresh в этом изменении **не испытывались**; их приёмка обязательна перед надёжной эксплуатацией.

Откат: приостановите облачную задачу, отключите/отзовите подключение PostHog OAuth, `sudo systemctl disable --now ai-media-analytics-report`, уберите только добавленный Caddy site из `.env`, пересоздайте только proxy закреплённой командой выше. Продуктовые тома не удаляйте. Созданные панели можно оставить для ручного просмотра.

## Локальная проверка подготовки

```powershell
.\.local-tools\report-venv\Scripts\python.exe -m pip install -r reporting/requirements.txt
.\.local-tools\report-venv\Scripts\python.exe -m unittest discover -s tests -v
.\.local-tools\report-venv\Scripts\python.exe -m reporting.setup_dashboards
git diff --check
```

Устанавливать зависимости нужно в отдельный venv, не в Python AI Media Client. Linux installer/systemd, реальный reverse proxy, выдача/refresh OAuth, выполнение HogQL, создание панелей и облачный запуск требуют живой проверки, локальные тесты их не заменяют.

Источники: [облачные и локальные автоматизации OpenAI](https://learn.chatgpt.com/docs/automations?surface=app), [custom MCP и OAuth](https://developers.openai.com/api/docs/guides/custom-mcp-server), [FastMCP OAuthProxy](https://gofastmcp.com/servers/auth/oauth-proxy), [PostHog Query API](https://posthog.com/docs/api/query). Upstream модели и схемы сверены с коммитом из `POSTHOG_VERSION`.
