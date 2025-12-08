import re
import argparse
import sys
import os

def merge_m3u_channels(m3u_content):
    """
    合并M3U内容中同名频道下的所有URL。
    
    :param m3u_content: 原始M3U文件的字符串内容。
    :return: 格式化后的M3U字符串内容。
    """
    # 如果输入为空，则直接返回空字符串
    if not m3u_content:
        return ""

    lines = m3u_content.strip().split('\n')
    
    header = ""
    # 存储合并后的频道数据: { "频道名称": {"info": "#EXTINF...", "urls": {"url1", "url2", ...}} }
    channels_map = {}
    
    current_info_line = None
    current_channel_name = None
    
    # --- 第一步：解析和分组数据 ---
    for line in lines:
        line = line.strip()
        
        # 1. 识别 M3U 头部
        if line.startswith('#EXTM3U'):
            header = line
            continue

        # 2. 识别频道信息行
        if line.startswith('#EXTINF:'):
            current_info_line = line
            # 使用正则表达式提取频道名称
            match = re.search(r',(.+)$', line)
            if match:
                current_channel_name = match.group(1).strip()
            else:
                # 如果无法解析频道名称，则跳过
                current_channel_name = None
            
            if current_channel_name and current_channel_name not in channels_map:
                # 存储该频道的第一条信息行
                channels_map[current_channel_name] = {"info": current_info_line, "urls": set()}
            
        # 3. 识别 URL 行
        elif line.startswith('http://') or line.startswith('https://'):
            if current_channel_name and current_channel_name in channels_map:
                # 将 URL 添加到对应频道的集合中 (集合会自动去重)
                channels_map[current_channel_name]["urls"].add(line)
                
            # URL 处理完后，将 current_channel_name 重置，确保下一个 URL 必须紧跟在 #EXTINF 之后
            current_channel_name = None 
            current_info_line = None


    # --- 第二步：重新构建 M3U 内容 ---
    output_lines = [header]
    
    for name, data in channels_map.items():
        # 添加合并后的 #EXTINF 行
        output_lines.append(data["info"])
        # 添加所有收集到的 URL，并排序以保持一致性
        # 注意: 频道属性行 (info) 必须紧跟在频道名称 (name) 提取成功之后。
        for url in sorted(list(data["urls"])):
            output_lines.append(url)
            
    return '\n'.join(output_lines)

def main():
    # 1. 创建参数解析器
    parser = argparse.ArgumentParser(
        description="合并M3U文件中同名频道下的所有URL，并支持文件输入/输出。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # 2. 定义输入文件参数
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help="输入M3U文件的路径，例如: input.m3u"
    )
    
    # 3. 定义输出文件参数
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help="输出M3U文件的路径，例如: output.m3u"
    )

    # 4. 解析命令行参数
    args = parser.parse_args()

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件 '{args.input}' 不存在。", file=sys.stderr)
        sys.exit(1)
        
    # 检查输入和输出文件是否相同
    if args.input == args.output:
        print("错误: 输入文件和输出文件不能是同一个文件，请使用不同的文件名。", file=sys.stderr)
        sys.exit(1)

    try:
        # 读取输入文件
        with open(args.input, 'r', encoding='utf-8') as f:
            m3u_content = f.read()
            
        # 执行合并操作
        modified_m3u = merge_m3u_channels(m3u_content)
        
        # 写入输出文件
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(modified_m3u)
            
        print(f"成功: M3U 频道已合并并写入到 '{args.output}'")
        
    except Exception as e:
        print(f"处理文件时发生错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
