"""
データベースパッケージ

データベース接続、セッション管理、CRUD操作を提供します。
"""

from .connection import DatabaseManager

__all__ = ['DatabaseManager']