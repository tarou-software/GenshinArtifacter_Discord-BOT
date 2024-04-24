# ライブラリ読み込み
import discord
from discord import app_commands
import random
import os
import datetime
from datetime import timedelta
import json
from dotenv import load_dotenv
import requests #enka.network(ネット上)からユーザーデータ(ファイル)を取得するためのライブラリ

# スコア計算するファイルをインポート
import score_calculation

#ローカルJSONファイル読み込み関数
import codecs,json
def read_json(path):
    with codecs.open(path,encoding='utf-8') as f:
        data = json.load(f)
    return data
#ローカルJSONファイル書き込み関数
def write_json(path,data):
    json_data = json.dumps(data)
    json_1 = codecs.open(path,'w','utf-8')
    json_1.write(json_data)
    json_1.close()

# コンフィグファイル読み込み
config = read_json('./config.json')

# 環境変数読み込み
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# APIアクセス制限(キャッシュ)
usr_info_ttl = {}
player_api_cache = {}

# 計算用一時保存辞書型
calc_save = {}

intents = discord.Intents.default()#適当に。
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Bot起動時に呼び出される関数
@client.event
async def on_ready():
    print(f'Ready! Name:{client.user}')
    await client.change_presence(activity=discord.Game(name="Genshin Impact"))
    await tree.sync()

# アバウトコマンド(このBOTに関する説明)
@tree.command(name="about",description="このBOTに関する説明。")
async def about_command(interaction: discord.Interaction):
    await interaction.response.send_message("このBOTはArtifacterImageGenをDiscord上で利用することができるBOTです。\nこのBOTのソースコードはgithub上で公開されており、誰でも簡単に利用することができます。\nGithubのURL: https://github.com/tarou-software/GenshinArtifacter_Discrord-BOT",ephemeral=True)

# ヘルプコマンド(コマンドに関する説明)
@tree.command(name="help",description="コマンドに関する説明を表示します。")
async def help_command(interaction: discord.Interaction, command:str):
    if(command == None):
        embed=discord.Embed(title='コマンドの説明')
        embed.add_field(name='/helpのあとにコマンド名を入力することで、説明を見ることができます。', value='例: /help build')
        embed.add_field(name='/help listコマンドを実行することでコマンド一覧を表示できます。')
        embed.set_footer('最終更新 2023/06/26')
        await interaction.response.send_message(embed=embed)
    if(command == 'list'):
        embed=discord.Embed(title='コマンド一覧')
        embed.add_field(name='/build', value='聖遺物スコアを計算し、画像を生成します。')
        embed.add_field(name='/build_self', value='UIDを手動で入力して画像を生成します。')
        embed.add_field(name='/uid_submit', value='UIDを登録・再登録します。')
        embed.add_field(name='/submit_uid_check', value='登録しているUIDを確認します。')
        #embed.add_field(name='/', value='')
        embed.set_footer('最終更新 2023/09/01')
    if(command == 'build'):
        embed=discord.Embed(title='buildコマンド', description='聖遺物スコアを計算し、画像を生成します。')
        embed.add_field(name='大まかな説明', value='聖遺物のスコア画像を生成するコマンドです。')
        embed.add_field(name='注意点', value='既にUIDを登録しているユーザーは別のUIDを利用するには/build_selfコマンドを利用してください。')
        embed.set_footer('最終更新 2023/09/01')
    if(command == 'uid_submit'):
        embed=discord.Embed(title='uid_submitコマンド', description='UIDを登録・再登録します。')
        embed.add_field(name='大まかな説明', value='UIDを登録するコマンドです。')
        embed.add_field(name='注意点', value='存在しないUIDは登録できません。')
        embed.set_footer('最終更新 2023/06/26')
    if(command == 'submit_uid_check'):
        embed=discord.Embed(title='submit_uid_checkコマンド', description='登録しているUIDを確認します。')
        embed.add_field(name='大まかな説明', value='登録しているUIDを確認するコマンドです。')
        embed.set_footer('最終更新 2023/06/26')
    if(command == 'build_self'):
        embed=discord.Embed(title='build_selfコマンド', description='UIDを手動で入力して画像を生成します。')
        embed.add_field(name='大まかな説明', value='登録しているUIDを確認するコマンドです。')
        embed.add_field(name='注意点', value='通常は/buildコマンドを使用してください。')
        embed.set_footer('最終更新 2023/09/01')
    #if(command == ''):

