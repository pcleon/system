#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
import os
import re
import logging
import random
import tarfile
import time
from datetime import datetime, timedelta


# 计算上个月时间范围
BACKUP_FILE_PATH = "/data/3306/mybackup/gfs/clone"
RESTORE_FILE_PATH = "/data/3306/myrestore"
TODAY = datetime.now()
THIS_MONTH = TODAY.strftime("%Y%m")
TODAY_NUM = TODAY.day
FIRST_DAY = TODAY.replace(day=1)
LAST_MONTH_END = FIRST_DAY - timedelta(days=1)
LAST_MONTH = LAST_MONTH_END.strftime("%Y%m")
LOG_FILE = f"/tmp/restore_{THIS_MONTH}{TODAY_NUM}.log"

MYSQL_PORT = 3307
MYSQL_SOCKET = f"{RESTORE_FILE_PATH}/mysql.sock"

# 配置日志记录
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",  # 解决中文编码问题
)


# 重定向Python脚本的stdout/stderr到logging
class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message.strip():
            self.level(message.strip())

    def flush(self):
        pass


sys.stdout = LoggerWriter(logging.info)
sys.stderr = LoggerWriter(logging.error)


# 执行Shell命令并记录输出
def run_shell_command(command):
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
        logging.info(f"命令成功: {command}\n输出: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"命令失败: {command}\n错误: {e.stderr}")


def get_spefic_file(filename):
    """
    获取指定文件
    """
    try:
        # 遍历远程目录[7,8](@ref)
        pattern = re.compile(r"_(.*?)_full_(\d{8})\..*\.tar\.gz")
        match = pattern.findall(filename)
        if match:
            hostname = match[0][0]
            filedate = match[0][1]
            # 筛选上个月文件[5](@ref)
            valid_file = {
                "filename": filename,
                "hostname": hostname,
                "filedate": filedate,
                "fullpath": os.path.join(BACKUP_FILE_PATH, filename),
            }
        return valid_file
    except Exception as e:
        logging.error(f"获取文件失败: {str(e)}")
        raise


def get_last_month_files(remote_dir):
    """
    获取上个月符合格式的文件列表
    """
    try:
        # 遍历远程目录[7,8](@ref)
        all_files = os.listdir(remote_dir)
        pattern = re.compile(r"_(.*?)_full_(\d{8})\..*\.tar\.gz")

        valid_files = []
        for f in all_files:
            match = pattern.findall(f)
            if match:
                hostname = match[0][0]
                filedate = match[0][1]
                # 筛选上个月文件[5](@ref)
                if filedate.startswith(LAST_MONTH):
                    valid_files.append(
                        {
                            "filename": f,
                            "hostname": hostname,
                            "filedate": filedate,
                            "fullpath": os.path.join(remote_dir, f),
                        }
                    )
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
        hostnames = sorted({f["hostname"] for f in file_list})
        # logging.info(f"去重后主机列表: {', '.join(hostnames)}")

        # 写入文件
        host_list_file = f"hostnames_list.{THIS_MONTH}.txt"
        with open(host_list_file, "w") as file:
            file.write("\n".join(hostnames))
        logging.info(f"主机名列表已写入文件: {host_list_file}")
    except Exception as e:
        logging.error(f"处理主机名失败: {str(e)}")
        raise


def choice_random_file(file_list):
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
        if TODAY_NUM > len(hostnames) or TODAY_NUM < 1:
            raise IndexError(f"当天日期超出主机名列表范围: {TODAY_NUM}")

        # 获取当天对应的主机名
        target_hostname = hostnames[TODAY_NUM - 1]  # 行号从 1 开始，索引从 0 开始
        logging.info(f"当天对应的主机名: {TODAY_NUM}|{target_hostname}")

        # 筛选该主机名的上个月文件列表
        filtered_files = [f for f in file_list if f["hostname"] == target_hostname]
        if not filtered_files:
            raise ValueError(f"未找到主机名 {target_hostname} 的上个月文件")

        # 随机选择一个文件
        chosen_file = random.choice(filtered_files)
        logging.info(f"随机选择的文件: {chosen_file['filename']}")

        return chosen_file
    except Exception as e:
        logging.error(f"文件处理失败: {str(e)}")
        raise


def pre_check_disk(selected_file):
    """
    检查文件大小和 /data 分区的可用空间
    """
    try:
        # 获取文件大小
        file_size = os.path.getsize(selected_file["fullpath"])
        logging.info(f"文件大小: {file_size} 字节")

        # 获取 /data 分区的可用空间
        statvfs = os.statvfs("/data")
        free_space = (
            statvfs.f_bavail * statvfs.f_frsize
        )  # 可用空间 = 可用块数 * 每块大小
        logging.info(f"/data 分区可用空间: {free_space} 字节")

        # 检查是否有足够的空间
        if file_size * 10 > free_space:
            raise OSError(
                f"/data 分区可用空间不足，文件大小: {file_size} 字节, 可用空间: {free_space} 字节"
            )

        logging.info("磁盘空间检查通过")
    except Exception as e:
        logging.error(f"预检查失败: {str(e)}")
        raise


def download_and_extract(selected_file):
    """
    下载并解压单一文件
    """
    try:
        # 下载文件（此处为本地拷贝示例）
        local_path = os.path.join(
            RESTORE_FILE_PATH,
            selected_file["hostname"],
            os.path.basename(selected_file["fullpath"]),
        )
        shutil.copyfile(selected_file["fullpath"], local_path)
        logging.info(f"已下载文件到: {local_path}")

        # 解压文件
        extract_path = f"{RESTORE_FILE_PATH}/{selected_file['hostname']}"
        os.makedirs(extract_path, exist_ok=True)
        with tarfile.open(local_path, "r:gz") as tar:
            tar.extractall(path=extract_path, filter="data")
        logging.info(f"已解压到: {extract_path}")
    except Exception as e:
        logging.error(f"下载解压失败: {str(e)}")
        raise


def generate_my_cnf(hostname, restore_base_dir=RESTORE_FILE_PATH):
    """
    动态生成 my.cnf 配置文件
    :param restore_base_dir: 配置文件保存路径
    :param hostname: 数据库主机名，用于动态设置 datadir
    """
    try:
        config_dir = os.path.join(restore_base_dir, hostname)
        if os.path.exists(config_dir):
            import shutil

            shutil.rmtree(config_dir)
            logging.info(f"已删除目录: {config_dir}")

        # 重新创建上层目录
        os.makedirs(config_dir, exist_ok=True)
        logging.info(f"已创建目录: {config_dir}")

        # 动态生成 my.cnf 内容
        my_cnf_content = f"""
[mysqld]
port={MYSQL_PORT}
mysqlx=0
lower_case_table_names=1
datadir={config_dir}/data
skip-log-bin
log-error={config_dir}/error.log
pid-file={config_dir}/mysqld.pid
socket={MYSQL_SOCKET}
"""
        my_cnf = os.path.join(config_dir, "my.cnf")
        # 写入配置文件
        with open(my_cnf, "w") as config_file:
            config_file.write(my_cnf_content.strip())
        logging.info(f"my.cnf 配置文件已生成: {restore_base_dir}")
    except Exception as e:
        logging.error(f"生成 my.cnf 配置文件失败: {str(e)}")
        raise


def verify_data():
    """
    验证数据完整性
    """
    try:
        # 这里可以添加具体的数据验证逻辑
        logging.info("检查库名")
        run_shell_command(
            f"""mysql -S {MYSQL_SOCKET} -e \
            "select SCHEMA_NAME from information_schema.SCHEMATA  where SCHEMA_NAME not in ('information_schema', 'mysql', 'performance_schema', 'sys', 'test', 'c2c_db')"
            """
        )
        logging.info("检查数据")
        run_shell_command(
            f"""
            table_list=`mysql -S {MYSQL_SOCKET} -Ne "select table_schema,table_name from information_schema.tables where TABLE_SCHEMA  not in ('information_schema', 'mysql', 'performance_schema', 'sys', 'test', 'c2c_db') limit 3"`
            echo $table_list |while read schema_name table_name; do
                mysql -S {MYSQL_SOCKET} -e "check table $schema_name.$table_name;select count(*) from $schema_name.$table_name"
            done
            """
        )
        logging.info("数据验证完成")
    except Exception as e:
        logging.error(f"数据验证失败: {str(e)}")
        raise


def boot_mysql(hostname, restore_base_dir=RESTORE_FILE_PATH):
    """
    启动 MySQL 进程并确认启动完成
    :param hostname: 数据库主机名，用于动态设置配置文件路径
    :param restore_base_dir: 数据恢复的基础目录
    """
    try:
        # 检查端口是否被占用
        command_check_port = f"netstat -tuln | grep ':{MYSQL_PORT}'"
        result = subprocess.run(
            command_check_port, shell=True, text=True, capture_output=True
        )
        if result.returncode == 0:  # 如果命令成功执行且有输出，说明端口被占用
            raise OSError(f"MySQL 端口 {MYSQL_PORT} 已被占用，无法启动 MySQL")

        # 配置文件路径
        config_dir = os.path.join(restore_base_dir, hostname)
        my_cnf_path = os.path.join(config_dir, "my.cnf")
        if not os.path.exists(my_cnf_path):
            raise FileNotFoundError(f"配置文件不存在: {my_cnf_path}")

        # 启动 MySQL 进程
        command = f"/data/3306/mysql8/bin/mysqld --defaults-file={my_cnf_path} &"
        logging.info(f"启动 MySQL 进程，命令: {command}")
        run_shell_command(command)  # 使用 run_shell_command 替代 subprocess.run

        # 确认 MySQL 启动完成
        for _ in range(30):  # 最多等待 30 秒
            if os.path.exists(MYSQL_SOCKET):
                logging.info("MySQL 启动完成")
                # 记录启动日志
                run_shell_command(f"cat {config_dir}/error.log")
                # 执行数据验证
                verify_data()
                return
            time.sleep(1)
    except Exception as e:
        logging.error(f"MySQL 启动失败: {str(e)}")
        run_shell_command(f"cat {config_dir}/error.log")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MySQL Backup Verification Script")
    parser.add_argument(
        "-f", "--file", help="指定文件路径进行调度", type=str, required=False
    )
    args = parser.parse_args()

    try:
        logging.info("======== 开始执行脚本 ========")
        # 指定文件时,直接处理
        if args.file:
            selected = get_spefic_file(args.file)
            print(f"指定恢复文件: {selected}")
        # 通过目录自动获取
        else:
            files = get_last_month_files(BACKUP_FILE_PATH)
            logging.info(f"找到上个月文件总数: {len(files)}")
            # 第二步：检查是否为当月1号并处理主机名
            if TODAY.day == 1:
                process_hostnames(files)
            # 第三步：处理文件
            selected = choice_random_file(files)
        print(selected)
        # 第四步：磁盘空间预检查
        pre_check_disk(selected)

        # 第四步：生成 my.cnf
        generate_my_cnf(selected["hostname"])
        # 第五步：下载解压
        download_and_extract(selected)
        print(f"下载并解压文件 ({selected}")
        # 第六步：启动 MySQL
        print(f"启动mysql {selected}")
        boot_mysql(selected["hostname"])

        logging.info("======== 脚本执行完成 ========")
    except Exception as e:
        logging.critical(f"主流程异常: {str(e)}")
    finally:
        run_shell_command(f"""mysql -S {MYSQL_SOCKET} -e "shutdown" """)
        tmpdir= f"{RESTORE_FILE_PATH}/{selected['hostname']}"
        shutil.rmtree(tmpdir)
        print(f"删除临时目录: {tmpdir}")
