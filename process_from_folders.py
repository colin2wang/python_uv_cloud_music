"""
文件夹列表工具

功能：
- 列出指定目录中的所有子文件夹

使用方法：
    from list_folders import list_folders, iterate_folders, process_folders
    
    # 列出所有文件夹
    folders = list_folders("J:\\音乐")
    
    # 使用迭代器逐个处理
    for folder in iterate_folders("J:\\音乐"):
        process_album(folder)
    
    # 批量处理
    def my_process_func(folder_path):
        return do_something(folder_path)
    
    results = process_folders("J:\\音乐", my_process_func)
"""

from pathlib import Path
from typing import List, Optional

from process_album_lyrics_fix import fix_album_lyrics


def list_folders(directory: str) -> List[str]:
    """
    列出目录中的所有文件夹

    Args:
        directory: 目录路径

    Returns:
        文件夹绝对路径列表（已排序）

    示例:
        # 列出所有文件夹
        folders = list_folders("J:\\音乐")
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")

    if not dir_path.is_dir():
        raise NotADirectoryError(f"路径不是目录: {directory}")

    # 获取所有子文件夹（不递归）
    folders = []
    for item in dir_path.iterdir():
        if item.is_dir():
            # 跳过隐藏文件夹（以.开头）
            if not item.name.startswith('.'):
                folders.append(item)

    # 按名称排序（使用默认排序：Unicode 编码顺序）
    folders.sort(key=lambda x: x.name.lower())

    # 返回绝对路径列表
    return [str(folder.resolve()) for folder in folders]


def iterate_folders(directory: str):
    """
    迭代器：逐个返回文件夹路径，方便在循环中处理

    Args:
        directory: 目录路径

    Yields:
        文件夹绝对路径

    示例:
        from list_folders import iterate_folders
        for folder in iterate_folders("J:\\音乐"):
            process_album(folder)
    """
    folders = list_folders(directory)
    for folder in folders:
        yield folder


def process_folders(directory: str, process_func, show_progress: bool = True,
                   stop_on_error: bool = False):
    """
    批量处理文件夹

    Args:
        directory: 目录路径
        process_func: 处理函数，接收文件夹绝对路径作为参数
        show_progress: 是否显示进度信息
        stop_on_error: 遇到错误时是否停止（False 则跳过继续处理）

    Returns:
        处理结果列表，每个元素包含 folder, success, result, error

    示例:
        from list_folders import process_folders
        from process_album_lyrics_fix import fix_album_lyrics

        results = process_folders(
            "J:\\音乐",
            fix_album_lyrics,
            show_progress=True
        )

        for r in results:
            print(f"{r['folder']}: {'成功' if r['success'] else '失败'}")
    """
    from datetime import datetime

    folders = list_folders(directory)
    results = []
    total = len(folders)
    start_time = datetime.now()

    if show_progress:
        print("=" * 60)
        print(f"开始处理 {total} 个文件夹")
        print("=" * 60)
    
    for idx, folder in enumerate(folders, 1):
        result = {
            'folder': folder,
            'success': False,
            'result': None,
            'error': None,
            'index': idx
        }
        
        if show_progress:
            folder_name = Path(folder).name
            print(f"\n[{idx}/{total}] 处理: {folder_name}")
            print(f"路径: {folder}")
        
        try:
            # 调用处理函数
            process_result = process_func(folder)
            result['success'] = True
            result['result'] = process_result
            
            if show_progress:
                print(f"✓ 处理成功")
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
            if show_progress:
                print(f"✗ 处理失败: {e}")
            
            if stop_on_error:
                print(f"\n遇到错误，停止处理")
                break
        
        results.append(result)
        
        if show_progress:
            # 显示当前进度
            elapsed = (datetime.now() - start_time).total_seconds()
            if idx > 1:
                avg_time = elapsed / idx
                remaining = avg_time * (total - idx)
                print(f"进度: {idx}/{total} | 已用: {elapsed:.1f}秒 | 预计剩余: {remaining:.1f}秒")
    
    if show_progress:
        # 显示汇总
        success_count = sum(1 for r in results if r['success'])
        failed_count = total - success_count
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("处理完成")
        print(f"总计: {total} 个文件夹")
        print(f"成功: {success_count} 个")
        print(f"失败: {failed_count} 个")
        print(f"耗时: {elapsed:.1f}秒")
        print("=" * 60)
    
    return results


def print_folders(folders: List[str], show_index: bool = False):
    """
    打印文件夹列表
    
    Args:
        folders: 文件夹路径列表
        show_index: 是否显示索引编号
    """
    if not folders:
        print("没有找到任何文件夹")
        return
    
    print(f"找到 {len(folders)} 个文件夹:")
    print("-" * 60)
    
    for i, folder in enumerate(folders):
        if show_index:
            print(f"{i+1:3d}. {folder}")
        else:
            print(folder)
    
    print("-" * 60)
    print(f"总计: {len(folders)} 个文件夹")


def main():
    # 配置：设置目录
    target_directory = r"J:\我的音乐\我的专辑\华语流行"

    # 输出选项
    show_index = True  # 是否显示索引编号
    quiet_mode = True  # 安静模式，只输出路径（每行一个）

    try:
        # 列出文件夹
        folders = list_folders(target_directory)

        if quiet_mode:
            # 安静模式：只输出路径，每行一个
            for folder in folders:
                print(folder)
                fix_album_lyrics(folder)
        else:
            # 正常模式：显示格式化输出
            print(f"排序方式: 默认排序 (Unicode)")
            print()
            print_folders(folders, show_index=show_index)

    
    except FileNotFoundError as e:
        print(f"错误: {e}")
    except NotADirectoryError as e:
        print(f"错误: {e}")
    except ValueError as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")


if __name__ == "__main__":
    main()
