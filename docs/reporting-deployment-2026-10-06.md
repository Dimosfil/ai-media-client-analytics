# Проверка reporting на VPS — 2026-10-06

## Развёрнуто

- VPS: `debianuser@195.209.221.217`; PostHog проект 1, Europe/Moscow.
- Исходники: `/opt/ai-media-analytics-report/reporting`; systemd: `ai-media-analytics-report.service`.
- Закрытые env/state: `/etc/ai-media-analytics-report.env` (root:root 0600), `/var/lib/ai-media-analytics-report` (analytics-report, 0700).
- MCP: `https://reports-195-209-221-217.sslip.io/mcp`; upstream внутри VPS: `172.17.0.1:8765`.
- [Product overview](https://analytics-195-209-221-217.sslip.io/project/1/dashboard/2).
- [Funnels and retention](https://analytics-195-209-221-217.sslip.io/project/1/dashboard/3).

Перенесены исходники reporting, analyticsctl и security overlay. Существующие файлы VPS сохранены перед обновлением. Постоянный RSA-ключ создан на VPS и передан web через env для native OAuth RS256. Пересозданы только web и proxy с `--no-build --pull never --no-deps`; образы и тома не обновлялись. Web вышел на health 200 примерно через 9–10 минут проверок миграций в штатном entrypoint.

Исправления, найденные при запуске: обязательный RS256/OIDC ключ; права чтения root-created venv для service user; допустимое значение `FASTMCP_CHECK_FOR_UPDATES=off` вместо `false`.

## Фактически проверено

- `python3 analyticsctl.py check-poc`: 38 digest-locked сервисов полной конфигурации, 17 в POC, публичные порты только proxy 80/443.
- `python -m reporting.check`: все шесть агрегатов и восемь источников графиков на живом Query API.
- `python -m reporting.setup_dashboards --apply` дважды: те же dashboard IDs 2/3, восемь insights, без дублей; принадлежность и сохранённые запросы проверены через API.
- `curl --fail https://analytics-195-209-221-217.sslip.io/_health`: 200 с VPS и внешнего компьютера.
- `curl --fail https://reports-195-209-221-217.sslip.io/.well-known/oauth-authorization-server`: 200 с VPS и внешнего компьютера.
- POST `/mcp` без Bearer: 401. TCP публичного IP:8765 с внешнего компьютера недоступен.
- `systemctl show ai-media-analytics-report -p ActiveState -p NRestarts -p MemoryCurrent`: active, 0 рестартов после исправления, около 91 МиБ.
- 17 локальных тестов; восемь reporting-тестов на Linux; `pip check` обеих сред и `bash -n reporting/install.sh` прошли.

Последний моментальный замер: RAM 3921 МиБ, доступно 894 МиБ; swap 1127/2047 МиБ; диск 87%, свободно 5,2 ГБ. Это ограниченный запас. В коротком vmstat не наблюдалось постоянного swap I/O; OOM за последние сутки не найден. Эти проверки не устанавливают причину прошлых зависаний браузера.

## Резервирование

Reporting был остановлен на время копирования env/state. Архив tar.gz создан в памяти и зашифрован Fernet; файлы `/root/analytics-report-bootstrap/reporting-20261006.enc` и `reporting-20261006.key` имеют 0600. Существующие цели не перезаписывались.

Расшифрованная копия извлечена через `tarfile.extractall(filter='data')` в новый каталог `/root/analytics-report-bootstrap/restore-check-20261006`. Содержимое env и каждого state-файла сравнено побайтно; восстановлены root:root 0600 для env и analytics-report с 0700/0600 для каталогов/файлов state. Служба снова запущена. Отдельная зашифрованная копия текущего PostHog `.env` с RSA-ключом: `posthog-env-20261006.enc`; decrypt round-trip совпал.

Это проверка файлов и прав в изолированном каталоге. Рабочие данные PostHog не восстанавливались. OAuth grant ещё отсутствует, поэтому восстановление действующих OAuth tokens, refresh и запуск восстановленной службы **не проверены**. Ключ шифрования и копии пока на одном VPS; независимое приватное хранилище не настроено. Для следующих копий и восстановления — раздел обслуживания в [runbook](scheduled-analytics.md).

## Ещё требуется

1. В веб ChatGPT открыть «Настройки → Плагины» и проверить доступный способ подключения собственного MCP; завершить OAuth лично с проектом 1.
2. Вызвать оба инструмента в облачном чате; подтвердить `complete=true`, затем зарегистрировать ежедневную задачу на 09:00 Europe/Moscow.
3. Проверить «Запустить сейчас», следующий запуск при выключенном ПК, refresh и сохранение авторизации после рестарта.
4. Просмотреть графики в UI. API-проверка запросов и объектов не заменяет визуальную приёмку.
5. Отозвать временный personal API key в PostHog: файлы с ним на компьютере и VPS удалены, сам ключ пока не отозван.

В этом этапе новые smoke/продуктовые события не отправлялись. Исходный репозиторий AI Media Client не изменялся. Облачная задача пока не создана и ежедневная доставка не подтверждена.