# APIサーバのステータス
def check_enka_status(uid):
    # キャッシュが有効かチェック
    now = datetime.datetime.now()
    if((f'{uid}' not in usr_info_ttl) or (now > usr_info_ttl[f'{uid}'])):
        # APIにアクセス
        print("[APIStatusGET]GET_API")
        bot_ver = config["BOT_Ver"]
        Administrator_Name = config["Administrator_Name"]
        headers = { 'User-Agent': f'GenshinArtifacter_Discrord-BOT_Ver{bot_ver}(Administrator: {Administrator_Name})' }
        r = requests.get(f'https://enka.network/api/uid/{uid}/', headers=headers)
        player_api_cache[f'{uid}'] = {}
        player_api_cache[f'{uid}']['status_code'] = int(r.status_code)
        if(r.status_code == 200):
            return 'OK'
        if(r.status_code == 400):
            return 'Invalid_UID'
        if(r.status_code == 404):
            return 'Not_Found_Player'
        if(r.status_code == 424):
            return 'Maintenance'
        if(r.status_code == 429):
            return 'Rate_Limit'
        if(r.status_code == 500):
            return 'Server_Error'
        if(r.status_code == 503):
            return 'Server_Pause'
    else:
        print("[APIStatusGET]Return_cache")
        return 'OK'

# 元素から16進数カラーコード
def conv_color_element_character(character_id):
    character_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json')# キャラクター関連の情報JSON
    character_json = character_json_ori.json()# JSON形式から変換
    character_element = character_json[character_id]['Element']
    # 配色参考
    # HoyoLab(https://www.hoyolab.com/article/14008044)
    if(character_element == 'Fire'):
        return 0xFF6F63 # 炎元素
    if(character_element == 'Water'):
        return 0x4C92EA # 水元素
    if(character_element == 'Wind'):
        return 0x4CD9C8 # 風元素
    if(character_element == 'Electric'):
        return 0xC773FF # 雷元素
    if(character_element == 'Grass'):
        return 0x7AD84C # 草元素
    if(character_element == 'Ice'):
        return 0x73CCFF # 氷元素
    if(character_element == 'Rock'):
        return 0xE6B322 # 岩元素

# UIDからプレイヤー情報のデータを取得
def usr_info_request(uid):
    # キャッシュが有効かチェック
    now = datetime.datetime.now()
    if((f'{uid}' not in usr_info_ttl) or (now > usr_info_ttl[f'{uid}'])):
        # APIにアクセス
        print("[PlayerInfoGET]GET_API")
        bot_ver = config["BOT_Ver"]
        Administrator_Name = config["Administrator_Name"]
        headers = { 'User-Agent': f'GenshinArtifacter_Discrord-BOT_Ver{bot_ver}(Administrator: {Administrator_Name})' }
        usr_info_json_ori = requests.get(f'https://enka.network/api/uid/{uid}/', headers=headers)
        # API応答チェック
        if(usr_info_json_ori.status_code == 200):
            # 成功
            # キャッシュ時間保存
            usr_info_ttl[f'{uid}'] = usr_info_json_ori.json()
            usr_info_ttl[f'{uid}'] = usr_info_ttl[f'{uid}']['ttl']
            usr_info_ttl[f'{uid}'] = now + timedelta(seconds=int(usr_info_ttl[f'{uid}']))
            # キャッシュ保存
            player_api_cache[f'{uid}'] = {}# キャッシュ削除
            player_api_cache[f'{uid}']['status_code'] = usr_info_json_ori.status_code# ステータスコード保存
            player_api_cache[f'{uid}']['api_data'] = usr_info_json_ori.json()# JSONデータ保存
            return usr_info_json_ori.json()# JSON形式から変換
        if(usr_info_json_ori.status_code == 400):
            return 'Invalid_UID'
        if(usr_info_json_ori.status_code == 404):
            return 'Not_Found_Player'
        if(usr_info_json_ori.status_code == 424):
            return 'Maintenance'
        if(usr_info_json_ori.status_code == 429):
            return 'Rate_Limit'
        if(usr_info_json_ori.status_code == 500):
            return 'Server_Error'
        if(usr_info_json_ori.status_code == 503):
            return 'Server_Pause'
    else:
        # キャッシュを返す
        print("[PlayerInfoGET]Return_cache")
        return player_api_cache[f'{uid}']['api_data']


