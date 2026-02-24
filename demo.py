import os
import random
import re
import time
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Optional, Dict, Any, List

import requests
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC, COMM, TRCK, TYER
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover


class NeteaseMusicToolAPI:
    """
    Netease Music API Client
    """

    def __init__(self, base_url: str = "https://musicapi.lxchen.cn", request_delay: float = 0.5):
        self.base_url = base_url.rstrip('/')
        self.request_delay = request_delay
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

    def _random_sleep(self):
        """Random delay to avoid frequent requests"""
        time.sleep(self.request_delay + random.uniform(0.1, 0.5))

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
        self._random_sleep()
        response = self.session.post(
            f"{self.base_url}/Search",
            data={'keyword': keyword, 'limit': limit}
        )
        return response.text

    # ==================== 2. 单曲解析 ====================

    def parse_song(self, song_id_or_url: str, level: str = "lossless") -> str:
        """Parse song details"""
        song_id = self._extract_id(song_id_or_url, 'song')

        self._random_sleep()
        response = self.session.post(
            f"{self.base_url}/Song_V1",
            data={'url': song_id, 'level': level, 'type': 'json'}
        )
        return response.text

    # ==================== 3. 歌单解析 ====================

    def parse_playlist(self, playlist_id_or_url: str) -> str:
        """Parse playlist details"""
        playlist_id = self._extract_id(playlist_id_or_url, 'playlist')

        self._random_sleep()
        response = self.session.get(
            f"{self.base_url}/Playlist",
            params={'id': playlist_id}
        )
        return response.text

    # ==================== 4. 专辑解析 ====================

    def parse_album(self, album_id_or_url: str) -> str:
        """Parse album details"""
        album_id = self._extract_id(album_id_or_url, 'album')

        self._random_sleep()
        response = self.session.get(
            f"{self.base_url}/Album",
            params={'id': album_id}
        )
        return response.text

# ==================== 使用示例 ====================

# 定义音质等级列表
quality_levels = ["lossless", "exhigh", "standard"]

def get_song_by_id(song_id: str, level: str = "lossless") -> Dict[str, Any]:
    """
    通过歌曲ID提取歌曲信息

    Args:
        song_id: 歌曲ID(例如: "186016")
        level: 音质等级 (standard, exhigh, lossless, hires)

    Returns:
        包含歌曲详细信息的字典，包含下载链接
    """
    api = NeteaseMusicToolAPI("https://musicapi.lxchen.cn")

    print("=" * 60)
    print("🎵 通过歌曲ID提取信息")
    print("=" * 60)
    print(f"歌曲ID: {song_id}")
    print(f"音质等级: {level}")
    print("-" * 60)

    result = None
    used_level = None
    
    # 尝试不同音质等级
    for qual in quality_levels:
        print(f"🔄 尝试音质: {qual}")
        result_str = api.parse_song(song_id, level=qual)
        
        try:
            temp_result = json.loads(result_str)
            if temp_result.get('status') == 200 and temp_result.get('data', {}).get('url'):
                result = temp_result
                used_level = qual
                print(f"✅ 找到可用音质: {qual}")
                break
            else:
                print(f"⚠️  音质 {qual} 不可用: {temp_result.get('data', {}).get('msg', '未知原因')}")
        except json.JSONDecodeError:
            print(f"❌ 音质 {qual} 解析失败")
            continue
    
    if not result:
        print(f"\n❌ 所有音质均不可用")
        return {"success": False, "message": "无可用音质", "tried_levels": quality_levels}

    if result and result.get('status') == 200:
        data = result['data']
        print(f"\n✅ 提取成功!\n")
        print(f"🎶 歌曲名称: {data['name']}")
        print(f"🎤 歌手: {data['ar_name']}")
        print(f"💿 专辑: {data['al_name']}")
        print(f"🔊 实际音质: {used_level or data['level']}")
        print(f"📦 文件大小: {data['size']}")
        print(f"🔗 下载/播放链接: {data['url']}")
        print(f"🖼️  封面图片: {data['pic']}")
        
        # 返回实际使用的音质
        result['used_quality'] = used_level or data['level']

        if data.get('lyric'):
            print(f"\n📝 歌词:")
            print(data['lyric'][:500] + "..." if len(data['lyric']) > 500 else data['lyric'])

        return result
    else:
        print(f"\n❌ 提取失败: {result.get('data', {}).get('msg', '未知错误')}")
        return result


