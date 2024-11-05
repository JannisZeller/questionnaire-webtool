from .auth import auth_bp
from .index import index_bp
from .signup import signup_bp
from .report import report_bp
from .account import account_bp
from .consent import consent_bp
from .user_reset import user_reset_bp
from .quest import quest_bp
from .htmx import htmx_bp

blueprints = [
    auth_bp,
    index_bp,
    report_bp,
    signup_bp,
    account_bp,
    consent_bp,
    user_reset_bp,
    quest_bp,
    htmx_bp,
]
