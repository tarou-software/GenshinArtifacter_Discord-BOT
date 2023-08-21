# GenshinArtifacter_Discrord-BOT

# これはなに？

現神の聖遺物のスコアを計算して画像を生成する「ArtifacterImageGen」をDiscord用BOTとして利用できるようにするためのコードです。

私は「ArtifacterImageGen」を元に作成したDiscordBOTを誰でも簡単に使えるように、MITライセンスでコードを配布することにしました。

これは、「ArtifacterImageGen」がgithubでMITライセンスで配布されているおかげです。

Hyugoさんに心から感謝します。

また、「EnkaNetworkAPI」ライブラリがあることで、アセットの更新が容易になりました。

yuko1101に心から感謝します。

githubを使うのはほぼ初めてなので、間違い等あるかもしれません。

間違いがあればご連絡いただけると幸いです。

# 動作環境
Python 3.11.2

Discord.py 2.2.2

python-dotenv 1.0.0

Pillow 9.5.0

PyYAML 6.0

requests 2.28.2

Node.js 18.16.0

npm 9.5.1

# はじめに

`/help`コマンドを実行して、コマンドに関する説明を見てください。

# セットアップ方法

## Windows

<details>
<summary>クリックして開く</summary>

編集中...

</details>

## Linux(Debian もしくは Ubuntu)

<details>
<summary>クリックして開く</summary>

### DiscordBOTの作成

DiscordDeveloperPortalにアクセスします。

https://discord.com/developers/applications

「New Application.」をクリックします。

(すでに専用BOTを作成している場合は、トークン生成まで読み飛ばしてください)

BOTの名称を決め、「NAME」欄に入力する。

利用規約とデベロッパーポリシーに同意し、「Create」をクリックします。

「SETTING」の「BOT」タブを選択し、「Add Bot」をクリックします。

確認ダイアログが表示されたら、「Yes, do it!」をクリックします。

(2FAが設定されている場合は、認証してください)。

### トークン生成

「TOKEN」の下にある「Copy」をクリックして、BOTトークンをコピーします。

このトークンをメモ帳などにメモ（ペースト）しておく。

このトークンは、流出しないように注意してください。

### BOTのゲートウェイ設定

「Privileged Gateway Intents」の「PRESENCE INTENT」、「SERVER MEMBERS INTENT」、「MESSAGE CONTENT INTENT」3つすべてをONにします。

変更を保存するには、忘れずに「Save Changes」をクリックしてください。

### ボットによるサーバーへの参加を許可する

メニューから「OAuth2」→「URL Generator」を選択します。

「SCOPES」の「BOT」にチェックを入れ、「BOT PERMISSIONS」を必要なパーミッションに設定します。

(サーバーを所有し、本ボットのコードを信頼している場合は、「Administrator」チェックボックスをチェックしてもよいと思われます。)

「GENERATED URL」欄に表示されたURLをコピーして、コピーしたURLにアクセスします。

ボットを参加させたいサーバーを選択し、「Yes」をクリックします。

認証が正しいことを確認し、認証をクリックします。

hCaptchaの認証をクリアして、BOTをエンカレッジする。

これで、Discord BOTの事前設定は完了です。

### ソースをダウンロード
このリポジトリをgithubからzipファイルでダウンロードするか、GithubCLIなどでcloneしてください。

https://github.com/tarou-software/GenshinArtifacter_Discrord-BOT

(ZIPファイルでダウンロードされた方は、解凍してください。)

ディレクトリ内の「.env」ファイルを開き、「Please Here Your Discord BOT TOKEN」を「Token Generation」でコピーしたBOTトークンに置き換えます。

### Pythonのセットアップ

バージョンの確認コマンドを実行してpythonがインストールされているかを確認します。

```
python3 --version
```

バージョンが表示されたらOKです。

pipをインストールします。

```
sudo apt update
sudo apt install python3-pip
```

pipを使用して、各ライブラリをインストールします。

コマンドは以下のとおりです。

各種ライブラリをインストールします。
```
pip3 install discord.py
```

```
pip3 install python-dotenv
```

```
pip3 install Pillow
```

```
pip3 install pyyaml
```

```
pip3 install requests
```

すべてが正しくインストールされたことを確認してください。

### コンフィグを変更する

BOTのソースコードが入っているディレクトリ内に、「config.json」というファイルが存在します。

このファイルはBOTの設定を変更するものです。

**起動前に変更する必要がある箇所がある**ので、テキストエディタなどで開きます。

