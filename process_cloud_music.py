import json
import os
import random
import re
import time
import urllib.parse
from typing import Dict, Any

import requests
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, COMM, TYER
from mutagen.mp4 import MP4, MP4Cover

from logging_config import setup_logger

# 创建日志记录器
logger = setup_logger(__name__)


class NeteaseMusicToolAPI:
    """
    Netease Music API Client
    """

    def __init__(self, base_url: str = "https://musicapi.lxchen.cn"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # 设置浏览器模拟请求头（排除HTTP/2伪头部）
        self.session.headers.update({
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://musicapi.lxchen.cn',
            'priority': 'u=1, i',
            'referer': 'https://musicapi.lxchen.cn/',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        })

    def _extract_id(self, text: str, pattern_type: str = 'song') -> str:
        """Extract ID from URL or text"""
        text = str(text) if text is not None else ""
        if not text:
            return text

        patterns = {
            'song': r'song\?id=(\d+)',
            'playlist': r'playlist\?id=(\d+)',
            'album': r'album\?id=(\d+)'
        }

        if 'music.163.com' in text or '163cn.tv' in text:
            pattern = patterns.get(pattern_type, r'id=(\d+)')
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        if text.isdigit():
            return text

        return text

    # ==================== 1. 搜索功能 ====================

    def search(self, keyword: str, limit: int = 10) -> str:
        """Search songs"""

        random_sleep(5.0)
        response = self.session.post(
            f"{self.base_url}/Search",
            data={'keyword': keyword, 'limit': limit}
        )
        return response.text

    # ==================== 2. 单曲解析 ====================

    def parse_song(self, song_id_or_url: str, level: str = "lossless") -> str:
        """Parse song details"""
        song_id = self._extract_id(song_id_or_url, 'song')

        random_sleep(5.0)
        response = self.session.post(
            f"{self.base_url}/Song_V1",
            data={'url': song_id, 'level': level, 'type': 'json'}
        )
        return response.text

    # ==================== 3. 歌单解析 ====================

    def parse_playlist(self, playlist_id_or_url: str) -> str:
        """Parse playlist details"""
        playlist_id = self._extract_id(playlist_id_or_url, 'playlist')

        random_sleep(5.0)
        response = self.session.get(
            f"{self.base_url}/Playlist",
            params={'id': playlist_id}
        )
        logger.info("-" * 60)
        return response.text

    # ==================== 4. 专辑解析 ====================

    def parse_album(self, album_id_or_url: str) -> str:
        """Parse album details"""
        album_id = self._extract_id(album_id_or_url, 'album')

        random_sleep(5.0)
        response = self.session.get(
            f"{self.base_url}/Album",
            params={'id': album_id}
        )
        return response.text


# ==================== 使用示例 ====================

# 定义音质等级列表
quality_levels = ["lossless", "exhigh", "standard"]


def random_sleep(max_delay: float = 2.0):
    """Random delay to avoid frequent requests"""
    delay = random.uniform(0.5, max_delay)
    logger.info(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)


def get_song_ids_by_playlist_id(playlist_id: str) -> Dict[str, Any]:
    """
    通过歌单ID提取歌单中所有歌曲的ID列表

    Args:
        playlist_id: 歌单ID(例如: "70512345")

    Returns:
        包含歌单信息和歌曲ID列表的字典
    """
    api = NeteaseMusicToolAPI("https://musicapi.lxchen.cn")

    logger.info("=" * 60)
    logger.info("🎵 通过歌单ID提取歌曲列表")
    logger.info("=" * 60)
    logger.info(f"歌单ID: {playlist_id}")
    logger.info("-" * 60)

    # 调用歌单解析接口
    playlist_result_str = api.parse_playlist(playlist_id)

    try:
        playlist_result = json.loads(playlist_result_str)

        if playlist_result.get('status') != 200:
            logger.error(f"\n❌ 歌单解析失败: {playlist_result.get('message', '未知错误')}")
            return {
                "success": False,
                "message": playlist_result.get('message', '歌单解析失败'),
                "playlist_id": playlist_id
            }

        # 提取歌单数据
        data_section = playlist_result.get('data', {})
        if not data_section:
            logger.error(f"\n 未找到数据部分")
            return {"success": False, "message": "未找到数据部分", "playlist_id": playlist_id}

        playlist_info = data_section.get('playlist', {})
        if not playlist_info:
            logger.error(f"\n 未找到歌单信息")
            return {"success": False, "message": "未找到歌单信息", "playlist_id": playlist_id}

        playlist_name = playlist_info.get('name', '未知歌单')
        playlist_creator = playlist_info.get('creator', '未知创建者')
        track_count = playlist_info.get('trackCount', 0)
        song_list = playlist_info.get('tracks', [])

        # 调试信息
        print(f"DEBUG: 原始数据键: {list(data_section.keys())}")
        print(f"DEBUG: playlist键: {list(playlist_info.keys())}")
        print(f"DEBUG: 歌单名称字段值: {playlist_name}")
        print(f"DEBUG: 创建者字段值: {playlist_creator}")
        print(f"DEBUG: 歌曲列表长度: {len(song_list)}")
        print(f"DEBUG: trackCount字段值: {track_count}")

        logger.info(f"\n✅ 歌单解析成功!")
        logger.info(f"📋 歌单名称: {playlist_name}")
        logger.info(f"👤 创建者: {playlist_creator}")
        logger.info(f"🎵 歌曲数量: {len(song_list)}")
        logger.info("-" * 60)

        # 提取所有歌曲ID
        song_ids = []
        song_details = []

        for i, song in enumerate(song_list, 1):
            song_id = song.get('id')
            song_name = song.get('name', '未知歌曲')
            # 处理歌手信息
            song_artists = song.get('artists', '未知艺术家')

            if song_id:
                song_ids.append(str(song_id))
                song_details.append({
                    "id": str(song_id),
                    "name": song_name,
                    "artists": song_artists,
                    "index": i
                })
                logger.info(f"{i:2d}. [{song_id}] {song_name} - {song_artists}")
            else:
                logger.warning(f"{i:2d}. ⚠️  无效歌曲数据: {song}")

        result = {
            "success": True,
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "playlist_creator": playlist_creator,
            "song_count": len(song_ids),
            "song_ids": song_ids,
            "song_details": song_details,
            "raw_data": playlist_result
        }

        logger.info(f"\n✅ 成功提取 {len(song_ids)} 首歌曲的ID")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"\n❌ JSON解析失败: {str(e)}")
        return {"success": False, "message": f"JSON解析失败: {str(e)}", "playlist_id": playlist_id}
    except Exception as e:
        logger.error(f"\n❌ 处理过程中发生错误: {str(e)}")
        return {"success": False, "message": f"处理失败: {str(e)}", "playlist_id": playlist_id}