# UIDからプレイヤー情報のembedを作成
def usr_info_embed_gene(uid, user_id):
    get_enka_status = check_enka_status(f'{uid}')
    if(get_enka_status != 'OK'):
        if(get_enka_status == 'Invalid_UID'):
            embed=discord.Embed(title='不正なUIDが入力されました。', description='UIDが正しいか確認してください。')
            embed.set_footer(text='Genshin_Image_Generator_BOT')
            return embed
        if(get_enka_status == 'Not_Found_Player'):
            embed=discord.Embed(title='プレイヤーが見つかりません。', description='UIDが正しいか確認してください。')
            embed.set_footer(text='Genshin_Image_Generator_BOT')
            return embed
        if(get_enka_status == 'Maintenance'):
            embed=discord.Embed(title='enka.networkがメンテナンス中です！', description='UIDの確認ができないため、メンテナンス終了後に再度お試しください。')
            embed.set_footer(text='Genshin_Image_Generator_BOT')
            return embed
    else:
        # プレイヤー情報を取得
        usr_info_json = calc_save[f'{user_id}']['player_info_data']# JSON形式から変換
        name_data_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json')# アイテムなどの名前関連の情報JSON
        name_data_json = name_data_json_ori.json()# JSON形式から変換
        # アイコンのURLを取得
        ## アイコンにしているキャラクターの名前IDを取得
        character_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json')# キャラクター関連の情報JSON
        character_json = character_json_ori.json()# JSON形式から変換
        ## 新形式IDリストを取得
        character_new_id_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/pfps.json')# 新形式のキャラクターIDの情報JSON
        character_new_id_json = character_new_id_json_ori.json()# JSON形式から変換
        # アイコンのIDの形式チェック(旧型式と新形式)#id
        if('avatarId' in usr_info_json['playerInfo']['profilePicture']):
            # 旧型式
            icon_avatar_id = usr_info_json['playerInfo']['profilePicture']['avatarId']
            character_side_icon_name = character_json[f'{icon_avatar_id}']['SideIconName']
            character_icon_name = character_side_icon_name.replace('_Side', '')
        if('id' in usr_info_json['playerInfo']['profilePicture']):
            # 新形式
            icon_avatar_new_id = usr_info_json['playerInfo']['profilePicture']['id']
            character_side_icon_name = character_new_id_json[f'{icon_avatar_new_id}']['iconPath']
            character_icon_name = character_side_icon_name.replace('_Circle','')
        ## URL生成
        icon_link = f'https://enka.network/ui/{character_icon_name}.png'
        # ネームカードのURLを取得
        namecard_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/namecards.json')# ネームカード関連の情報JSON
        namecard_json = namecard_json_ori.json()# JSON形式から変換
        namecard_id = usr_info_json['playerInfo']['nameCardId']
        namecard_image_id = namecard_json[f'{namecard_id}']['icon']
        namecard_link = f'https://enka.network/ui/{namecard_image_id}.png'
        # 各種情報を変数へ
        usr_name = usr_info_json['playerInfo']['nickname']
        if("signature" in usr_info_json['playerInfo']):
            usr_sign = usr_info_json['playerInfo']['signature']
        if("signature" not in usr_info_json['playerInfo']):
            usr_sign = 'ステータスメッセージなし'
        ## 深境螺旋
        usr_towerFloorIndex = usr_info_json['playerInfo']['towerFloorIndex']
        usr_towerLevelIndex = usr_info_json['playerInfo']['towerLevelIndex']
        usr_finishAchievement = usr_info_json['playerInfo']['finishAchievementNum']
        usr_tower_text = f'{usr_towerFloorIndex}層 {usr_towerLevelIndex}間'
        ## 冒険・世界ランク
        usr_level = usr_info_json['playerInfo']['level']
        usr_worldLevel = usr_info_json['playerInfo']['worldLevel']
        usr_info_text = f'冒険ランク{usr_level}・世界ランク{usr_worldLevel}'
        # embed作成(デザインはGenshinJapanのBOTを参考)(embed_usr_info)
        embed_usr_info=discord.Embed(title=usr_name,description=usr_sign)# 名前とステメを表示
        embed_usr_info.add_field(name="螺旋",value=f'{usr_tower_text}',inline=True)
        embed_usr_info.add_field(name="アチーブメント",value=f'{usr_finishAchievement}',inline=True)
        embed_usr_info.set_thumbnail(url=icon_link)# アイコンを表示
        embed_usr_info.set_image(url=namecard_link)# 名刺を表示
        embed_usr_info.set_footer(text=f'{usr_info_text}')# フッターとして指定することで、画像の下にテキストを表示できる
        return embed_usr_info

