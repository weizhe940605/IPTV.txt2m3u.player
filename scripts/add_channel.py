import os
import argparse
import tempfile
import shutil

def add_channels_to_m3u(input_file, output_file, channels_str, group_name, append_to_end, merge_urls):
    """
    支持格式: "频道1,url1,url2;频道2,urlA"
    - merge_urls: True 时，多个 URL 合并在一个元数据下
    """
    # 1. 解析频道组
    channel_groups = [g.strip() for g in channels_str.split(';') if g.strip()]
    
    new_channels_block = ""
    for group in channel_groups:
        parts = [p.strip() for p in group.split(',')]
        if len(parts) < 2:
            continue
            
        name = parts[0]
        urls = parts[1:]
        
        # 构建元数据行
        # 根据你之前的示例，这里保留 tvg-name 和 group-title 的规范格式
        inf_line = f'#EXTINF:-1 tvg-name="{name}" group-title="{group_name}",{name}\n'
        
        if merge_urls:
            # 模式：合并 URL
            new_channels_block += inf_line
            for url in urls:
                new_channels_block += f"{url}\n"
        else:
            # 模式：独立生成（每个 URL 一个元数据行）
            for url in urls:
                new_channels_block += f"{inf_line}{url}\n"
    
    if not os.path.exists(input_file):
        print(f"错误：找不到输入文件 '{input_file}'")
        return

    is_same_file = os.path.abspath(input_file) == os.path.abspath(output_file)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if is_same_file:
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(output_file), text=True)
            out_f = open(fd, 'w', encoding='utf-8')
        else:
            out_f = open(output_file, 'w', encoding='utf-8')

        with out_f:
            if append_to_end:
                out_f.writelines(lines)
                if lines and not lines[-1].endswith('\n'):
                    out_f.write('\n')
                out_f.write(new_channels_block)
            else:
                if lines and lines[0].strip().startswith("#EXTM3U"):
                    out_f.write(lines[0])
                    out_f.write(new_channels_block)
                    out_f.writelines(lines[1:])
                else:
                    out_f.write("#EXTM3U\n")
                    out_f.write(new_channels_block)
                    out_f.writelines(lines)

        if is_same_file:
            shutil.move(temp_path, output_file)
                
        print(f"处理成功！模式：{'合并 URL' if merge_urls else '独立条目'}，位置：{'末尾' if append_to_end else '开头'}")

    except Exception as e:
        print(f"处理过程中发生错误: {e}")

def main():
    parser = argparse.ArgumentParser(description="高级 M3U 频道插入脚本")
    parser.add_argument("-i", "--input", required=True, help="输入 M3U 文件")
    parser.add_argument("-o", "--output", required=True, help="输出 M3U 文件")
    parser.add_argument("-a", "--add", required=True, help='格式: "名1,u1,u2;名2,u3"')
    parser.add_argument("-g", "--group", default="其它", help="分组名")
    parser.add_argument("-r", "--rear", action="store_true", help="添加到文件末尾")
    parser.add_argument("-m", "--merge", action="store_true", help="将同频道下的所有 URL 合并在一个元数据下")
    
    args = parser.parse_args()
    add_channels_to_m3u(args.input, args.output, args.add, args.group, args.rear, args.merge)

if __name__ == "__main__":
    main()