def get_song_ids_by_album_id(album_id: str) -> Dict[str, Any]:
    """
    通过专辑ID提取专辑中所有歌曲的ID列表

    Args:
        album_id: 专辑ID(例如: "361790100")

    Returns:
        包含专辑信息和歌曲ID列表的字典
    """
    api = NeteaseMusicToolAPI("https://musicapi.lxchen.cn")

    logger.info("=" * 60)
    logger.info("🎵 通过专辑ID提取歌曲列表")
    logger.info("=" * 60)
    logger.info(f"专辑ID: {album_id}")
    logger.info("-" * 60)

    # 调用专辑解析接口
    album_result_str = api.parse_album(album_id)

    try:
        album_result = json.loads(album_result_str)

        if album_result.get('status') != 200:
            logger.error(f"\n❌ 专辑解析失败: {album_result.get('message', '未知错误')}")
            return {
                "success": False,
                "message": album_result.get('message', '专辑解析失败'),
                "album_id": album_id
            }

        # 提取专辑数据
        album_data = album_result.get('data', {}).get('album', {})
        if not album_data:
            logger.error(f"\n❌ 未找到专辑数据")
            return {"success": False, "message": "未找到专辑数据", "album_id": album_id}

        album_name = album_data.get('name', '未知专辑')
        album_artist = album_data.get('artist', '未知艺术家')
        song_list = album_data.get('songs', [])

        logger.info(f"\n✅ 专辑解析成功!")
        logger.info(f"💿 专辑名称: {album_name}")
        logger.info(f"🎤 艺术家: {album_artist}")
        logger.info(f"🎵 歌曲数量: {len(song_list)}")
        logger.info("-" * 60)

        # 提取所有歌曲ID
        song_ids = []
        song_details = []

        for i, song in enumerate(song_list, 1):
            song_id = song.get('id')
            song_name = song.get('name', '未知歌曲')
            song_artists = song.get('artists', '未知艺术家')

            if song_id:
                song_ids.append(str(song_id))
                song_details.append({
                    "id": str(song_id),
                    "name": song_name,
                    "artists": song_artists,
                    "index": i
                })
                logger.info(f"{i:2d}. [{song_id}] {song_name} - {song_artists}")
            else:
                logger.warning(f"{i:2d}. ⚠️  无效歌曲数据: {song}")

        result = {
            "success": True,
            "album_id": album_id,
            "album_name": album_name,
            "album_artist": album_artist,
            "song_count": len(song_ids),
            "song_ids": song_ids,
            "song_details": song_details,
            "raw_data": album_result
        }

        logger.info(f"\n✅ 成功提取 {len(song_ids)} 首歌曲的ID")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"\n❌ JSON解析失败: {str(e)}")
        return {"success": False, "message": f"JSON解析失败: {str(e)}", "album_id": album_id}
    except Exception as e:
        logger.error(f"\n❌ 处理过程中发生错误: {str(e)}")
        return {"success": False, "message": f"处理失败: {str(e)}", "album_id": album_id}


