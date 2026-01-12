"""
Custom middleware for CORS handling and access logging.
"""
import logging
from datetime import datetime

logger = logging.getLogger('app.middleware')


class AccessLogMiddleware:
    """记录访问者IP和其他信息的中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 跳过 favicon.ico 的日志记录
        if request.path == '/favicon.ico':
            response = self.get_response(request)
            return response

        # 处理请求
        response = self.get_response(request)

        # 跳过轮询请求的日志（GET /api/rooms/{room_id}）
        if request.method == 'GET' and request.path.startswith('/api/rooms/') and len(request.path.split('/')) == 4:
            return response

        # 只记录重要操作（POST/PUT/DELETE）和错误请求（4xx, 5xx）
        status_code = response.status_code
        should_log = (
            request.method in ['POST', 'PUT', 'DELETE', 'PATCH'] or
            status_code >= 400
        )

        if not should_log:
            return response

        # 获取客户端IP地址
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')

        # 获取其他信息
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        method = request.method
        path = request.path
        referer = request.META.get('HTTP_REFERER', '-')

        # 记录访问日志
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(
            f"[{timestamp}] {ip} - {method} {path} {status_code} - "
            f"User-Agent: {user_agent[:100]} - Referer: {referer}"
        )

        return response


class CorsMiddleware:
    """Simple CORS middleware for development."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-User-Fingerprint'
            response['Access-Control-Max-Age'] = '86400'
            return response

        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-User-Fingerprint'
        return response
