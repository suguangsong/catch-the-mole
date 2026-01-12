"""
API views for rooms and voting.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services import get_room_service, OpenDotaService
import uuid
import time
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class RoomCreateView(APIView):
    """创建房间接口"""

    def post(self, request):
        match_id = request.data.get('match_id')
        room_password = request.data.get('room_password')
        max_votes = request.data.get('max_votes', 5)
        votes_per_user = request.data.get('votes_per_user', 1)
        username = request.data.get('username')
        show_only_winner_votes = request.data.get('show_only_winner_votes', True)
        user_fingerprint = request.headers.get('X-User-Fingerprint')

        if not match_id:
            return Response({
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': '比赛ID不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not username:
            return Response({
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': '用户名不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user_fingerprint:
            return Response({
                'success': False,
                'error': 'UNAUTHORIZED',
                'message': '请提供用户指纹'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            match_id = int(match_id)
            max_votes = int(max_votes)
            votes_per_user = int(votes_per_user)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': '参数格式错误'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 房间ID使用时间戳生成
        room_id = str(int(time.time() * 1000))
        
        # 如果没有提供房间密码，自动生成
        if not room_password:
            room_password = str(uuid.uuid4())

        room_service = get_room_service()
        # 检查房间密码是否已被使用
        if room_service.room_exists_by_password(room_password):
            return Response({
                'success': False,
                'error': 'ROOM_PASSWORD_EXISTS',
                'message': '该房间密码已被使用，请更换房间密码'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            heroes = OpenDotaService().get_losing_team_heroes(match_id)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'INVALID_MATCH_ID',
                'message': f'无法获取比赛数据，请检查比赛ID是否正确'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = room_service.create_room(
                room_id=room_id,
                room_password=room_password,
                match_id=match_id,
                max_votes=max_votes,
                votes_per_user=votes_per_user,
                creator_username=username,
                creator_fingerprint=user_fingerprint,
                heroes=heroes,
                show_only_winner_votes=show_only_winner_votes
            )
        except Exception as e:
            return Response({
                'success': False,
                'error': 'CREATE_ROOM_ERROR',
                'message': f'创建房间失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 打印房间创建成功信息
        logger.info(
            f"房间创建成功 - 比赛ID: {room['match_id']}, "
            f"房间ID: {room['room_id']}, "
            f"房间密码: {room['room_password']}, "
            f"创建者: {room['creator_username']}, "
            f"最大投票人数: {room['max_votes']}, "
            f"每人票数: {room['votes_per_user']}, "
            f"状态: {room['status']}, "
            f"只展示内鬼得票: {room.get('show_only_winner_votes', True)}, "
            f"英雄数量: {len(room['heroes']) if room.get('heroes') else 0}"
        )

        return Response({
            'success': True,
            'data': {
                'room_id': room['room_id'],
                'room_password': room['room_password'],
                'match_id': room['match_id'],
                'status': room['status'],
                'max_votes': room['max_votes'],
                'votes_per_user': room['votes_per_user'],
                'creator_username': room['creator_username'],
                'heroes': room['heroes'],
                'show_only_winner_votes': room.get('show_only_winner_votes', True)
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class RoomDetailView(APIView):
    """获取房间信息接口"""

    def get(self, request, room_id):
        try:
            user_fingerprint = request.headers.get('X-User-Fingerprint')
            room_service = get_room_service()

            # 通过房间密码查找房间
            room = room_service.get_room_by_password(room_id)
            if not room:
                return Response({
                    'success': False,
                    'error': 'ROOM_NOT_FOUND',
                    'message': '房间不存在'
                }, status=status.HTTP_404_NOT_FOUND)

            response_data = {
                'room_id': room.get('room_id', ''),
                'room_password': room.get('room_password', ''),
                'match_id': room.get('match_id', 0),
                'status': room.get('status', 'init'),
                'max_votes': room.get('max_votes', 5),
                'votes_per_user': room.get('votes_per_user', 1),
                'current_votes': room.get('current_votes', 0),
                'creator_username': room.get('creator_username', ''),
                'creator_fingerprint': room.get('creator_fingerprint', ''),
                'heroes': room.get('heroes', []),
                'show_only_winner_votes': room.get('show_only_winner_votes', True),
                'player_order': room.get('player_order'),
                'order_generation_count': room.get('order_generation_count', 0)
            }

            room_status = room.get('status', 'init')
            if room_status == 'finished':
                response_data['votes'] = room.get('votes', {})
            else:
                # init 和 voting 状态都返回用户投票信息
                if user_fingerprint:
                    try:
                        user_voted_players = room_service.get_user_voted_players(room['room_id'], user_fingerprint)
                        if user_voted_players is not None:
                            response_data['user_voted_players'] = user_voted_players
                        # 检查用户是否已开始投票
                        user_started = room_service.has_user_started_voting(room['room_id'], user_fingerprint)
                        response_data['user_started_voting'] = user_started
                    except Exception:
                        pass
                try:
                    voted_usernames = room_service.get_voted_usernames(room['room_id'])
                    response_data['voted_usernames'] = voted_usernames
                except Exception:
                    response_data['voted_usernames'] = []

            return Response({
                'success': True,
                'data': response_data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': 'SERVER_ERROR',
                'message': f'获取房间信息失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class RoomStartView(APIView):
    """开始投票接口"""

    def post(self, request, room_id):
        user_fingerprint = request.headers.get('X-User-Fingerprint')

        if not user_fingerprint:
            return Response({
                'success': False,
                'error': 'UNAUTHORIZED',
                'message': '请提供用户指纹'
            }, status=status.HTTP_401_UNAUTHORIZED)

        room_service = get_room_service()

        # 通过房间密码查找房间
        room = room_service.get_room_by_password(room_id)
        if not room:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            actual_room_id = room['room_id']
        except KeyError:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if room['status'] == 'finished':
            return Response({
                'success': False,
                'error': 'ROOM_FINISHED',
                'message': '投票已结束'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 标记当前用户已开始投票（用户级别，不影响房间状态）
        room_service.start_user_voting(actual_room_id, user_fingerprint)

        return Response({
            'success': True,
            'data': {
                'message': '投票已开始'
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class RoomVoteView(APIView):
    """提交投票接口"""

    def post(self, request, room_id):
        user_fingerprint = request.headers.get('X-User-Fingerprint')
        username = request.data.get('username', '')
        player_index = request.data.get('player_index')

        if not user_fingerprint:
            return Response({
                'success': False,
                'error': 'UNAUTHORIZED',
                'message': '请提供用户指纹'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not player_index:
            return Response({
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': '玩家索引不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            player_index = int(player_index)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'INVALID_PLAYER_INDEX',
                'message': '玩家索引必须在 1-5 范围内'
            }, status=status.HTTP_400_BAD_REQUEST)

        if player_index < 1 or player_index > 5:
            return Response({
                'success': False,
                'error': 'INVALID_PLAYER_INDEX',
                'message': '玩家索引必须在 1-5 范围内'
            }, status=status.HTTP_400_BAD_REQUEST)

        room_service = get_room_service()

        # 通过房间密码查找房间
        room = room_service.get_room_by_password(room_id)
        if not room:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            actual_room_id = room['room_id']
        except KeyError:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if room['status'] == 'finished':
            return Response({
                'success': False,
                'error': 'ROOM_FINISHED',
                'message': '投票已结束'
            }, status=status.HTTP_400_BAD_REQUEST)

        result = room_service.vote(actual_room_id, user_fingerprint, player_index, username)

        if not result['success']:
            return Response({
                'success': False,
                'error': result['error'],
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'message': result['message'],
            'finished': result['finished'],
            'current_votes': result['current_votes'],
            'max_votes': result['max_votes'],
            'user_voted_players': result['user_voted_players'],
            'user_remaining_votes': result['user_remaining_votes']
        }

        return Response({
            'success': True,
            'data': response_data
        })


@method_decorator(csrf_exempt, name='dispatch')
class RoomResetView(APIView):
    """重置投票接口"""

    def post(self, request, room_id):
        user_fingerprint = request.headers.get('X-User-Fingerprint')

        if not user_fingerprint:
            return Response({
                'success': False,
                'error': 'UNAUTHORIZED',
                'message': '请提供用户指纹'
            }, status=status.HTTP_401_UNAUTHORIZED)

        room_service = get_room_service()

        # 通过房间密码查找房间
        room = room_service.get_room_by_password(room_id)
        if not room:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            actual_room_id = room['room_id']
        except KeyError:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        result = room_service.reset_voting(actual_room_id, user_fingerprint)

        if not result['success']:
            status_code = status.HTTP_400_BAD_REQUEST
            if result['error'] == 'UNAUTHORIZED':
                status_code = status.HTTP_403_FORBIDDEN
            elif result['error'] == 'ROOM_NOT_FOUND':
                status_code = status.HTTP_404_NOT_FOUND
            return Response({
                'success': False,
                'error': result['error'],
                'message': result['message']
            }, status=status_code)

        return Response({
            'success': True,
            'data': {
                'message': result['message']
            }
        })

@method_decorator(csrf_exempt, name='dispatch')
class RoomGenerateOrderView(APIView):
    """生成随机玩家排序接口"""

    def post(self, request, room_id):
        user_fingerprint = request.headers.get('X-User-Fingerprint')

        if not user_fingerprint:
            return Response({
                'success': False,
                'error': 'UNAUTHORIZED',
                'message': '请提供用户指纹'
            }, status=status.HTTP_401_UNAUTHORIZED)

        room_service = get_room_service()

        # 通过房间密码查找房间
        room = room_service.get_room_by_password(room_id)
        if not room:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            actual_room_id = room['room_id']
        except KeyError:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        result = room_service.generate_player_order(actual_room_id, user_fingerprint)

        if not result['success']:
            status_code = status.HTTP_400_BAD_REQUEST
            if result['error'] == 'UNAUTHORIZED':
                status_code = status.HTTP_403_FORBIDDEN
            elif result['error'] == 'ROOM_NOT_FOUND':
                status_code = status.HTTP_404_NOT_FOUND
            return Response({
                'success': False,
                'error': result['error'],
                'message': result['message']
            }, status=status_code)

        return Response({
            'success': True,
            'data': {
                'message': result['message'],
                'order': result['order']
            }
        })
