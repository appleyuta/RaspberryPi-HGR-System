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

テレビ  
![tv](https://github.com/appleyuta/RaspberryPi-HGR-System/blob/main/demo/tv_demo.gif)  
[音声付き実行デモ(テレビ)](https://drive.google.com/file/d/1s1qNGif82lDRxwMHlbF_nLyt1CB9UhEN/view?usp=sharing)

ラジオ  
![radio](https://github.com/appleyuta/RaspberryPi-HGR-System/blob/main/demo/radio_demo.gif)  
[音声付き実行デモ(ラジオ)](https://drive.google.com/file/d/17_MrWGOTZl4V6-CBKR9baaDONod8nfAz/view?usp=sharing)

照明  
![light](https://github.com/appleyuta/RaspberryPi-HGR-System/blob/main/demo/light_demo.gif)  
[音声付き実行デモ(照明)](https://drive.google.com/file/d/1AMNmwWAQx4k3uAjHc9ooJVMLYlVAi2QY/view?usp=sharing)

エアコン  
![aircon](https://github.com/appleyuta/RaspberryPi-HGR-System/blob/main/demo/aircon_demo.gif)  
[音声付き実行デモ(エアコン)](https://drive.google.com/file/d/1Vg5cv_YjNdHtDIUxkVzP2FJbDGfUzujT/view?usp=sharing)


実行デモのように家電を操作するためには、irMagician(大宮技研)をRaspberry Pi4に接続する必要がある。