def get_song_metadata_by_song_id(song_id: str, level: str = "lossless") -> Dict[str, Any]:
    """
    通过歌曲ID提取歌曲信息

    Args:
        song_id: 歌曲ID(例如: "186016")
        level: 音质等级 (standard, exhigh, lossless, hires)

    Returns:
        包含歌曲详细信息的字典，包含下载链接
    """
    try:
        api = NeteaseMusicToolAPI("https://musicapi.lxchen.cn")

        logger.info("=" * 60)
        logger.info("🎵 通过歌曲ID提取信息")
        logger.info("=" * 60)
        logger.info(f"歌曲ID: {song_id}")
        logger.info(f"音质等级: {level}")
        logger.info("-" * 60)

        result = None
        used_level = None

        # 尝试不同音质等级
        for qual in quality_levels:
            logger.info(f"🔄 尝试音质: {qual}")
            try:
                result_str = api.parse_song(song_id, level=qual)

                try:
                    temp_result = json.loads(result_str)
                    if temp_result.get('status') == 200 and temp_result.get('data', {}).get('url'):
                        result = temp_result
                        used_level = qual
                        logger.info(f"✅ 找到可用音质: {qual}")
                        break
                    else:
                        logger.warning(f"⚠️  音质 {qual} 不可用: {temp_result.get('data', {}).get('msg', '未知原因')}")
                except json.JSONDecodeError:
                    logger.error(f"❌ 音质 {qual} 解析失败")
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ 网络请求失败 (音质 {qual}): {str(e)}")
                continue
            except Exception as e:
                logger.error(f"❌ 获取音质 {qual} 时发生未知错误: {str(e)}")
                continue

        if not result:
            logger.error(f"\n❌ 所有音质均不可用")
            return {"success": False, "message": "无可用音质", "tried_levels": quality_levels}

        if result and result.get('status') == 200:
            data = result['data']
            logger.info(f"\n✅ 提取成功!\n")
            logger.info(f"🎶 歌曲名称: {data['name']}")
            logger.info(f"🎤 歌手: {data['ar_name']}")
            logger.info(f"💿 专辑: {data['al_name']}")
            logger.info(f"🔊 实际音质: {used_level or data['level']}")
            logger.info(f"📦 文件大小: {data['size']}")
            logger.info(f"🔗 下载/播放链接: {data['url']}")
            logger.info(f"🖼️  封面图片: {data['pic']}")

            # 返回实际使用的音质
            result['used_quality'] = used_level or data['level']

            if data.get('lyric'):
                logger.info(f"\n📝 歌词:")
                logger.info(data['lyric'][:500] + "..." if len(data['lyric']) > 500 else data['lyric'])

            return result
        else:
            logger.error(f"\n❌ 提取失败: {result.get('data', {}).get('msg', '未知错误')}")
            return result

    except Exception as e:
        logger.error(f"❌ 获取歌曲元数据时发生严重错误: {str(e)}")
        return {"success": False, "message": f"获取元数据失败: {str(e)}", "song_id": song_id}


