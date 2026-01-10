"""
URL configuration for catch-the-mole project.
"""
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.http import FileResponse, HttpResponseRedirect, HttpResponse
import os
from pathlib import Path

def serve_index(request):
    """提供前端构建后的 index.html（用于 Vue Router 的客户端路由）"""
    try:
        index_path = Path(settings.BASE_DIR) / 'static' / 'index.html'
        if index_path.exists():
            try:
                with open(index_path, 'rb') as f:
                    content = f.read()
                response = HttpResponse(content, content_type='text/html')
                return response
            except Exception:
                # 如果读取文件失败，返回 Django 模板（开发环境）
                return TemplateView.as_view(template_name='index.html')(request)
        # 如果文件不存在，返回 Django 模板（开发环境）
        return TemplateView.as_view(template_name='index.html')(request)
    except Exception:
        # 如果所有操作都失败，返回一个简单的 HTML 页面，包含重定向脚本
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=/">
    <script>window.location.href = '/';</script>
</head>
<body>
    <p>正在跳转到首页...</p>
</body>
</html>
        '''
        return HttpResponse(html_content, content_type='text/html')

def redirect_room(request, room_id):
    """重定向房间路由到首页"""
    return HttpResponseRedirect('/')

urlpatterns = [
    # API 路由必须在前面，避免被前端路由拦截
    path('api/', include('app.api.urls')),
    # 房间路由直接重定向到首页
    path('room/<str:room_id>', redirect_room, name='room'),
    # 所有前端路由都返回 index.html，由 Vue Router 处理
    # 注意：这些路由不能匹配以 /api/ 开头的路径
    path('', serve_index, name='index'),
    path('create', serve_index, name='create'),
    path('join', serve_index, name='join'),
]

# 静态文件服务配置
# 在生产环境下，直接从 STATICFILES_DIRS 提供静态文件
# 因为前端构建产物已经复制到了 backend/static 目录
static_dirs = settings.STATICFILES_DIRS if hasattr(settings, 'STATICFILES_DIRS') else []
if not static_dirs:
    static_dirs = [Path(settings.BASE_DIR) / 'static']

for static_dir in static_dirs:
    static_path = Path(static_dir)
    if static_path.exists():
        urlpatterns += [
            path('static/<path:path>', static_serve, {'document_root': str(static_path)}),
        ]
