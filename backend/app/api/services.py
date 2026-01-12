"""
Business logic services.
"""
import uuid
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import requests
import threading


class RoomService:
    """房间管理服务（单例模式）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(RoomService, cls).__new__(cls)
                    cls._instance._rooms: Dict[str, Dict] = {}
                    cls._instance._room_lock = threading.Lock()
        return cls._instance

    def room_exists(self, room_id: str) -> bool:
        """检查房间是否存在"""
        with self._room_lock:
            return room_id in self._rooms

    def room_exists_by_password(self, room_password: str) -> bool:
        """通过密码检查房间是否存在"""
        with self._room_lock:
            for room in self._rooms.values():
                if room.get('room_password') == room_password:
                    return True
            return False

    def get_room_by_password(self, room_password: str) -> Optional[Dict]:
        """通过密码获取房间信息"""
        with self._room_lock:
            for room in self._rooms.values():
                if room.get('room_password') == room_password:
                    room_copy = room.copy()
                    # 确保 voted_users 字段存在
                    if 'voted_users' not in room_copy:
                        room_copy['voted_users'] = {}
                    room_copy['current_votes'] = len(room_copy.get('voted_users', {}))
                    return room_copy
            return None

    def get_room_status(self, room_id: str) -> Optional[str]:
        """获取房间状态"""
        with self._room_lock:
            if room_id not in self._rooms:
                return None
            return self._rooms[room_id]['status']

    def create_room(
        self,
        room_id: str,
        room_password: str,
        match_id: int,
        max_votes: int,
        votes_per_user: int,
        creator_username: str,
        creator_fingerprint: str,
        heroes: List[Dict],
        show_only_winner_votes: bool = True
    ) -> Dict:
        """创建房间"""
        with self._room_lock:
            room = {
                'room_id': room_id,
                'room_password': room_password,
                'match_id': match_id,
                'max_votes': max_votes,
                'votes_per_user': votes_per_user,
                'status': 'init',
                'created_at': datetime.now(),
                'creator_username': creator_username,
                'creator_fingerprint': creator_fingerprint,
                'heroes': heroes,
                'votes': {},
                'voted_users': {},
                'show_only_winner_votes': show_only_winner_votes
            }
            self._rooms[room_id] = room
            return room

    def get_room(self, room_id: str) -> Dict:
        """获取房间信息"""
        with self._room_lock:
            if room_id not in self._rooms:
                raise KeyError(f'房间不存在: {room_id}')
            room = self._rooms[room_id].copy()
            # 确保 voted_users 字段存在
            if 'voted_users' not in room:
                room['voted_users'] = {}
            room['current_votes'] = len(room.get('voted_users', {}))
            return room

    def start_voting(self, room_id: str):
        """开始投票（房间级别，已废弃，保留用于兼容）"""
        with self._room_lock:
            self._rooms[room_id]['status'] = 'voting'

    def start_user_voting(self, room_id: str, user_fingerprint: str):
        """用户开始投票（用户级别）"""
        with self._room_lock:
            room = self._rooms[room_id]
            if 'voted_users' not in room:
                room['voted_users'] = {}
            if user_fingerprint not in room['voted_users']:
                room['voted_users'][user_fingerprint] = {
                    'vote_count': 0,
                    'voted_players': [],
                    'started': True
                }
            else:
                room['voted_users'][user_fingerprint]['started'] = True

    def has_user_started_voting(self, room_id: str, user_fingerprint: str) -> bool:
        """检查用户是否已开始投票"""
        with self._room_lock:
            if room_id not in self._rooms:
                return False
            room = self._rooms[room_id]
            if 'voted_users' not in room:
                return False
            if user_fingerprint not in room['voted_users']:
                return False
            return room['voted_users'][user_fingerprint].get('started', False)

    def vote(self, room_id: str, user_fingerprint: str, player_index: int, username: str = None) -> Dict:
        """提交投票"""
        with self._room_lock:
            room = self._rooms[room_id]

            if user_fingerprint not in room['voted_users']:
                room['voted_users'][user_fingerprint] = {
                    'vote_count': 0,
                    'voted_players': [],
                    'username': username,
                    'started': False
                }
            elif username and not room['voted_users'][user_fingerprint].get('username'):
                room['voted_users'][user_fingerprint]['username'] = username

            # 检查用户是否已开始投票
            if not room['voted_users'][user_fingerprint].get('started', False):
                return {
                    'success': False,
                    'error': 'VOTING_NOT_STARTED',
                    'message': '请先点击开始投票'
                }

            user_vote_info = room['voted_users'][user_fingerprint]

            if user_vote_info['vote_count'] >= room['votes_per_user']:
                return {
                    'success': False,
                    'error': 'ALREADY_VOTED',
                    'message': '你已完成所有投票'
                }

            if player_index in user_vote_info['voted_players']:
                return {
                    'success': False,
                    'error': 'DUPLICATE_VOTE',
                    'message': '不能重复投票给同一玩家'
                }

            player_key = str(player_index)
            if player_key not in room['votes']:
                room['votes'][player_key] = 0

            room['votes'][player_key] += 1
            user_vote_info['vote_count'] += 1
            user_vote_info['voted_players'].append(player_index)

            current_votes = len(room['voted_users'])
            # 判断投票是否结束：需要同时满足两个条件
            # 1. 已投票用户数达到最大投票人数
            # 2. 所有已投票的用户都完成了他们的所有投票
            finished = False
            if current_votes >= room['max_votes']:
                # 检查所有已投票的用户是否都完成了所有投票
                all_users_completed = True
                for user_info in room['voted_users'].values():
                    if user_info['vote_count'] < room['votes_per_user']:
                        all_users_completed = False
                        break
                finished = all_users_completed

            if finished:
                room['status'] = 'finished'

            user_remaining_votes = room['votes_per_user'] - user_vote_info['vote_count']

            message = '投票成功'
            if finished:
                message = '投票成功，投票已结束'
            elif user_remaining_votes > 0:
                message = f'投票成功，还需投 {user_remaining_votes} 票'

            return {
                'success': True,
                'message': message,
                'finished': finished,
                'current_votes': current_votes,
                'max_votes': room['max_votes'],
                'user_voted_players': user_vote_info['voted_players'].copy(),
                'user_remaining_votes': user_remaining_votes
            }

    def get_user_voted_players(self, room_id: str, user_fingerprint: str) -> Optional[List[int]]:
        """获取用户已投票的玩家列表"""
        with self._room_lock:
            if room_id not in self._rooms:
                return None

            room = self._rooms[room_id]
            if user_fingerprint not in room['voted_users']:
                return []

            return room['voted_users'][user_fingerprint]['voted_players'].copy()

    def get_voted_usernames(self, room_id: str) -> List[str]:
        """获取已投票用户的用户名列表"""
        with self._room_lock:
            if room_id not in self._rooms:
                return []

            room = self._rooms[room_id]
            usernames = []
            for user_info in room['voted_users'].values():
                username = user_info.get('username')
                if username:
                    usernames.append(username)
            return usernames

    def reset_voting(self, room_id: str, creator_fingerprint: str) -> Dict:
        """重置投票状态（只有房主可以操作）"""
        with self._room_lock:
            if room_id not in self._rooms:
                return {
                    'success': False,
                    'error': 'ROOM_NOT_FOUND',
                    'message': '房间不存在'
                }

            room = self._rooms[room_id]

            # 验证是否为房主
            if room.get('creator_fingerprint') != creator_fingerprint:
                return {
                    'success': False,
                    'error': 'UNAUTHORIZED',
                    'message': '只有房主可以重置投票'
                }

            # 重置投票状态
            room['status'] = 'init'
            room['votes'] = {}
            room['voted_users'] = {}

            return {
                'success': True,
                'message': '投票已重置'
            }

    @property
    def current_votes(self) -> int:
        """获取当前已投票人数（用于房间信息）"""
        # 这个方法在get_room中计算
        pass


def get_room_service() -> RoomService:
    """获取房间服务单例"""
    return RoomService()


class OpenDotaService:
    """OpenDota API服务"""

    BASE_URL = 'https://api.opendota.com/api'
    _heroes_data = None
    _heroes_lock = threading.Lock()

    def __init__(self):
        """初始化时加载英雄配置文件"""
        if OpenDotaService._heroes_data is None:
            with OpenDotaService._heroes_lock:
                if OpenDotaService._heroes_data is None:
                    self._load_heroes_config()

    def _load_heroes_config(self):
        """从配置文件加载英雄数据"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'heroes.json'
        )
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                heroes_list = json.load(f)
                OpenDotaService._heroes_data = {hero['id']: hero for hero in heroes_list}
        except FileNotFoundError:
            raise FileNotFoundError(f'英雄配置文件未找到: {config_path}')
        except json.JSONDecodeError as e:
            raise ValueError(f'英雄配置文件格式错误: {e}')

    def get_match_data(self, match_id: int) -> Dict:
        """获取比赛数据"""
        url = f'{self.BASE_URL}/matches/{match_id}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_heroes(self) -> List[Dict]:
        """获取英雄列表（从配置文件读取）"""
        if OpenDotaService._heroes_data is None:
            self._load_heroes_config()
        return list(OpenDotaService._heroes_data.values())

    def get_hero_by_id(self, hero_id: int) -> Optional[Dict]:
        """根据hero_id获取英雄信息"""
        if OpenDotaService._heroes_data is None:
            self._load_heroes_config()
        return OpenDotaService._heroes_data.get(hero_id)

    def get_losing_team_heroes(self, match_id: int) -> List[Dict]:
        """获取失败方的玩家和英雄信息"""
        match_data = self.get_match_data(match_id)

        players = match_data.get('players', [])
        radiant_win = match_data.get('radiant_win', False)

        losing_team_players = []
        for player in players:
            is_radiant = player.get('isRadiant', False)
            if (radiant_win and not is_radiant) or (not radiant_win and is_radiant):
                hero_id = player.get('hero_id')
                hero_info = self.get_hero_by_id(hero_id)
                if hero_info:
                    hero_name = hero_info.get('name_cn') or hero_info.get('name_en', f'Hero {hero_id}')
                else:
                    hero_name = f'Hero {hero_id}'
                nickname = player.get('personaname', 'Unknown')

                losing_team_players.append({
                    'player_slot': player.get('player_slot', 0),
                    'hero_id': hero_id,
                    'hero_name': hero_name,
                    'nickname': nickname
                })

        if len(losing_team_players) != 5:
            raise ValueError(f'失败方玩家数量不正确，期望5人，实际{len(losing_team_players)}人')

        return losing_team_players