```
"Administrator_Name" : "Please Enter Your Name",
```

という行の「Please Enter Your Name」をあなたのニックネームに変更してください。

これは、EnkaNetworkのAPIを使用するために**必要な設定です**ので**必ず**行ってください。

また、

```
"BOT_Ver" : ~~~,
```

という項目は**変更しないで**ください。

<details>
<summary>任意の設定</summary>

#### uid_register

```
"uid_register" : true,
```

この項目を変更することで、UIDの登録を可能にするかしないかを設定できます。

- 有効にする場合は、「true」
- 無効にする場合は、「false」

に変更してください。

(初期設定は有効の「true」です。)

#### image_uid_mode

```
"image_uid_mode" : true
```

この項目を変更することで、タイミングによっては別の人の画像が送信されるという事態を回避することができます。

- 有効にする場合は、「true」
- 無効にする場合は、「false」

に変更してください。

(初期設定は有効の「true」です。)

</details>

### BOTを起動する

コマンドプロンプトなどを起動します。

カレントディレクトリをソースディレクトリに変更します。

次のコマンドを実行します。

```
python3 bot_start.py
```

(シェルスクリプトファイルを作成することをお勧めします。）

「Ready! Name:~~」と表示され、Discord上でBOTが正常に動作していることを確認してください。

</details>

# アセット更新

ArtifacterImageGenの仕様上、原神のバージョンアップが行われた際に追加される新要素に対応するためにはアセットの更新が必要になります。

## 初期設定

<details>
<summary>クリックして開く</summary>

### Node.jsのインストール

以下のコマンドでLTS版のNode.jsをインストールします。

```
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install nodejs -y
```

### ライブラリのインストール

カレントディレクトリをソースディレクトリに変更します。

次のコマンドを実行します。

```
npm install enka-network-api
```

</details>

## 更新

<details>
<summary>クリックして開く</summary>

**重要**
更新するときは、EnkaNetworkがメンテナンスをしていないことを確認してください。

更新をするには、カレントディレクトリをソースディレクトリに変更し以下のコマンドを実行します。

```
node asset_update.js
```

(シェルスクリプトファイルを作成することをお勧めします。）

実行すると、自動でキャラクター・武器・聖遺物のアセットを更新します。

更新時にBOTの再起動は不要です。

</details>

# 著作権表示

ArtifacterImageGen Copyright (c) Hyugo(FuroBath)

GenshinArtifacter_Discrord-BOT Copyright (c) mendoitarou_

EnkaNetworkAPI(ライブラリ) Copyright (c) yuko1101


# お借り(使用)したもの

[FuroBath/ArtifacterImageGen](https://github.com/FuroBath/ArtifacterImageGen)

[yuko1101/enka-network-api](https://github.com/yuko1101/enka-network-api)

# 翻訳
このREADME-ja.mdは、DeepL翻訳ツールを使用して、日本語から英語に翻訳した後、英語から日本語に翻訳されています。

https://www.deepl.com/ja/translator

# 連絡先

返信に時間がかかる場合がありますので、ご了承ください。

Twitter: [@mendoitarou_](https://twitter.com/mendoitarou_)

E-Mail: [contact@mendoitarou.com](mailto:contact@mendoitarou.com)

# リリースノート

# 1.2.3

<details>
<summary>クリックして開く</summary>

- キャラクターの凸数が表示されない問題を修正

</details>

## 1.2.2

<details>
<summary>クリックして開く</summary>

- 聖遺物をつけていないキャラの画像を生成しようとしたときに、エラーが発生して画像が生成されない問題を修正。

</details>

## 1.2.1

<details>
<summary>クリックして開く</summary>

- BOTに関する情報を確認するコマンド名を変更
- コマンドの説明を見れるコマンドを追加

</details>

## 1.2.0

<details>
<summary>クリックして開く</summary>

- 生成画像キャラの元素に応じて埋め込みの色を変化
- アセット更新プログラムを追加

</details>

## 1.1.0

<details>
<summary>クリックして開く</summary>

- APIのルールに従えていない箇所があったので修正。
- UIDを登録しなかった場合の動作を変更
- 動作変更に伴い、/build_noコマンドの削除
- 画像生成の際、タイミングによっては別ユーザーの画像が生成される可能性がある問題を修正(コンフィグでON/OFF可能)
- 動作変更に伴い、READMEに説明を追記

</details>

## 1.0.0

<details>
<summary>クリックして開く</summary>

- 初期リリース

</details>