def batch_download_songs(song_ids: List[str], download_dir: str = "downloads", max_workers: int = 3) -> Dict[str, Any]:
    """
    批量下载多首歌曲
    
    Args:
        song_ids: 歌曲ID列表
        download_dir: 下载目录路径
        max_workers: 最大并发线程数
    
    Returns:
        Dict: 包含成功和失败详情的统计信息
    """
    print("=" * 60)
    print("🎵 批量下载歌曲")
    print("=" * 60)
    print(f"待下载歌曲数量: {len(song_ids)}")
    print(f"下载目录: {download_dir}")
    print(f"最大并发数: {max_workers}")
    print("-" * 60)
    
    # 结果统计
    results = {
        'total': len(song_ids),
        'success': 0,
        'failed': 0,
        'success_list': [],
        'failed_list': []
    }
    
    # 线程锁用于安全更新结果
    results_lock = Lock()
    
    def download_single_song(song_id: str) -> Dict[str, Any]:
        """下载单首歌曲的包装函数"""
        try:
            print(f"\n🔄 处理歌曲 ID: {song_id}")
            metadata = get_song_by_id(song_id)
            
            if metadata and metadata.get('success', True):
                success = download_song_and_resources(metadata, download_dir)
                if success:
                    with results_lock:
                        results['success'] += 1
                        results['success_list'].append({
                            'song_id': song_id,
                            'song_name': metadata['data']['name'],
                            'artist': metadata['data']['ar_name']
                        })
                    return {'song_id': song_id, 'status': 'success'}
                else:
                    with results_lock:
                        results['failed'] += 1
                        results['failed_list'].append({
                            'song_id': song_id,
                            'reason': '下载失败'
                        })
                    return {'song_id': song_id, 'status': 'failed', 'reason': '下载失败'}
            else:
                with results_lock:
                    results['failed'] += 1
                    results['failed_list'].append({
                        'song_id': song_id,
                        'reason': metadata.get('message', '获取元数据失败') if metadata else '获取元数据失败'
                    })
                return {'song_id': song_id, 'status': 'failed', 'reason': '获取元数据失败'}
                
        except Exception as e:
            with results_lock:
                results['failed'] += 1
                results['failed_list'].append({
                    'song_id': song_id,
                    'reason': str(e)
                })
            return {'song_id': song_id, 'status': 'failed', 'reason': str(e)}
    
    # 使用线程池并发下载
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_song = {executor.submit(download_single_song, song_id): song_id 
                         for song_id in song_ids}
        
        # 收集结果
        for future in as_completed(future_to_song):
            song_id = future_to_song[future]
            try:
                result = future.result()
                if result['status'] == 'success':
                    print(f"✅ 歌曲 {song_id} 处理完成")
                else:
                    print(f"❌ 歌曲 {song_id} 处理失败: {result['reason']}")
            except Exception as e:
                print(f"❌ 歌曲 {song_id} 处理异常: {str(e)}")
                with results_lock:
                    results['failed'] += 1
    
    # 输出统计结果
    print("\n" + "=" * 60)
    print("📊 批量下载统计")
    print("=" * 60)
    print(f"总计: {results['total']} 首")
    print(f"✅ 成功: {results['success']} 首")
    print(f"❌ 失败: {results['failed']} 首")
    print(f"成功率: {results['success']/results['total']*100:.1f}%")
    
    if results['success_list']:
        print("\n✅ 成功下载的歌曲:")
        for item in results['success_list']:
            print(f"  • {item['artist']} - {item['song_name']} (ID: {item['song_id']})")
    
    if results['failed_list']:
        print("\n❌ 下载失败的歌曲:")
        for item in results['failed_list']:
            print(f"  • ID: {item['song_id']} - 原因: {item['reason']}")
    
    print("=" * 60)
    
    return results

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
        artist = metadata.get('ar_name', '')
        album = metadata.get('al_name', '')
        lyric = metadata.get('lyric', '')
        cover_path = metadata.get('cover_path', '')
        
        print(f"🏷️  正在写入元数据到 {os.path.basename(file_path)}...")
        
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
                    print(f"⚠️  封面图片写入失败: {str(e)}")
            
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
                    print(f"⚠️  封面图片写入失败: {str(e)}")
            
            audio_file.save()
            
        elif ext in ['.m4a', '.mp4', '.aac']:
            # 处理 MP4/AAC 文件
            audio_file = MP4(file_path)
            
            # 创建元数据字典
            mp4_tags = {}
            
            if song_name:
                mp4_tags['\xa9nam'] = song_name  # Title
            if artist:
                mp4_tags['\xa9ART'] = artist     # Artist
            if album:
                mp4_tags['\xa9alb'] = album      # Album
            if lyric:
                mp4_tags['\xa9lyr'] = lyric[:1000]  # Lyrics
            
            # 添加封面
            if cover_path and os.path.exists(cover_path):
                try:
                    with open(cover_path, 'rb') as img_file:
                        img_data = img_file.read()
                        mp4_tags['covr'] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]
                except Exception as e:
                    print(f"⚠️  封面图片写入失败: {str(e)}")
            
            audio_file.tags.update(mp4_tags)
            audio_file.save()
            
        else:
            print(f"⚠️  不支持的文件格式: {ext}")
            return False
        
        print(f"✅ 元数据写入成功!")
        return True
        
    except Exception as e:
        print(f"❌ 元数据写入失败: {str(e)}")
        return False


