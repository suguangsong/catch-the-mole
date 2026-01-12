"""
WSGI config for catch-the-mole project.
"""

import os
import logging

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = get_wsgi_application()

# 初始化日志系统
logger = logging.getLogger('app')
logger.info('Django application initialized')