# 計算方法選択メニュー
class Calc_Type_Select_Menu(discord.ui.View):
    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder="計算方法を選択",
        options=[
            discord.SelectOption(value='FIGHT_PROP_ATTACK_PERCENT', label='攻撃力%', description='攻撃力% + 会心率×2 + 会心ダメージ'),
            discord.SelectOption(value='FIGHT_PROP_CHARGE_EFFICIENCY', label='元チャ効率', description='元チャ効率% + 会心率×2 + 会心ダメージ'),
            discord.SelectOption(value='FIGHT_PROP_CHARGE_EFFICIENCY_V2', label='元チャ効率 ver2', description='元チャ効率%×0.9 + 会心率×2 + 会心ダメージ'),
            discord.SelectOption(value='FIGHT_PROP_DEFENSE_PERCENT', label='防御力%', description='防御力% + 会心率×2 + 会心ダメージ'),
            discord.SelectOption(value='FIGHT_PROP_DEFENSE_PERCENT_V2', label='防御力% ver2', description='防御力%×0.8 + 会心率×2 + 会心ダメージ'),
            discord.SelectOption(value='FIGHT_PROP_HP_PERCENT', label='HP%', description='HP% + 会心率×2 + 会心ダメージ'),
            discord.SelectOption(value='FIGHT_PROP_ELEMENT_MASTERY', label='元素熟知', description='(元素熟知 + 会心率×2 + 会心ダメージ)÷2'),
            discord.SelectOption(value='FIGHT_PROP_ELEMENT_MASTERY_V2', label='元素熟知 ver2', description='元素熟知×0.25 + 会心率×2 + 会心ダメージ'),
        ],
    )
    async def selectMenu(self, interaction: discord.Interaction, select: discord.ui.Select):
        # 一時的に変数に代入
        uid = calc_save[f'{interaction.user.id}']['uid']
        character_id = calc_save[f'{interaction.user.id}']['select_character']
        calculation_type = str(select.values[0])
        await interaction.response.defer(ephemeral=True)
        score_calculation.image_gene(f'{uid}',f'{character_id}',f'{calculation_type}',player_api_cache[f'{uid}']['api_data'])
        # キャラクター情報JSON
        character_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json')
        character_json = character_json_ori.json()# JSON形式から変換
        # アイテムなどの名前関連の情報JSON
        name_data_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json')
        name_data_json = name_data_json_ori.json()# JSON形式から変換
        character_name_hash = character_json[f'{character_id}']['NameTextMapHash']
        character_name = name_data_json['ja'][f'{character_name_hash}']
        embed_image=discord.Embed(title=character_name, color=conv_color_element_character(character_id))
        fname="Image.png"
        # 画像にUIDをつけるかどうかの設定に合わせて参照画像変更
        if(config["image_uid_mode"] == True):
            file = discord.File(fp=f'./ArtifacterImageGen/Tests/Image_{uid}.png',filename=fname,spoiler=False)
        else:
            if(config["image_uid_mode"] == False):
                file = discord.File(fp=f'./ArtifacterImageGen/Tests/Image.png',filename=fname,spoiler=False)
        embed_image.set_image(url=f"attachment://{fname}")
        await interaction.delete_original_response()
        await interaction.followup.send(file=file, embed=embed_image, ephemeral=True)
        #await interaction.edit_original_response(file=file, embed=embed_image)

