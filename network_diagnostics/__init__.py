#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 作者：道相抖音@慈悲剪辑，技术问题点关注留言

"""
网络诊断工具模块
用于网络测试、IP查询、端口扫描和网络速度测试
"""

from network_diagnostics.main import NetworkDiagnostics, main
from network_diagnostics.utils import get_network_info, get_external_ip

__all__ = ['NetworkDiagnostics', 'main', 'get_network_info', 'get_external_ip']
