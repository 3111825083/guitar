python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pyinstaller -F -w --name guitar main.py #打包软件
