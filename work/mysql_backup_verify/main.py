#!/usr/bin/env python3
import os
import re
import logging
import random
import tarfile
from datetime import datetime, timedelta


# 计算上个月时间范围[5](@ref)
BACKUP_FILE_PATH = "/path/to/backup/files"  # 远程目录路径
TODAY = datetime.now()
THIS_MONTH = TODAY.strftime("%Y%m")
FIRST_DAY = TODAY.replace(day=1)
LAST_MONTH_END = FIRST_DAY - timedelta(days=1)
LAST_MONTH = LAST_MONTH_END.strftime("%Y%m")
        

# 配置日志记录[1,3](@ref)
logging.basicConfig(
    filename='file_processor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_last_month_files(remote_dir):
    """
    获取上个月符合格式的文件列表
    """
    try:
        # 遍历远程目录[7,8](@ref)
        all_files = os.listdir(remote_dir)
        pattern = re.compile(r'_(.*?)_full_(\d{8})\..*\.tar\.gz')
        
        valid_files = []
        for f in all_files:
            match = pattern.findall(f)
            if match:
                hostname = match[0][0]
                filedate = match[0][1]
                # 筛选上个月文件[5](@ref)
                if filedate.startswith(LAST_MONTH):
                    valid_files.append({
                        'filename': f,
                        'hostname': hostname,
                        'filedate': filedate,
                        'fullpath': os.path.join(remote_dir, f)
                    })
        return valid_files
    except Exception as e:
        logging.error(f"获取文件列表失败: {str(e)}")
        raise

def process_hostnames(file_list):
    """
    去重、排序主机名并写入文件
    """
    try:
        # 去重排序主机名
        hostnames = sorted({f['hostname'] for f in file_list})
        logging.info(f"去重后主机列表: {', '.join(hostnames)}")
        
        # 写入文件
        with open("hostnames_list.txt", "w") as file:
            file.write("\n".join(hostnames))
        logging.info("主机名列表已写入文件: hostnames_list.txt")
    except Exception as e:
        logging.error(f"处理主机名失败: {str(e)}")
        raise

def process_files(file_list):
    """
    按当天序号读取对应行号的 hostname_list 中的主机名，
    筛选该主机名的上个月文件列表，并随机选择一个文件
    """
    try:
        # 读取主机名列表文件
        hostname_file = f"hostnames_list.{THIS_MONTH}.txt"
        if not os.path.exists(hostname_file):
            raise FileNotFoundError(f"主机名列表文件不存在: {hostname_file}")
        
        with open(hostname_file, "r") as file:
            hostnames = [line.strip() for line in file.readlines()]
        
        # 获取当天日期对应的行号
        today_num = TODAY.day
        if today_num > len(hostnames) or today_num < 1:
            raise IndexError(f"当天日期超出主机名列表范围: {today_num}")
        
        # 获取当天对应的主机名
        target_hostname = hostnames[today_num - 1]  # 行号从 1 开始，索引从 0 开始
        logging.info(f"当天对应的主机名: {today_num}|{target_hostname}")
        
        # 筛选该主机名的上个月文件列表
        filtered_files = [f for f in file_list if f['hostname'] == target_hostname]
        if not filtered_files:
            raise ValueError(f"未找到主机名 {target_hostname} 的上个月文件")
        
        # 随机选择一个文件
        chosen_file = random.choice(filtered_files)
        logging.info(f"随机选择的文件: {chosen_file['filename']}")
        
        return chosen_file
    except Exception as e:
        logging.error(f"文件处理失败: {str(e)}")
        raise

def download_and_extract(selected_file):
    """
    下载并解压单一文件
    """
    try:
        # 下载文件（此处为本地拷贝示例）
        local_path = os.path.basename(selected_file['fullpath'])
        with open(selected_file['fullpath'], 'rb') as src, open(local_path, 'wb') as dst:
            dst.write(src.read())
        logging.info(f"已下载文件到: {local_path}")
        
        # 解压文件
        extract_path = f"./extracted/{selected_file['hostname']}"
        os.makedirs(extract_path, exist_ok=True)
        with tarfile.open(local_path, 'r:gz') as tar:
            tar.extractall(path=extract_path)
        logging.info(f"已解压到: {extract_path}")
    except Exception as e:
        logging.error(f"下载解压失败: {str(e)}")
        raise

if __name__ == "__main__":
    remote_directory = BACKUP_FILE_PATH
    
    try:
        logging.info("======== 开始执行脚本 ========")
        
        # 第一步：获取文件列表
        files = get_last_month_files(remote_directory)
        logging.info(f"找到上个月文件总数: {len(files)}")
        
        # 第二步：检查是否为当月1号并处理主机名
        if TODAY.day == 1:
            process_hostnames(files)
        
        # 第三步：处理文件
        selected = process_files(files)
        
        # 第四步：下载解压
        download_and_extract(selected)
        
        logging.info("======== 脚本执行完成 ========")
    except Exception as e:
        logging.critical(f"主流程异常: {str(e)}")