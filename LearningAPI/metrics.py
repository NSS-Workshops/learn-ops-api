from prometheus_client import Counter, Histogram, Gauge

# Example Counter: Tracks the total number of API requests
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint'] # Labels for method (GET, POST, etc.) and endpoint
)

# Example Histogram: Tracks the duration of API requests
api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'Histogram of API request durations',
    ['method', 'endpoint']
)

# Example Gauge: Tracks the number of active users
active_users = Gauge(
    'active_users',
    'Number of currently active users'
)

# Counter for user logins
user_login_total = Counter(
    'user_login_total',
    'Total number of user logins'
)

# Custom Counter: Tracks the total number of course views
course_views_total = Counter(
    'course_views_total',
    'Total number of course views',
    ['type', 'course_id'] # Labels for view type (list/detail) and course ID
)