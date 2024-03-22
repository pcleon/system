import configparser


def covert_config_parser(filename):
    config = configparser.ConfigParser()
    # 在读取文件之前添加一个默认的section头部
    config.read_string("[default]\n" + open(filename).read())
    # 获取所有的配置项
    return config
