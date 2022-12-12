# log_checker ver.1.1.0

## About
なんらかのログを見るためのツールです。
当ツールの使用にて生じた損害などに関しては一切の責任を負いかねます。

## Requirements
### Dockerを使う場合
- Docker
    - Docker Compose
### 使わない場合
- Python
    - fastapi - Web framework
    - uvicorn - ASGI
    - jinja2 - テンプレートエンジン

## Run it
```console
$ docker compose up
```

## Usage
1. logファイル配置
    - *.log を logs/ 配下に設置
2. ブラウザアクセス
    - 下記のURLにアクセスして、あとは流れでお願いします
    - http://127.0.0.1:8001/
    