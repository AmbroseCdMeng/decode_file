import os
import time
import re
import html

# 定义输入输出目录
input_dir = 'encode_files'
output_dir = 'output'

# 如果输出目录不存在，则创建它
os.makedirs(output_dir, exist_ok=True)

# 函数：处理HTML实体和CDATA
def decode_html_entities(content):
    # 处理HTML实体
    content = html.unescape(content)
    # 去除CDATA部分
    content = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', content, flags=re.DOTALL)
    return content

# 函数：将 HTML 实体编码还原为字符
def decode_html_numeric_entities(content):
    def replace_match(match):
        try:
            return chr(int(match.group(1), 16))
        except ValueError:
            return match.group(0)
    
    # 替换 &#xXXXX; 和 &#DDDD; 格式的实体
    content = re.sub(r'&#x([0-9a-fA-F]+);', replace_match, content)
    content = re.sub(r'&#([0-9]+);', lambda m: chr(int(m.group(1))), content)
    return content

# 函数：将变体的 Unicode 转义字符还原为标准的 \uXXXX 格式
def normalize_unicode_escapes(content):
    # 将 \uu, \uuu 变为 \u
    content = re.sub(r'\\u{2,}', r'\\u', content)
    
    # 查找并替换合法的 \uXXXX 转义字符
    def replace_match(match):
        try:
            return match.group(0).encode().decode('unicode_escape')
        except UnicodeDecodeError:
            # 返回原始字符串，如果解码失败
            return match.group(0)

    # 使用正则表达式查找所有合法的 \uXXXX 转义字符
    fixed_content = re.sub(r'(\\u[0-9a-fA-F]{4})', replace_match, content)
    
    return fixed_content

# 函数：解码文件内容
def decode_content(encoded_content):
    # 第一步：处理HTML实体和CDATA
    content = decode_html_entities(encoded_content)
    print("After decode_html_entities:\n", content)

    # 第二步：处理HTML数字实体
    content = decode_html_numeric_entities(content)
    print("After decode_html_numeric_entities:\n", content)
    
    # 第三步：归一化并解码内容
    decoded_content = normalize_unicode_escapes(content)
    print("After normalize_unicode_escapes:\n", decoded_content)
    
    return decoded_content

# 处理每个输入目录中的文件
for filename in os.listdir(input_dir):
    if os.path.isfile(os.path.join(input_dir, filename)):
        # 读取文件内容
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
            encoded_content = f.read()
        
        try:
            # 解码文件内容
            decoded_content = decode_content(encoded_content)
            
            # 生成输出文件名
            output_filename = f'decode_{filename}_{int(time.time() * 1000)}.{filename.split(".")[-1]}'
            
            # 将解码后的内容写入输出文件
            with open(os.path.join(output_dir, output_filename), 'w', encoding='utf-8') as f:
                f.write(decoded_content)
                
            print(f'已处理 {filename} -> {output_filename}')
        except Exception as e:
            print(f'处理文件 {filename} 时出错: {e}')
