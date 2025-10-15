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
    # Start with all logs, ordered by creation time
    logs_queryset = StatusLog.objects.all().order_by('-create_datetime')

    level_filter_str = request.GET.get('level')
    logger_filter = request.GET.get('logger')
    request_id_filter = request.GET.get('request_id')
    user_id_filter = request.GET.get('user_id')

    # Apply database-level filters first (level and logger are confirmed working)
    if level_filter_str:
        level_int = LOG_LEVEL_MAP.get(level_filter_str.upper())
        if level_int is not None:
            logs_queryset = logs_queryset.filter(level__gte=level_int)

    if logger_filter:
        logs_queryset = logs_queryset.filter(logger_name__icontains=logger_filter)

    if request_id_filter:
        # Assuming 'extra' content is serialized into the 'msg' field as a JSON string.
        # This performs a string containment check for the request_id within the msg field.
        logs_queryset = logs_queryset.filter(msg__icontains=f"'request_id': '{request_id_filter}'")

    if user_id_filter:
        # Assuming 'extra' content is serialized into the 'msg' field as a JSON string.
        # This performs a string containment check for the user_id within the msg field.
        logs_queryset = logs_queryset.filter(msg__icontains=f"'user_id': {user_id_filter}")
    
    logs = logs_queryset # Assign the filtered queryset to 'logs'

    context_logs = []
    for log in logs:
        context_logs.append({
            "id": log.id,
            "create_datetime": log.create_datetime,
            "level": REVERSE_LOG_LEVEL_MAP.get(log.level, str(log.level)),
            "logger_name": log.logger_name.strip(),
            "msg": log.msg,
            "trace": log.trace,
            "extra": getattr(log, 'extra', {}), 
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
        "current_request_id_filter": request_id_filter,
        "current_user_id_filter": user_id_filter,
        "available_levels": sorted(list(LOG_LEVEL_MAP.keys())),
        "available_loggers": available_loggers,
    }
    return render(request, 'LogViewer/log_list.html', context)



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
        "current_request_id_filter": request_id_filter,
        "current_user_id_filter": user_id_filter,
        "available_levels": sorted(list(LOG_LEVEL_MAP.keys())),
        "available_loggers": available_loggers,
    }
    return render(request, 'LogViewer/log_list.html', context)