# キャラ選択メニュー
class Character_Select_Menu(discord.ui.View):
    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder="キャラクターを選択"
    )
    async def selectMenu(self, interaction: discord.Interaction, select: discord.ui.Select):
        # 詳細公開中か確認
        ## プレイヤー情報を取得
        usr_info_json = calc_save[f'{interaction.user.id}']['player_info_data']# JSON形式から変換
        if("avatarInfoList" in usr_info_json):
            # 詳細公開中の場合
            # 選択キャラ一時保存
            calc_save[f'{interaction.user.id}']['select_character'] = str(select.values[0])
            # 聖遺物計算方法選択メニュー
            calc_type_select = Calc_Type_Select_Menu()
            #await interaction.response.send_message('計算方法を選択してください。', view=calc_type_select, ephemeral=True)
            await interaction.response.edit_message(content='計算方法を選択してください。',embed=None, view=calc_type_select)
        if("avatarInfoList" not in usr_info_json):
            # 詳細非公開の場合
            embed=discord.Embed(title='キャラクター詳細取得失敗',description='キャラクターの詳細を公開中にしてください。\nもしくは、キャラクターをプロフィールに設定してください。')
            embed.set_footer(text='Genshin_Image_Generator_BOT')
            await interaction.response.edit_message(embed=embed)

# UIDからキャラクターの選択メニュー生成
def character_select_menu_gene(user_id):
    # プレイヤー情報を取得
    usr_info_json = calc_save[f'{user_id}']['player_info_data']# JSON形式から変換
    # 名前翻訳JSON
    name_data_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json')# アイテムなどの名前関連の情報JSON
    name_data_json = name_data_json_ori.json()# JSON形式から変換
    # キャラクター関連のJSON
    character_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json')# キャラクター関連の情報JSON
    character_json = character_json_ori.json()# JSON形式から変換
    # キャラクターの選択メニューを作成
    character_select = Character_Select_Menu()
    # プロフィールにキャラクターが設定されているかどうか確認
    if("showAvatarInfoList" in usr_info_json["playerInfo"]):
        for character_id in usr_info_json['playerInfo']['showAvatarInfoList']:
            list_character_id = character_id['avatarId']
            list_character_level = character_id['level']
            character_name_hash = character_json[f'{list_character_id}']['NameTextMapHash']
            character_name = name_data_json['ja'][f'{character_name_hash}']
            character_select.selectMenu.add_option(
                label=character_name,
                value=list_character_id,
                description=f'Lv{list_character_level}'
            )
    if("showAvatarInfoList" not in usr_info_json["playerInfo"]):
        character_select.selectMenu.add_option(label='キャラクターなし', description='プロフィールにキャラクターが設定されていません。')
    return character_select