def write_metadata_to_file(file_path: str, metadata: Dict[str, Any]) -> bool:
    """
    将元数据写入音频文件

    Args:
        file_path: 音频文件路径
        metadata: 包含歌曲信息的元数据字典

    Returns:
        bool: 写入是否成功
    """
    try:
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        song_name = metadata.get('name', '')
        artist = metadata.get('ar_name', '').split(',')
        album = metadata.get('al_name', '')
        lyric = metadata.get('lyric', '')
        cover_path = metadata.get('cover_path', '')
        track_number = metadata.get('track_number', '')

        logger.info(f"🏷️  正在写入元数据到 {os.path.basename(file_path)}...")

        if ext in ['.mp3', '.mp2', '.mp1']:
            # 处理 MP3 文件
            audio_file = ID3(file_path)

            # 标题
            if song_name:
                audio_file.add(TIT2(encoding=3, text=song_name))

            # 艺术家
            if artist:
                audio_file.add(TPE1(encoding=3, text=artist))

            # 专辑
            if album:
                audio_file.add(TALB(encoding=3, text=album))

            # 年份
            audio_file.add(TYER(encoding=3, text=str(time.localtime().tm_year)))

            # 轨道号
            if track_number:
                from mutagen.id3 import TRCK
                audio_file.add(TRCK(encoding=3, text=track_number))

            # 注释（歌词）
            if lyric:
                audio_file.add(COMM(encoding=3, lang='eng', desc='', text=lyric[:1000]))  # 限制长度

            # 封面图片
            if cover_path and os.path.exists(cover_path):
                try:
                    with open(cover_path, 'rb') as img_file:
                        img_data = img_file.read()
                        audio_file.add(APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=img_data
                        ))
                except Exception as e:
                    logger.warning(f"⚠️  封面图片写入失败: {str(e)}")

            audio_file.save()

        elif ext == '.flac':
            # 处理 FLAC 文件
            audio_file = FLAC(file_path)

            if song_name:
                audio_file['TITLE'] = song_name
            if artist:
                audio_file['ARTIST'] = artist
            if album:
                audio_file['ALBUM'] = album
            if lyric:
                audio_file['LYRICS'] = lyric[:1000]
            if track_number:
                audio_file['TRACKNUMBER'] = track_number

            # 添加封面
            if cover_path and os.path.exists(cover_path):
                try:
                    with open(cover_path, 'rb') as img_file:
                        img_data = img_file.read()
                        picture = Picture()
                        picture.type = 3  # Cover (front)
                        picture.mime = 'image/jpeg'
                        picture.data = img_data
                        audio_file.add_picture(picture)
                except Exception as e:
                    logger.warning(f"⚠️  封面图片写入失败: {str(e)}")

            audio_file.save()

        elif ext in ['.m4a', '.mp4', '.aac']:
            # 处理 MP4/AAC 文件
            audio_file = MP4(file_path)

            # 创建元数据字典
            mp4_tags = {}

            if song_name:
                mp4_tags['\xa9nam'] = song_name  # Title
            if artist:
                mp4_tags['\xa9ART'] = artist  # Artist
            if album:
                mp4_tags['\xa9alb'] = album  # Album
            if lyric:
                mp4_tags['\xa9lyr'] = lyric[:1000]  # Lyrics
            if track_number:
                mp4_tags['trkn'] = [(int(track_number), 0)]  # Track number for MP4

            # 添加封面
            if cover_path and os.path.exists(cover_path):
                try:
                    with open(cover_path, 'rb') as img_file:
                        img_data = img_file.read()
                        mp4_tags['covr'] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]
                except Exception as e:
                    logger.warning(f"⚠️  封面图片写入失败: {str(e)}")

            audio_file.tags.update(mp4_tags)
            audio_file.save()

        else:
            logger.warning(f"⚠️  不支持的文件格式: {ext}")
            return False

        logger.info(f"✅ 元数据写入成功!")
        return True

    except Exception as e:
        logger.error(f"❌ 元数据写入失败: {str(e)}")
        return False


