# main.py
import sys
from PyQt5.QtWidgets import QApplication
from guitar_app import MainWindow


def main():
    """主程序入口"""
    app = QApplication(sys.argv)
    app.setApplicationName("吉他谱查看器")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
