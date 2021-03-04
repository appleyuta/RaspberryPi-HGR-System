# RaspberryPi-HGR-System
Raspberry Pi4を用いたジェスチャ家電操作システムです。
PC版は[こちら](https://github.com/appleyuta/Hand-Gesture-Recognition)。

## セットアップ
Raspberry Pi4における本アプリケーションのセットアップ手順を説明する。

1. Raspberry Pi4にRaspberryPi OSをインストールする

2. LXTerminalを開き、以下のコマンドを実行する
```
sudo apt update
sudo apt upgrade -y
sudo apt install python3-tk python3-pil.imagetk -y
sudo apt install libportaudio2 libasound2-dev -y
sudo apt install libatlas-dev -y
```

3. pip3を最新版にアップデートする
```
sudo pip3 install --upgrade pip
```

4. requirements.txtに書かれているライブラリをインストールする
```
pip3 install -r "requirements.txt"
```

5. tflite_runtimeをインストールする
```
pip3 install --extra-index-url https://google-coral.github.io/py-repo/ tflite-runtime
```

6. アプリケーションを実行する
```
python3 guiapp.py
```

## デモ
Raspberry Pi4を用いた家電操作実行デモ

![tv](https://github.com/appleyuta/RaspberryPi-HGR-System/tree/main/demo/tv_demo.gif)

![radio](https://github.com/appleyuta/RaspberryPi-HGR-System/tree/main/demo/radio_demo.gif)

![light](https://github.com/appleyuta/RaspberryPi-HGR-System/tree/main/demo/light_demo.gif)

![aircon](https://github.com/appleyuta/RaspberryPi-HGR-System/tree/main/demo/aircon_demo.gif)


実行デモのように家電を操作するためには、irMagician(大宮技研)をRaspberry Pi4に接続する必要がある。