def write_picture_to_file(file_path: str) -> bool:
    """
    将同目录下的图片文件写入音频文件

    Args:
        file_path: 音频文件路径

    Returns:
        bool: 写入是否成功
    """
    try:
        # 获取文件所在目录和基础文件名（不包含扩展名）
        file_dir = os.path.dirname(file_path)
        file_base_name = os.path.splitext(os.path.basename(file_path))[0]

        # 支持的图片格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        cover_path = None

        # 查找同目录下同名的图片文件
        for ext in image_extensions:
            potential_cover = os.path.join(file_dir, file_base_name + ext)
            if os.path.exists(potential_cover):
                cover_path = potential_cover
                logger.info(f"🖼️  找到封面图片: {os.path.basename(cover_path)}")
                break

        if not cover_path:
            logger.warning(f"⚠️  未找到与歌曲同名的图片文件")
            return False

        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        logger.info(f"🏷️  正在将图片写入 {os.path.basename(file_path)}...")

        if ext in ['.mp3', '.mp2', '.mp1']:
            # 处理 MP3 文件
            try:
                audio_file = ID3(file_path)

                # 读取图片文件
                with open(cover_path, 'rb') as img_file:
                    img_data = img_file.read()

                    # 判断图片MIME类型
                    mime_type = 'image/jpeg'
                    if cover_path.lower().endswith('.png'):
                        mime_type = 'image/png'
                    elif cover_path.lower().endswith('.bmp'):
                        mime_type = 'image/bmp'
                    elif cover_path.lower().endswith('.gif'):
                        mime_type = 'image/gif'

                    # 添加封面图片
                    audio_file.add(APIC(
                        encoding=3,
                        mime=mime_type,
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=img_data
                    ))

                audio_file.save()
                logger.info(f"✅ MP3封面图片写入成功!")
                return True

            except Exception as e:
                logger.error(f"❌ MP3封面图片写入失败: {str(e)}")
                return False

        elif ext == '.flac':
            # 处理 FLAC 文件
            try:
                audio_file = FLAC(file_path)

                # 读取图片文件
                with open(cover_path, 'rb') as img_file:
                    img_data = img_file.read()

                    # 创建Picture对象
                    picture = Picture()
                    picture.type = 3  # Cover (front)

                    # 判断图片MIME类型
                    if cover_path.lower().endswith('.png'):
                        picture.mime = 'image/png'
                    elif cover_path.lower().endswith('.bmp'):
                        picture.mime = 'image/bmp'
                    elif cover_path.lower().endswith('.gif'):
                        picture.mime = 'image/gif'
                    else:
                        picture.mime = 'image/jpeg'

                    picture.data = img_data
                    audio_file.add_picture(picture)

                audio_file.save()
                logger.info(f"✅ FLAC封面图片写入成功!")
                return True

            except Exception as e:
                logger.error(f"❌ FLAC封面图片写入失败: {str(e)}")
                return False

        elif ext in ['.m4a', '.mp4', '.aac']:
            # 处理 MP4/AAC 文件
            try:
                audio_file = MP4(file_path)

                # 读取图片文件
                with open(cover_path, 'rb') as img_file:
                    img_data = img_file.read()

                    # 判断图片格式
                    image_format = MP4Cover.FORMAT_JPEG
                    if cover_path.lower().endswith('.png'):
                        image_format = MP4Cover.FORMAT_PNG

                    # 更新标签
                    if audio_file.tags is None:
                        audio_file.add_tags()

                    audio_file.tags['covr'] = [MP4Cover(img_data, imageformat=image_format)]

                audio_file.save()
                logger.info(f"✅ MP4/AAC封面图片写入成功!")
                return True

            except Exception as e:
                logger.error(f"❌ MP4/AAC封面图片写入失败: {str(e)}")
                return False

        else:
            logger.warning(f"⚠️  不支持的文件格式: {ext}")
            return False

    except Exception as e:
        logger.error(f"❌ 图片写入过程中发生错误: {str(e)}")
        return False


