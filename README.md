# pixiv-down-img

一个windows环境用于批量下载 Pixiv 图片的工具。可以通过指定用户或作品来下载，支持以下功能：

- **批量下载多个用户的作品**：通过用户 ID 列表快速获取指定用户的所有公开作品。
- **批量下载多个作品**：通过作品 ID 列表快速下载指定的单个或多个作品。
- **灵活配置**：可以仅设置用户或作品，也可以同时设置，满足多样化的下载需求。

## 功能特点

- **高效下载**：支持多线程，自己在ini配置线程数（线程太高会429），提高下载速度。
- **自定义保存路径**：下载内容可指定保存目录，方便管理。

## 使用方法

1. 克隆项目到本地：
   ```cmd
   git clone https://github.com/mrnfqrbl/pixiv-down-img.git
   cd pixiv-down-img
   pip install -r requirements.txt 
   python main.py