def download_song_and_resources(song_metadata: Dict[str, Any], download_dir: str = "downloads") -> bool:
    """
    下载歌曲文件和相关资源(歌词、封面)
    
    Args:
        song_metadata: 歌曲元数据字典
        download_dir: 下载目录路径
    
    Returns:
        bool: 下载是否成功
    """
    if not song_metadata or not song_metadata.get('success', True):
        print("❌ 无效的歌曲元数据")
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
        filename = f"{safe_artist} - {safe_song_name}"
        music_file_path = os.path.join(download_dir, f"{filename}{file_extension}")
        lyric_file_path = os.path.join(download_dir, f"{filename}.lrc")
        cover_file_path = os.path.join(download_dir, f"{filename}.jpg")
        
        print(f"📄 检测到文件格式: {file_extension}")
        
        print(f"\n📥 开始下载: {filename}")
        print(f"📊 文件大小: {file_size}")
        print(f"🔊 音质: {quality}")
        print("-" * 60)
        
        # 下载音乐文件
        print("🎵 正在下载音乐文件...")
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(music_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ 音乐文件下载完成: {os.path.basename(music_file_path)}")
        except Exception as e:
            print(f"❌ 音乐文件下载失败: {str(e)}")
            return False
        
        # 将封面路径传递给元数据
        metadata_for_tagging = data.copy()
        if os.path.exists(cover_file_path):
            metadata_for_tagging['cover_path'] = cover_file_path
        else:
            metadata_for_tagging['cover_path'] = ''
        
        # 写入元数据到音频文件
        print("\n🏷️  正在写入元数据...")
        if write_metadata_to_file(music_file_path, metadata_for_tagging):
            print(f"✅ 元数据已成功附加到: {os.path.basename(music_file_path)}")
        else:
            print(f"⚠️  元数据写入失败，但文件已正常下载")
        
        # 下载歌词
        if lyric:
            print("📝 正在保存歌词...")
            try:
                with open(lyric_file_path, 'w', encoding='utf-8') as f:
                    f.write(lyric)
                print(f"✅ 歌词保存完成: {os.path.basename(lyric_file_path)}")
            except Exception as e:
                print(f"⚠️  歌词保存失败: {str(e)}")
        else:
            print("⚠️  未找到歌词")
        
        # 下载封面
        if cover_url:
            print("🖼️  正在下载封面...")
            try:
                cover_response = requests.get(cover_url + '?param=512x512', timeout=10)
                cover_response.raise_for_status()
                
                with open(cover_file_path, 'wb') as f:
                    f.write(cover_response.content)
                print(f"✅ 封面下载完成: {os.path.basename(cover_file_path)}")
            except Exception as e:
                print(f"⚠️  封面下载失败: {str(e)}")
        else:
            print("⚠️  未找到封面")
        
        print(f"\n🎉 下载完成! 文件保存在: {download_dir}")
        return True
        
    except KeyError as e:
        print(f"❌ 元数据缺少必要字段: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 下载过程中发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    # https://music.163.com/song?id=3334714206&uct2=U2FsdGVkX1/bZsD39mI3mNQ9P08OkVsv9W6eRBdWZz8=
    metadata = get_song_by_id("3334714206", "lossless")

    download_song_and_resources(metadata)