def download_song_and_resources(song_metadata: Dict[str, Any], download_dir: str = "downloads",
                                idx: int = None) -> bool:
    """
    下载歌曲文件和相关资源(歌词、封面)

    Args:
        song_metadata: 歌曲元数据字典
        download_dir: 下载目录路径

    Returns:
        bool: 下载是否成功
    """
    if not song_metadata or not song_metadata.get('success', True):
        logger.error("❌ 无效的歌曲元数据")
        return False

    try:
        data = song_metadata['data']
        song_name = data['name']
        artist = data['ar_name']
        album = data['al_name']
        download_url = data['url']
        lyric = data.get('lyric', '')
        cover_url = data.get('pic', '')
        file_size = data.get('size', '')
        quality = song_metadata.get('used_quality', data.get('level', 'unknown'))

        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)

        # 清理文件名中的非法字符
        safe_song_name = re.sub(r'[<>:"/\\|?*]', '_', song_name)
        safe_artist = re.sub(r'[<>:"/\\|?*]', '_', artist)

        # 从下载URL中提取文件扩展名
        file_extension = ".mp3"  # 默认扩展名
        if download_url:
            # 解析URL获取文件名
            parsed_url = urllib.parse.urlparse(download_url)
            # 从路径中提取文件扩展名
            path_parts = parsed_url.path.split('/')
            if path_parts:
                last_part = path_parts[-1]
                if '.' in last_part:
                    file_extension = os.path.splitext(last_part)[1].lower()
            # 如果URL参数中有文件信息，也尝试提取
            if not file_extension or file_extension == ".mp3":
                query_params = urllib.parse.parse_qs(parsed_url.query)
                if 'v' in query_params and query_params['v'][0]:
                    v_param = query_params['v'][0]
                    if '.' in v_param:
                        ext_from_v = os.path.splitext(v_param)[1].lower()
                        if ext_from_v in ['.flac', '.wav', '.aac', '.m4a']:
                            file_extension = ext_from_v

        # 构造文件名
        if idx is not None:
            # 如果提供了索引，格式化为3位数字（不足前面补0）
            formatted_index = f"{idx:03d}"
            filename = f"{formatted_index} - {safe_artist} - {safe_song_name}"
        else:
            filename = f"{safe_artist} - {safe_song_name}"
        music_file_path = os.path.join(download_dir, f"{filename}{file_extension}")
        lyric_file_path = os.path.join(download_dir, f"{filename}.lrc")
        cover_file_path = os.path.join(download_dir, f"{filename}.jpg")

        logger.info(f"📄 检测到文件格式: {file_extension}")

        # 检查同名文件是否已存在，如果存在则跳过下载
        if os.path.exists(music_file_path):
            logger.info(f"\n⏭️  文件已存在，跳过下载: {os.path.basename(music_file_path)}")
            logger.info(f"📁 文件路径: {music_file_path}")
            return True

        logger.info(f"\n📥 开始下载: {filename}")
        logger.info(f"📊 文件大小: {file_size}")
        logger.info(f"🔊 音质: {quality}")
        logger.info("-" * 60)

        # 下载音乐文件
        logger.info("🎵 正在下载音乐文件...")
        random_sleep()
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(music_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"✅ 音乐文件下载完成: {os.path.basename(music_file_path)}")
        except Exception as e:
            logger.error(f"❌ 音乐文件下载失败: {str(e)}")
            return False

        # 将封面路径和轨道号传递给元数据
        metadata_for_tagging = data.copy()
        if os.path.exists(cover_file_path):
            metadata_for_tagging['cover_path'] = cover_file_path
        else:
            metadata_for_tagging['cover_path'] = ''

        # 添加轨道号信息
        if idx is not None:
            metadata_for_tagging['track_number'] = str(idx)

        # 写入元数据到音频文件
        logger.info("\n🏷️  正在写入元数据...")
        if write_metadata_to_file(music_file_path, metadata_for_tagging):
            logger.info(f"✅ 元数据已成功附加到: {os.path.basename(music_file_path)}")
        else:
            logger.warning(f"⚠️  元数据写入失败，但文件已正常下载")

        # 下载歌词
        if lyric:
            logger.info("📝 正在保存歌词...")
            try:
                with open(lyric_file_path, 'w', encoding='utf-8') as f:
                    f.write(lyric)
                logger.info(f"✅ 歌词保存完成: {os.path.basename(lyric_file_path)}")
            except Exception as e:
                logger.warning(f"⚠️  歌词保存失败: {str(e)}")
        else:
            logger.warning("⚠️  未找到歌词")

        # 下载封面
        if cover_url:
            logger.info("🖼️  正在下载封面...")
            random_sleep()
            try:
                cover_response = requests.get(cover_url + '?param=320x320', timeout=10)
                cover_response.raise_for_status()

                with open(cover_file_path, 'wb') as f:
                    f.write(cover_response.content)
                logger.info(f"✅ 封面下载完成: {os.path.basename(cover_file_path)}")
            except Exception as e:
                logger.warning(f"⚠️  封面下载失败: {str(e)}")
        else:
            logger.warning("⚠️  未找到封面")

        logger.info("🎵 添加封面到歌曲文件...")
        write_picture_to_file(music_file_path)
        logger.info("✅ 封面已添加到歌曲文件")

        logger.info(f"\n🎉 下载完成! 文件保存在: {download_dir}")
        return True

    except KeyError as e:
        logger.error(f"❌ 元数据缺少必要字段: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ 下载过程中发生错误: {str(e)}")
        return False


