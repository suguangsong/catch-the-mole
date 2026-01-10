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


@method_decorator(csrf_exempt, name='dispatch')
class RoomCreateView(APIView):
    """创建房间接口"""

    def post(self, request):
        match_id = request.data.get('match_id')
        room_id = request.data.get('room_id')
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

        if not room_id:
            room_id = str(uuid.uuid4())

        room_service = get_room_service()
        # 检查房间是否已存在
        if room_service.room_exists(room_id):
            existing_status = room_service.get_room_status(room_id)
            # 如果房间状态是 voting 或 finished，不允许覆盖
            if existing_status in ['voting', 'finished']:
                return Response({
                    'success': False,
                    'error': 'ROOM_ALREADY_EXISTS',
                    'message': '该房间 ID 已被使用，请更换房间 ID'
                }, status=status.HTTP_400_BAD_REQUEST)
            # 如果房间状态是 init，检查是否是同一个创建者
            elif existing_status == 'init':
                try:
                    existing_room = room_service.get_room(room_id)
                    if existing_room.get('creator_fingerprint') != user_fingerprint:
                        return Response({
                            'success': False,
                            'error': 'ROOM_ALREADY_EXISTS',
                            'message': '该房间 ID 已被使用，请更换房间 ID'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    # 如果是同一个创建者，允许重新创建（覆盖）
                except KeyError:
                    # 房间在检查过程中被删除，允许创建
                    pass

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

        return Response({
            'success': True,
            'data': {
                'room_id': room['room_id'],
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

            if not room_service.room_exists(room_id):
                return Response({
                    'success': False,
                    'error': 'ROOM_NOT_FOUND',
                    'message': '房间不存在'
                }, status=status.HTTP_404_NOT_FOUND)

            try:
                room = room_service.get_room(room_id)
            except KeyError:
                return Response({
                    'success': False,
                    'error': 'ROOM_NOT_FOUND',
                    'message': '房间不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                import traceback
                return Response({
                    'success': False,
                    'error': 'SERVER_ERROR',
                    'message': f'获取房间信息失败: {str(e)}',
                    'traceback': traceback.format_exc() if hasattr(traceback, 'format_exc') else ''
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            response_data = {
                'room_id': room.get('room_id', ''),
                'match_id': room.get('match_id', 0),
                'status': room.get('status', 'init'),
                'max_votes': room.get('max_votes', 5),
                'votes_per_user': room.get('votes_per_user', 1),
                'current_votes': room.get('current_votes', 0),
                'creator_username': room.get('creator_username', ''),
                'creator_fingerprint': room.get('creator_fingerprint', ''),
                'heroes': room.get('heroes', []),
                'show_only_winner_votes': room.get('show_only_winner_votes', True)
            }

            room_status = room.get('status', 'init')
            if room_status == 'finished':
                response_data['votes'] = room.get('votes', {})
            elif room_status == 'voting':
                if user_fingerprint:
                    try:
                        user_voted_players = room_service.get_user_voted_players(room_id, user_fingerprint)
                        if user_voted_players is not None:
                            response_data['user_voted_players'] = user_voted_players
                    except Exception:
                        pass
                try:
                    voted_usernames = room_service.get_voted_usernames(room_id)
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

        if not room_service.room_exists(room_id):
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            room = room_service.get_room(room_id)
        except KeyError:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if room['creator_fingerprint'] != user_fingerprint:
            return Response({
                'success': False,
                'error': 'PERMISSION_DENIED',
                'message': '只有房间创建者可以开始投票'
            }, status=status.HTTP_403_FORBIDDEN)

        if room['status'] == 'voting':
            return Response({
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': '投票已开始，无需重复操作'
            }, status=status.HTTP_400_BAD_REQUEST)

        if room['status'] == 'finished':
            return Response({
                'success': False,
                'error': 'ROOM_FINISHED',
                'message': '投票已结束'
            }, status=status.HTTP_400_BAD_REQUEST)

        room_service.start_voting(room_id)

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

        if not room_service.room_exists(room_id):
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            room = room_service.get_room(room_id)
        except KeyError:
            return Response({
                'success': False,
                'error': 'ROOM_NOT_FOUND',
                'message': '房间不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        if room['status'] == 'init':
            return Response({
                'success': False,
                'error': 'VOTING_NOT_STARTED',
                'message': '投票尚未开始'
            }, status=status.HTTP_400_BAD_REQUEST)

        if room['status'] == 'finished':
            return Response({
                'success': False,
                'error': 'ROOM_FINISHED',
                'message': '投票已结束'
            }, status=status.HTTP_400_BAD_REQUEST)

        result = room_service.vote(room_id, user_fingerprint, player_index, username)

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
