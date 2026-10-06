#!/bin/bash
# Install only the reporting service. Does not start it or change PostHog.
set -euo pipefail
umask 077
if [[ "$EUID" != 0 || "$#" != 1 ]]; then
    echo 'Usage: sudo bash reporting/install.sh /absolute/private/report.env' >&2
    exit 2
fi
[[ -f reporting/server.py && -f "$1" ]] || { echo 'Missing source or private env file' >&2; exit 1; }
config=/etc/ai-media-analytics-report.env
if [[ -e "$config" ]] && ! cmp -s "$1" "$config"; then
    echo 'Existing service config differs; refusing to overwrite secrets' >&2
    exit 1
fi
getent passwd analytics-report >/dev/null || useradd --system --no-create-home --shell /usr/sbin/nologin analytics-report
install -d -m 755 /opt/ai-media-analytics-report/reporting
install -d -o analytics-report -g analytics-report -m 700 /var/lib/ai-media-analytics-report
if [[ "$(readlink -f "$1")" != "$config" ]]; then
    install -m 600 "$1" "$config"
fi
install -m 644 reporting/*.py reporting/requirements.txt /opt/ai-media-analytics-report/reporting/
python3 -m venv /opt/ai-media-analytics-report/.venv
/opt/ai-media-analytics-report/.venv/bin/python -m pip install --disable-pip-version-check -r reporting/requirements.txt
# umask 077 protects credentials, but installed code must be readable by the service user.
chmod -R a+rX /opt/ai-media-analytics-report/.venv
install -m 644 reporting/ai-media-analytics-report.service /etc/systemd/system/ai-media-analytics-report.service
systemctl daemon-reload
echo 'Installed. Service is not started: configure private bind address, OAuth and HTTPS first.'