def download_song(song_id: str, level: str = "lossless"):
    metadata = get_song_metadata_by_song_id(song_id, level)
    download_song_and_resources(metadata, idx=None)


def download_album(album_id: str, index_ids: list, level: str = "lossless"):
    album_metadata = get_song_ids_by_album_id(album_id)
    index = 0
    for song_id in album_metadata['song_ids']:
        song_detail = album_metadata['song_details'][index]
        song_index = song_detail['index']
        logger.info(f"{index + 1}. {song_detail}")

        if len(index_ids) > 0:
            if song_index in index_ids:
                logger.info(f"{song_index} is in the {index_ids}, continue downloading...")
                metadata = get_song_metadata_by_song_id(song_id, level)
                download_song_and_resources(metadata, idx=song_index)
            else:
                logger.info(f"{song_index} is not in the {index_ids}, skipping downloading...")
        else:
            metadata = get_song_metadata_by_song_id(song_id, level)
            download_song_and_resources(metadata, idx=song_index)
        index += 1


def download_playlist(playlist_id: str, index_ids: list, level: str = "lossless"):
    playlist_metadata = get_song_ids_by_playlist_id(playlist_id)
    index = 0
    for song_id in playlist_metadata['song_ids']:
        song_detail = playlist_metadata['song_details'][index]
        song_index = song_detail['index']
        logger.info(f"{index + 1}. {song_detail}")

        if len(index_ids) > 0:
            if song_index in index_ids:
                logger.info(f"{song_index} is in the {index_ids}, continue downloading...")
                metadata = get_song_metadata_by_song_id(song_id, level)
                download_song_and_resources(metadata, idx=None)
            else:
                logger.info(f"{song_index} is not in the {index_ids}, skipping downloading...")
        else:
            metadata = get_song_metadata_by_song_id(song_id, level)
            download_song_and_resources(metadata, idx=None)
        index += 1


if __name__ == "__main__":
    # Part-1 Download Song by Song ID
    # https://music.163.com/song?id=1403318151&uct2=U2FsdGVkX1/51s2ftrMtCWSRuIrLyQp53N06DKxa1F0=
    download_song("2124385868")

    indexes = []
    # indexes = [4, 6, 15, 18, 19]

    # Part-2 Download Songs by Album ID
    # download_album("360266684", indexes)

    # Part-3 Download Playlist
    # download_playlist("2605912264", indexes)

    pass