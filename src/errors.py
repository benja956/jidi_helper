class LCUClientError(Exception):
    """LCU客户端相关错误"""
    pass

class ClientNotFoundError(LCUClientError):
    """客户端未启动"""
    pass

class NetworkError(LCUClientError):
    """网络连接异常"""
    pass

class DataUpdateError(Exception):
    """数据更新失败"""
    pass

class PermissionError(Exception):
    """权限不足"""
    pass 