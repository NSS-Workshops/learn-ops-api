from django.shortcuts import render
from django_db_logger.models import StatusLog
import logging

LOG_LEVEL_MAP = {
    'NOTSET': logging.NOTSET,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
}
REVERSE_LOG_LEVEL_MAP = {v: k for k, v in LOG_LEVEL_MAP.items()}


def log_list(request):
    logs = StatusLog.objects.all().order_by('-create_datetime')

    level_filter_str = request.GET.get('level')
    logger_filter = request.GET.get('logger')

    if level_filter_str:
        level_int = LOG_LEVEL_MAP.get(level_filter_str.upper())
        if level_int is not None:
            logs = logs.filter(level__gte=level_int)

    if logger_filter:
        logs = logs.filter(logger_name__icontains=logger_filter)

    context_logs = []
    for log in logs:
        context_logs.append({
            "id": log.id,
            "create_datetime": log.create_datetime,
            "level": REVERSE_LOG_LEVEL_MAP.get(log.level, str(log.level)),
            "logger_name": log.logger_name.strip(),
            "msg": log.msg,
            "trace": log.trace,
        })

    # ✅ Ensure logger dropdown has only unique, cleaned names
    available_loggers = (
        StatusLog.objects.values_list("logger_name", flat=True)
        .distinct()
    )
    available_loggers = sorted(set(name.strip() for name in available_loggers if name))

    context = {
        "message": "Recent Logs",
        "logs": context_logs,
        "current_level_filter": level_filter_str,
        "current_logger_filter": logger_filter,
        "available_levels": sorted(list(LOG_LEVEL_MAP.keys())),
        "available_loggers": available_loggers,
    }
    return render(request, 'LogViewer/log_list.html', context)

