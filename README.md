# RaspberryPi-HGR-System
Raspberry Pi4を用いたジェスチャ家電操作システムです。
PC版は[こちら](https://github.com/appleyuta/Hand-Gesture-Recognition)。

## 使用するハードウェア
本システムで必須となるハードウェアは以下の3つである。

1. Raspberry Pi4 (4GB,8GBモデル推奨)

2. Raspberry Pi Camera Module (USBカメラではシステムの動作を保証できません)

3. irMagician (赤外線信号による家電操作のため)

上記に加えて、以下の機材のいずれかが必要です。

4. Raspberry Piに接続するモニター (ジェスチャ画面を見て操作する場合)

5. Raspberry Piに接続するスピーカー (音声サポートを使用して操作する場合)

## Raspberry Pi Camera Moduleの設定

1. Raspberry Piのメニューボタンから設定を選択

2. Raspberry Piの設定を選択

3. インターフェイスを選択

4. カメラを有効にしてOKボタンを押す

5. 再起動を要求されるので再起動する

## セットアップ
Raspberry Pi4における本アプリケーションのセットアップ手順を説明する。

1. Raspberry Pi4にRaspberryPi OSをインストールする  
システムを快適に利用するには64bit版OSのインストールを推奨します。

2. LXTerminalを開き、以下のコマンドを実行する
```
sudo apt update
sudo apt upgrade -y
sudo apt install python3-tk python3-pil.imagetk -y
sudo apt install libportaudio2 libasound2-dev -y
sudo apt install libatlas-base-dev -y
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
![tv](https://raw.github.com/wiki/appleyuta/RaspberryPi-HGR-System/demo/tv_demo.gif)  
[音声付き実行デモ(テレビ)](https://drive.google.com/file/d/1s1qNGif82lDRxwMHlbF_nLyt1CB9UhEN/view?usp=sharing)

ラジオ  
![radio](https://raw.github.com/wiki/appleyuta/RaspberryPi-HGR-System/demo/radio_demo.gif)  
[音声付き実行デモ(ラジオ)](https://drive.google.com/file/d/17_MrWGOTZl4V6-CBKR9baaDONod8nfAz/view?usp=sharing)

照明  
![light](https://raw.github.com/wiki/appleyuta/RaspberryPi-HGR-System/demo/light_demo.gif)  
[音声付き実行デモ(照明)](https://drive.google.com/file/d/1AMNmwWAQx4k3uAjHc9ooJVMLYlVAi2QY/view?usp=sharing)

エアコン  
![aircon](https://raw.github.com/wiki/appleyuta/RaspberryPi-HGR-System/demo/aircon_demo.gif)  
[音声付き実行デモ(エアコン)](https://drive.google.com/file/d/1Vg5cv_YjNdHtDIUxkVzP2FJbDGfUzujT/view?usp=sharing)


実行デモのように家電を操作するためには、irMagician(大宮技研)をRaspberry Pi4に接続する必要がある。


## 使用したネットワーク
このアプリケーションで使用したネットワークについて解説する。  
YOLOv3をベースにRaspberry Piで高速で実行できるようにアーキテクチャを改善した。  
YOLOv3は物体検出に有用となる特徴量を抽出するBackboneと、Backboneで得られた特徴量を基に物体を検出するHeadに分けられる。

YOLOv3の公式実装は以下のようになる。  
Backbone : Darknet53  
Head : Standard Convolution

これらを以下のように変更したネットワークを提案する。  
Backbone : **MobileNetV3-Small**  
Head : **Depthwise Separable Convolution**

また公式実装の入力サイズは416x416であるが、これを224x224に変更した。

提案したネットワークを**M**obile**N**etV3-**S**mall **Y**OLOv3を省略し**MNSY**と呼称する。

## MNSYの有効性
MNSYと代表的なネットワークの比較を以下に示す。  
mAPに関してはCOCO mAPを使用し、学習データは[Creative Senz3d Dataset](https://lttm.dei.unipd.it/downloads/gesture/)及び自前で集めた画像、合計33,000枚を用いた。Tensorflowでモデルを学習させ、Tensorflow Liteに変換してRaspberry Pi上で実行を行った。

|Model|Params|Model Size|mAP|Inference Speed|
|:---|:---|:---|:---|:---|
|MNSY|2.4M|4.58MB|80.86|14.25fps|
|Tiny-YOLOv4|5.9M|11.2MB|81.14|4.51fps|
|Tiny-YOLOv3|8.7M|16.5MB|80.21|4.38fps|
|EfficientDet-D0|3.9M|16.3MB|**85.06**|0.79fps|
|MobileNetV3-Small|**1.3M**|**2.57MB**|42.56|**17.63fps**|
|MobileNetV2|3.0M|5.68MB|62.19|11.89fps|
|MobileNet|3.8M|7.29MB|57.53|10.77fps|
|NasNetMobile|4.9M|9.56MB|61.87|6.40fps|

Tiny-YOLOv4はMNSYと比較して精度が僅か0.28%だけ高くなっているが、パラメータ数、モデルサイズ、速度においてはMNSYが大きく上回っている。  
MNSYはパラーメータ数、モデルサイズ、精度、速度のすべてでTiny-YOLOv3を上回っている。  
EfficientDet-D0はMNSYと比べて精度が4.2%高くなっているが、実行速度が著しく低下している。  
MobileNetV3-SmallはMNSYと比べて高速で実行可能であるが、精度が著しく低下している。  
以上のことから、MNSYは速度と精度の両立を実現したネットワークであり、様々な用途での応用が期待できる。