# UID登録フォーム作成
class register_uid(discord.ui.Modal, title='UID登録'):
    uid = discord.ui.TextInput(label='uid', placeholder='00000000', required=True, min_length=9, max_length=9, style=discord.TextStyle.short)

    # UID入力後動作
    async def on_submit(self, interaction: discord.Interaction):
        get_enka_status = check_enka_status(f'{self.uid}')
        if(get_enka_status != 'OK'):
            if(get_enka_status == 'Invalid_UID'):
                embed=discord.Embed(title='不正なUIDが入力されました。', description='UIDが正しいか確認してください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
            if(get_enka_status == 'Not_Found_Player'):
                embed=discord.Embed(title='プレイヤーが見つかりません。', description='UIDが正しいか確認してください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
            if(get_enka_status == 'Maintenance'):
                embed=discord.Embed(title='enka.networkがメンテナンス中です！', description='UIDの確認ができないため、メンテナンス終了後に再度お試しください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
        else:
            uid_list = read_json('./uid_list.json')
            uid_list[f'{interaction.user.id}'] = f'{self.uid}'
            write_json('./uid_list.json',uid_list)
            embed=discord.Embed(title='UID登録完了',description='再度/buildコマンドを実行してください。')
            embed.add_field(name='uid',value=f'{self.uid}')
            embed.set_footer(text='Genshin_Image_Generator_BOT')
        await interaction.response.send_message(embed=embed, ephemeral=True)

# UID取得フォーム作成
class Form_uid(discord.ui.Modal, title='UID入力'):
    uid = discord.ui.TextInput(label='uid', placeholder='000000000', required=True, min_length=9, max_length=9, style=discord.TextStyle.short)

    # UID入力後動作
    async def on_submit(self, interaction: discord.Interaction):
        get_enka_status = check_enka_status(f'{self.uid}')
        if(get_enka_status != 'OK'):
            if(get_enka_status == 'Invalid_UID'):
                embed=discord.Embed(title='不正なUIDが入力されました。', description='UIDが正しいか確認してください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
            if(get_enka_status == 'Not_Found_Player'):
                embed=discord.Embed(title='プレイヤーが見つかりません。', description='UIDが正しいか確認してください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
            if(get_enka_status == 'Maintenance'):
                embed=discord.Embed(title='enka.networkがメンテナンス中です！', description='UIDの確認ができないため、メンテナンス終了後に再度お試しください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # 待ってもらう
            await interaction.response.defer(ephemeral=True)
            # UIDの一時保存
            calc_save[f'{interaction.user.id}'] = {}
            calc_save[f'{interaction.user.id}']['uid'] = self.uid
            # プレイヤー情報の一次保存
            calc_save[f'{interaction.user.id}']['player_info_data'] = usr_info_request(self.uid)
            # ユーザー情報生成
            embed_usr_info = usr_info_embed_gene(f'{self.uid}', interaction.user.id)
            # キャラクター選択メニュー生成
            character_select = character_select_menu_gene(interaction.user.id)
            # 送信
            #await interaction.response.send_message(view=character_select, embed=embed_usr_info, ephemeral=True)
            await interaction.followup.send(view=character_select, embed=embed_usr_info, ephemeral=True)

# ビルドコマンド実行時、uid未登録者へのUID登録促し時に使うボタン
## 登録
class uid_submit_button(discord.ui.Button):
    def __init__(self, *, style: discord.ButtonStyle = discord.ButtonStyle.secondary, label: str = "登録する"):
        super().__init__(style=style, label=label)
    async def callback(self, interaction: discord.Interaction):
        modal = register_uid()
        await interaction.response.send_modal(modal)
        await modal.wait()

## 登録しない
class uid_not_submit_button(discord.ui.Button):
    def __init__(self, *, style: discord.ButtonStyle = discord.ButtonStyle.secondary, label: str = "登録しない"):
        super().__init__(style=style, label=label)
    async def callback(self, interaction: discord.Interaction):
        modal = Form_uid()
        await interaction.response.send_modal(modal)
        await modal.wait()

# ビルドコマンド
@tree.command(name="build",description="聖遺物スコアを計算し、画像を生成します。")
async def build_command(interaction:discord.Interaction):
    if(config['uid_register'] == True):
        uid_list = read_json('./uid_list.json')
        if(f'{interaction.user.id}' in uid_list):
            await interaction.response.defer(ephemeral=True)
            calc_save[f'{interaction.user.id}'] = {}
            calc_save[f'{interaction.user.id}']['uid'] = uid_list[f'{interaction.user.id}']
            # プレイヤー情報の一次保存
            temp = usr_info_request(uid_list[f'{interaction.user.id}'])
            if(temp == 'Invalid_UID'):
                embed=discord.Embed(title='不正なUIDが入力されました。', description='UIDが正しいか確認してください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
                await interaction.followup.send(embed=embed, ephemeral=True)
            elif(temp == 'Maintenance'):
                embed=discord.Embed(title='enka.networkがメンテナンス中です！', description='UIDの確認ができないため、メンテナンス終了後に再度お試しください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
                await interaction.followup.send(embed=embed, ephemeral=True)
            elif(temp == 'Not_Found_Player'):
                embed=discord.Embed(title='プレイヤーが見つかりません。', description='UIDが正しいか確認してください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
                await interaction.followup.send(embed=embed, ephemeral=True)
            elif(temp == 'Rate_Limit'):
                embed=discord.Embed(title='アクセス数が多いです。', description='時間をおいて再度お試しください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
                await interaction.followup.send(embed=embed, ephemeral=True)
            elif(temp == 'Server_Error'):
                embed=discord.Embed(title='サーバーエラー', description='もう一度お試しください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
                await interaction.followup.send(embed=embed, ephemeral=True)
            elif(temp == 'Server_Pause'):
                embed=discord.Embed(title='サーバーポーズ', description='時間をおいて再度お試しください。')
                embed.set_footer(text='Genshin_Image_Generator_BOT')
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                calc_save[f'{interaction.user.id}']['player_info_data'] = usr_info_request(uid_list[f'{interaction.user.id}'])
                embed_usr_info = usr_info_embed_gene(uid_list[f'{interaction.user.id}'], interaction.user.id)
                character_select = character_select_menu_gene(interaction.user.id)
                #await interaction.response.send_message(view=character_select, embed=embed_usr_info, ephemeral=True)
                await interaction.followup.send(view=character_select, embed=embed_usr_info, ephemeral=True)
        else:
            # UID登録促し埋め込み作成
            embed = discord.Embed(title='UID登録ができます！',description='UIDの登録をすることで次回からUIDの入力が不要になります！')
            embed.set_footer(text='Genshin_Image_Generator_BOT')
            # 登録する/しないボタン表示準備
            view = discord.ui.View()
            view.add_item(uid_submit_button(style=discord.ButtonStyle.primary))
            view.add_item(uid_not_submit_button(style=discord.ButtonStyle.grey))
            await interaction.response.send_message(view=view,embed=embed, ephemeral=True)
    if(config['uid_register'] == False):
        modal = Form_uid()
        await interaction.response.send_modal(modal)

# UID手動入力
@tree.command(name="build_self",description="UIDを手動で入力して画像を生成できます。")
async def build_uid_no(interaction:discord.Interaction):
    modal = Form_uid()
    await interaction.response.send_modal(modal)

# UID登録コマンド
@tree.command(name="uid_submit",description="UIDを登録・再登録します。")
async def uid_submit(interaction:discord.Interaction):
    modal = register_uid()
    await interaction.response.send_modal(modal)

# 登録UID確認コマンド
@tree.command(name="submit_uid_check",description='登録しているUIDを確認します。')
async def submit_uid_check(interaction:discord.Interaction):
    # UIDリスト読み込み
    uid_list = read_json('./uid_list.json')
    # 登録確認
    if(f'{interaction.user.id}' in uid_list):
        your_uid = uid_list[f'{interaction.user.id}']
    if(f'{interaction.user.id}' not in uid_list):
        your_uid = '登録されていません'
    # embed作成
    embed = discord.Embed(title='登録UID確認')
    embed.add_field(name='UID',value=f'{your_uid}')
    embed.set_footer(text='Genshin_Image_Generator_BOT')
    # embed送信
    await interaction.response.send_message(embed=embed, ephemeral=True)

# BOT停止コマンド(管理者権限必須)
@tree.command(name="bot_stop",description="Botを停止。管理者権限必須")
@app_commands.default_permissions(administrator=True)
async def bot_stop(interaction:discord.Interaction):
    await interaction.response.send_message("Botを停止します。", ephemeral=True)
    await client.close()

client.run(DISCORD_TOKEN)
