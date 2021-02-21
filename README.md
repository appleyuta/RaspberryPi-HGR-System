# RaspberryPi-HGR-System
Raspberry Pi4を用いたジェスチャ家電操作システムです。

## セットアップ
Raspberry Pi4における本アプリケーションのセットアップ手順を説明する。

1. Raspberry Pi4にRaspberryPi OSをインストールする

2. LXTerminalを開き、以下のコマンドを実行する
```
sudo apt update
sudo apt upgrade
sudo apt install python3-tk
```

3. requirements.txtに書かれているライブラリをインストールする
```
pip3 install -r "requirements.txt"
```

4. tflite_runtimeをインストールする
```
pip3 install --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime
```

5. アプリケーションを実行する
```
python3 guiapp.py
```

## デモ
RaspberryPi4を用いた家電操作実行デモ

coming soon