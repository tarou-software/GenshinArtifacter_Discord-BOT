import json
import datetime
from datetime import timedelta
import requests
from decimal import Decimal, ROUND_HALF_UP

#ArtifacterImageGenをインポート
from ArtifacterImageGen import Generater

# コンフィグファイル読み込み
import codecs,json
def read_json(path):
    with codecs.open(path,encoding='utf-8') as f:
        data = json.load(f)
    return data
config = read_json('./config.json')

# APIアクセス制限(キャッシュ)
usr_info_ttl = {}
player_api_cache = {}

# 元素名変換
conv_element_name = {# 並びはロード画面の順番
    'Fire' : '炎',
    'Water' : '水',
    'Wind' : '風',
    'Electric' : '雷',
    'Grass' : '草',
    'Ice' : '氷',
    'Rock' : '岩'
}

# 元素名対応ダメージ表記変換
conv_element_damage = {# 並びはロード画面の順番
    'Fire' : '40',
    'Water' : '42',
    'Wind' : '44',
    'Electric' : '41',
    'Grass' : '43',
    'Ice' : '46',
    'Rock' : '45'
}

# ステータス名変換
conv_status_name = {
    'FIGHT_PROP_HP' : 'HP',
    'FIGHT_PROP_ATTACK' : '攻撃力',
    'FIGHT_PROP_DEFENSE' : '防御力',
    'FIGHT_PROP_HP_PERCENT' : 'HPパーセンテージ',
    'FIGHT_PROP_ATTACK_PERCENT' : '攻撃パーセンテージ',
    'FIGHT_PROP_DEFENSE_PERCENT' : '防御パーセンテージ',
    'FIGHT_PROP_CRITICAL' : '会心率',
    'FIGHT_PROP_CRITICAL_HURT' : '会心ダメージ',
    'FIGHT_PROP_CHARGE_EFFICIENCY' : '元素チャージ効率',
    'FIGHT_PROP_HEAL_ADD' : '与える治癒効果',
    'FIGHT_PROP_ELEMENT_MASTERY' : '元素熟知',
    'FIGHT_PROP_PHYSICAL_ADD_HURT' : '物理ダメージ',
    'FIGHT_PROP_FIRE_ADD_HURT' : '炎元素ダメージ',
    'FIGHT_PROP_ELEC_ADD_HURT' : '雷元素ダメージ',
    'FIGHT_PROP_WATER_ADD_HURT' : '水元素ダメージ',
    'FIGHT_PROP_WIND_ADD_HURT' : '風元素ダメージ',
    'FIGHT_PROP_ICE_ADD_HURT' : '氷元素ダメージ',
    'FIGHT_PROP_ROCK_ADD_HURT' : '岩元素ダメージ',
    'FIGHT_PROP_GRASS_ADD_HURT' : '草元素ダメージ'
}

# ステータス%か否か判別
check_status_percent = {
    'FIGHT_PROP_HP' : 'false',
    'FIGHT_PROP_ATTACK' : 'false',
    'FIGHT_PROP_DEFENSE' : 'false',
    'FIGHT_PROP_HP_PERCENT' : 'true',
    'FIGHT_PROP_ATTACK_PERCENT' : 'true',
    'FIGHT_PROP_DEFENSE_PERCENT' : 'true',
    'FIGHT_PROP_CRITICAL' : 'true',
    'FIGHT_PROP_CRITICAL_HURT' : 'true',
    'FIGHT_PROP_CHARGE_EFFICIENCY' : 'true',
    'FIGHT_PROP_HEAL_ADD' : 'true',
    'FIGHT_PROP_ELEMENT_MASTERY' : 'false',
    'FIGHT_PROP_PHYSICAL_ADD_HURT' : 'true',
    'FIGHT_PROP_FIRE_ADD_HURT' : 'true',
    'FIGHT_PROP_ELEC_ADD_HURT' : 'true',
    'FIGHT_PROP_WATER_ADD_HURT' : 'true',
    'FIGHT_PROP_WIND_ADD_HURT' : 'true',
    'FIGHT_PROP_ICE_ADD_HURT' : 'true',
    'FIGHT_PROP_ROCK_ADD_HURT' : 'true',
    'FIGHT_PROP_GRASS_ADD_HURT' : 'true'
}

# 計算形式辞書
score_cal_type_name = {
    'FIGHT_PROP_ATTACK_PERCENT' : '攻撃パーセンテージ',
    'FIGHT_PROP_CHARGE_EFFICIENCY' : '元チャ効率',
    'FIGHT_PROP_CHARGE_EFFICIENCY_V2' : '元チャ効率 ver2',
    'FIGHT_PROP_DEFENSE_PERCENT' : '防御パーセンテージ',
    'FIGHT_PROP_DEFENSE_PERCENT_V2' : '防御パーセンテージ ver2',
    'FIGHT_PROP_HP_PERCENT' : 'HPパーセンテージ',
    'FIGHT_PROP_ELEMENT_MASTERY' : '元素熟知',
    'FIGHT_PROP_ELEMENT_MASTERY_V2' : '元素熟知 ver2'
}

# 聖遺物種類
reliquary_type_name = {
    'flower' : 'EQUIP_BRACER',
    'wing' : 'EQUIP_NECKLACE',
    'clock' : 'EQUIP_SHOES',
    'cup' : 'EQUIP_RING',
    'crown' : 'EQUIP_DRESS'
}

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

# 聖遺物ステータス
def reliquary_status_dic(character_parth_json,reliquary_info_list,name_data_json,type):
    #### 聖遺物種類
    reliquary_set_name_hash = reliquary_info_list['flat']['setNameTextMapHash']
    character_parth_json['Artifacts'][f'{type}']['type'] = name_data_json['ja'][f'{reliquary_set_name_hash}']
    #### レベル(+??)
    character_parth_json['Artifacts'][f'{type}']['Level'] = reliquary_info_list['reliquary']['level'] - 1#1~21なので1引く
    #### レアリティ
    character_parth_json['Artifacts'][f'{type}']['rarelity'] = reliquary_info_list['flat']['rankLevel']
    #### メインステータス
    character_parth_json['Artifacts'][f'{type}']['main'] = {}
    ##### ステータス名
    reliquary_main_status_id = reliquary_info_list['flat']['reliquaryMainstat']['mainPropId']
    character_parth_json['Artifacts'][f'{type}']['main']['option'] = conv_status_name[f'{reliquary_main_status_id}']
    ##### 値
    character_parth_json['Artifacts'][f'{type}']['main']['value'] = reliquary_info_list['flat']['reliquaryMainstat']['statValue']
     #### サブステータス
    character_parth_json['Artifacts'][f'{type}']['sub'] = []
    for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
        sub_status_name_id = reliquary_sub_status_list['appendPropId']
        sub_status_name = conv_status_name[f'{sub_status_name_id}']
        substatus_value = reliquary_sub_status_list['statValue']
        if(check_status_percent[f'{sub_status_name_id}'] == 'false'):
            substatus_value = int(Decimal(reliquary_sub_status_list['statValue']).quantize(Decimal('1'), ROUND_HALF_UP))
        character_parth_json['Artifacts'][f'{type}']['sub'] += [{
            'option' : sub_status_name,
            'value' : substatus_value
        }]
    return character_parth_json

# スコア計算
def score_calculation(reliquary_info_list,cal_type,reliquary_type):
    substatus_value = {}
    substatus_value['select'] = 0
    substatus_value['critical'] = 0
    substatus_value['critical_hurt'] = 0
    score = 0
    #reliquary_score_list = {}
    if(reliquary_info_list['flat']['itemType'] == 'ITEM_RELIQUARY'):
        for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
            if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_CRITICAL'):
                substatus_value['critical'] = float(reliquary_sub_status_list['statValue'])
            if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_CRITICAL_HURT'):
                substatus_value['critical_hurt'] = float(reliquary_sub_status_list['statValue'])
        if(cal_type == 'FIGHT_PROP_ATTACK_PERCENT'):
            for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
                if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_ATTACK_PERCENT'):
                        substatus_value['select'] += float(reliquary_sub_status_list['statValue'])
                        #攻撃力% + 会心率×2 + 会心ダメージ
            score = substatus_value['select'] + float((substatus_value['critical'] * 2)) + float(substatus_value['critical_hurt'])
        if(cal_type == 'FIGHT_PROP_CHARGE_EFFICIENCY'):
            for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
                if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_CHARGE_EFFICIENCY'):
                    substatus_value['select'] += float(reliquary_sub_status_list['statValue'])
                    #元チャ効率% + 会心率×2 + 会心ダメージ
            score = substatus_value['select'] + float((substatus_value['critical'] * 2)) + float(substatus_value['critical_hurt'])
        if(cal_type == 'FIGHT_PROP_CHARGE_EFFICIENCY_V2'):
            for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
                if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_CHARGE_EFFICIENCY'):
                    substatus_value['select'] += float(reliquary_sub_status_list['statValue'])
                    #元チャ効率%×0.9 + 会心率×2 + 会心ダメージ
            score = float(substatus_value['select'] * 0.9) + float((substatus_value['critical'] * 2)) + float(substatus_value['critical_hurt'])
        if(cal_type == 'FIGHT_PROP_DEFENSE_PERCENT'):
            for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
                if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_DEFENSE_PERCENT'):
                    substatus_value['select'] += float(reliquary_sub_status_list['statValue'])
                    #防御力% + 会心率×2 + 会心ダメージ
            score = substatus_value['select'] + float((substatus_value['critical'] * 2)) + float(substatus_value['critical_hurt'])
        if(cal_type == 'FIGHT_PROP_DEFENSE_PERCENT_V2'):
            for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
                if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_DEFENSE_PERCENT'):
                    substatus_value['select'] += float(reliquary_sub_status_list['statValue'])
                    #防御力%×0.8 + 会心率×2 + 会心ダメージ
            score = float(substatus_value['select'] * 0.8) + float((substatus_value['critical'] * 2)) + float(substatus_value['critical_hurt'])
        if(cal_type == 'FIGHT_PROP_HP_PERCENT'):
            for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
                if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_HP_PERCENT'):
                    substatus_value['select'] += float(reliquary_sub_status_list['statValue'])
                    #HP% + 会心率×2 + 会心ダメージ
            score = substatus_value['select'] + float((substatus_value['critical'] * 2)) + float(substatus_value['critical_hurt'])
        if(cal_type == 'FIGHT_PROP_ELEMENT_MASTERY'):
            for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
                if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_ELEMENT_MASTERY'):
                    substatus_value['select'] += float(reliquary_sub_status_list['statValue'])
                    #(元素熟知 + 会心率×2 + 会心ダメージ)÷2
            score = (substatus_value['select'] + float((substatus_value['critical'] * 2)) + float(substatus_value['critical_hurt'])) / 2
        if(cal_type == 'FIGHT_PROP_ELEMENT_MASTERY_V2'):
            for reliquary_sub_status_list in reliquary_info_list['flat']['reliquarySubstats']:
                if(reliquary_sub_status_list['appendPropId'] == 'FIGHT_PROP_ELEMENT_MASTERY'):
                    substatus_value['select'] += float(reliquary_sub_status_list['statValue'])
                    #元素熟知×0.25 + 会心率×2 + 会心ダメージ
            score = float(substatus_value['select'] * 0.25) + float((substatus_value['critical'] * 2)) + float(substatus_value['critical_hurt'])
    return score

# JSON生成
def score_json_parth(uid,character_id,calt_type,usr_info_cache_json):
    uid = int(uid)
    character_id = int(character_id)
    # ユーザー情報JSON
    #usr_info_json = usr_info_request(uid)
    usr_info_json = usr_info_cache_json
    # キャラクター情報JSON
    character_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json')
    character_json = character_json_ori.json()# JSON形式から変換
    # アイテムなどの名前関連の情報JSON
    name_data_json_ori = requests.get('https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json')
    name_data_json = name_data_json_ori.json()# JSON形式から変換
    # ArtifactorGenに渡すJSONファイル用配列
    character_parth_json = {}# 辞書型変数を初期化
    character_parth_json['uid'] = uid# UID
    character_parth_json['input'] = ''# サンプルに何も入ってなかったので空白に(値を入れても画像に変化なし)
    ## キャラの名前を変換・代入
    character_name_hash = character_json[f'{character_id}']['NameTextMapHash']
    character_name = name_data_json['ja'][f'{character_name_hash}']
    character_parth_json['Character'] = {}
    character_parth_json['Character']['Name'] = character_name
    ## キャラの凸数を変換・代入
    count = 0
    for character_list_id in usr_info_json['avatarInfoList']:
        if(character_list_id['avatarId'] == character_id):
            if('talentIdList' in character_list_id):
                for character_talentIdList in character_list_id['talentIdList']:
                    count = count + 1
    character_parth_json['Character']['Const'] = count
    ## キャラのレベルを取得・代入
    for character_list_id in usr_info_json['playerInfo']['showAvatarInfoList']:
        if(character_list_id['avatarId'] == character_id):
            character_parth_json['Character']['Level'] = character_list_id['level']
    ## キャラのステータス取得・代入
    for character_info_list in usr_info_json['avatarInfoList']:# キャラクターの詳細情報
        if(character_info_list['avatarId'] == character_id):
            # キャラの元素取得
            element_ori_name = character_json[f'{character_id}']['Element']
            element_name = conv_element_name[f'{element_ori_name}']
            # キャラの元素に対応したダメージのプロパティID取得
            element_damage_id = conv_element_damage[f'{element_ori_name}']
            ### キャラの好感度レベルを取得・代入
            character_parth_json['Character']['Love'] = character_info_list['fetterInfo']['expLevel']
            ### HP
            character_parth_json['Character']['Status'] = {}
            character_parth_json['Character']['Status']['HP'] = int(Decimal(character_info_list['fightPropMap']['2000']).quantize(Decimal('1'), ROUND_HALF_UP))
            ### 攻撃力
            character_parth_json['Character']['Status']['攻撃力'] = int(Decimal(character_info_list['fightPropMap']['2001']).quantize(Decimal('1'), ROUND_HALF_UP))
            ### 防御力
            character_parth_json['Character']['Status']['防御力'] = int(Decimal(character_info_list['fightPropMap']['2002']).quantize(Decimal('1'), ROUND_HALF_UP))
            ### 元素熟知
            character_parth_json['Character']['Status']['元素熟知'] = int(Decimal(character_info_list['fightPropMap']['28']).quantize(Decimal('1'), ROUND_HALF_UP))
            ### 会心率
            character_parth_json['Character']['Status']['会心率'] = float('{0:.1f}'.format(Decimal(character_info_list['fightPropMap']['20'] * 100).quantize(Decimal('0.1'), ROUND_HALF_UP)))
            ### 会心ダメージ
            character_parth_json['Character']['Status']['会心ダメージ'] = float('{0:.1f}'.format(Decimal(character_info_list['fightPropMap']['22'] * 100).quantize(Decimal('0.1'), ROUND_HALF_UP)))
            ### 元素チャージ効率
            character_parth_json['Character']['Status']['元素チャージ効率'] = float('{0:.1f}'.format(Decimal(character_info_list['fightPropMap']['23'] * 100).quantize(Decimal('0.1'), ROUND_HALF_UP)))
            ### キャラの元素を取得し、その元素のダメージを取得・代入
            character_parth_json['Character']['Status'][f'{element_name}元素ダメージ'] = float('{0:.1f}'.format(Decimal(character_info_list['fightPropMap'][f'{element_damage_id}'] * 100).quantize(Decimal('0.1'), ROUND_HALF_UP)))
            ## 天賦の情報取得・代入
            count = 0
            character_parth_json['Character']['Talent'] = {}
            for skill_level_id in character_json[f'{character_id}']['SkillOrder']:
                count = count + 1
                if(count == 1):
                    ### 通常
                    character_parth_json['Character']['Talent']['通常'] = character_info_list['skillLevelMap'][f'{skill_level_id}']
                if(count == 2):
                    ### スキル
                    character_parth_json['Character']['Talent']['スキル'] = character_info_list['skillLevelMap'][f'{skill_level_id}']
                if(count == 3):
                    ### 爆発
                    character_parth_json['Character']['Talent']['爆発'] = character_info_list['skillLevelMap'][f'{skill_level_id}']
            ## 基礎ステータス
            character_parth_json['Character']['Base'] = {}
            ### HP
            character_parth_json['Character']['Base']['HP'] = int(Decimal(character_info_list['fightPropMap']['1']).quantize(Decimal('1'), ROUND_HALF_UP))#int('{0:.1f}'.format(Decimal(character_info_list['fightPropMap']['1']).quantize(Decimal('0.1'), ROUND_HALF_UP)))
            ### 攻撃力
            character_parth_json['Character']['Base']['攻撃力'] = int(Decimal(character_info_list['fightPropMap']['4']).quantize(Decimal('1'), ROUND_HALF_UP))#int('{0:.1f}'.format(Decimal(character_info_list['fightPropMap']['4']).quantize(Decimal('0.1'), ROUND_HALF_UP)))
            ### 防御力
            character_parth_json['Character']['Base']['防御力'] = int(Decimal(character_info_list['fightPropMap']['7']).quantize(Decimal('1'), ROUND_HALF_UP))#int('{0:.1f}'.format(Decimal(character_info_list['fightPropMap']['7']).quantize(Decimal('0.1'), ROUND_HALF_UP)))
            ## 武器のステータス取得・代入
            character_parth_json['Weapon'] = {}
            for weapon_info_list in character_info_list['equipList']:
                if(weapon_info_list['flat']['itemType'] == 'ITEM_WEAPON'):
                    ### 名前
                    weapon_name_hash = weapon_info_list['flat']['nameTextMapHash']
                    character_parth_json['Weapon']['name'] = name_data_json['ja'][f'{weapon_name_hash}']
                    ### レベル
                    character_parth_json['Weapon']['Level'] = weapon_info_list['weapon']['level']
                    ### 凸数
                    weapon_id = weapon_info_list['itemId']
                    character_parth_json['Weapon']['totu'] = weapon_info_list['weapon']['affixMap'][f'1{weapon_id}'] + 1# 0~4なので1足す
                    ### レアリティ
                    character_parth_json['Weapon']['rarelity'] = weapon_info_list['flat']['rankLevel']
                    for weapon_status_list in weapon_info_list['flat']['weaponStats']:
                        # メインステータス
                        if(weapon_status_list['appendPropId'] == 'FIGHT_PROP_BASE_ATTACK'):
                            ### 基礎攻撃力
                            character_parth_json['Weapon']['BaseATK'] = weapon_status_list['statValue']
                    character_parth_json['Weapon']['Sub'] = {}
                    for weapon_status_list in weapon_info_list['flat']['weaponStats']:
                        ### サブステータス
                        if(weapon_status_list['appendPropId'] != 'FIGHT_PROP_BASE_ATTACK'):
                            #### ステータス名
                            sub_status_name = weapon_status_list['appendPropId']
                            character_parth_json['Weapon']['Sub']['name'] = conv_status_name[f'{sub_status_name}']
                            #### ステータス値
                            character_parth_json['Weapon']['Sub']['value'] = weapon_status_list['statValue']
            ## 聖遺物スコア
            score_save = {}
            score_save['total'] = 0
            for reliquary_info_list in character_info_list['equipList']:
                if(reliquary_info_list['flat']['itemType'] == 'ITEM_RELIQUARY'):
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_BRACER'):
                        score_save['flower'] = score_calculation(reliquary_info_list,calt_type,'flower')
                        score_save['total'] = score_save['total'] + score_save['flower']
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_NECKLACE'):
                        score_save['wing'] = score_calculation(reliquary_info_list,calt_type,'wing')
                        score_save['total'] = score_save['total'] + score_save['wing']
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_SHOES'):
                        score_save['clock'] = score_calculation(reliquary_info_list,calt_type,'clock')
                        score_save['total'] = score_save['total'] + score_save['clock']
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_RING'):
                        score_save['cup'] = score_calculation(reliquary_info_list,calt_type,'cup')
                        score_save['total'] = score_save['total'] + score_save['cup']
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_DRESS'):
                        score_save['crown'] = score_calculation(reliquary_info_list,calt_type,'crown')
                        score_save['total'] = score_save['total'] + score_save['crown']
            # score_save['total'] = score_save['flower'] + score_save['wing'] + score_save['clock'] + score_save['cup'] + score_save['crown']
            character_parth_json['Score'] = {}
            ### 計算方法
            character_parth_json['Score']['State'] = score_cal_type_name[f'{calt_type}']
            ### 合計スコア
            character_parth_json['Score']['total'] = float('{0:.1f}'.format(float(Decimal(score_save['total']).quantize(Decimal('0.01'), ROUND_HALF_UP))))
            ### 花のスコア
            if('flower' in score_save):
                character_parth_json['Score']['flower'] = float('{0:.1f}'.format(float(Decimal(score_save['flower']).quantize(Decimal('0.01'), ROUND_HALF_UP))))
            else:
                character_parth_json['Score']['flower'] = 0
            ### 羽のスコア
            if('wing' in score_save):
                character_parth_json['Score']['wing'] = float('{0:.1f}'.format(float(Decimal(score_save['wing']).quantize(Decimal('0.01'), ROUND_HALF_UP))))
            else:
                character_parth_json['Score']['wing'] = 0
            ### 時計のスコア
            if('clock' in score_save):
                character_parth_json['Score']['clock'] = float('{0:.1f}'.format(float(Decimal(score_save['clock']).quantize(Decimal('0.01'), ROUND_HALF_UP))))
            else:
                character_parth_json['Score']['clock'] = 0
            ### 盃のスコア
            if('cup' in score_save):
                character_parth_json['Score']['cup'] = float('{0:.1f}'.format(float(Decimal(score_save['cup']).quantize(Decimal('0.01'), ROUND_HALF_UP))))
            else:
                character_parth_json['Score']['cup'] = 0
            ### 冠のスコア
            if('crown' in score_save):
                character_parth_json['Score']['crown'] = float('{0:.1f}'.format(float(Decimal(score_save['crown']).quantize(Decimal('0.01'), ROUND_HALF_UP))))
            else:
                character_parth_json['Score']['crown'] = 0
            ## 聖遺物のステータス
            character_parth_json['Artifacts'] = {}
            character_parth_json['Artifacts']['flower'] = {}
            for reliquary_info_list in character_info_list['equipList']:
                if(reliquary_info_list['flat']['itemType'] == 'ITEM_RELIQUARY'):
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_BRACER'):
                        ### 花
                        character_parth_json = reliquary_status_dic(character_parth_json,reliquary_info_list,name_data_json,'flower')
            character_parth_json['Artifacts']['wing'] = {}
            for reliquary_info_list in character_info_list['equipList']:
                if(reliquary_info_list['flat']['itemType'] == 'ITEM_RELIQUARY'):
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_NECKLACE'):
                        ### 羽
                        character_parth_json = reliquary_status_dic(character_parth_json,reliquary_info_list,name_data_json,'wing')
            character_parth_json['Artifacts']['clock'] = {}
            for reliquary_info_list in character_info_list['equipList']:
                if(reliquary_info_list['flat']['itemType'] == 'ITEM_RELIQUARY'):
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_SHOES'):
                        ### 時計
                        character_parth_json = reliquary_status_dic(character_parth_json,reliquary_info_list,name_data_json,'clock')
            character_parth_json['Artifacts']['cup'] = {}
            for reliquary_info_list in character_info_list['equipList']:
                if(reliquary_info_list['flat']['itemType'] == 'ITEM_RELIQUARY'):
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_RING'):
                        ### 盃
                        character_parth_json = reliquary_status_dic(character_parth_json,reliquary_info_list,name_data_json,'cup')
            character_parth_json['Artifacts']['crown'] = {}
            for reliquary_info_list in character_info_list['equipList']:
                if(reliquary_info_list['flat']['itemType'] == 'ITEM_RELIQUARY'):
                    if(reliquary_info_list['flat']['equipType'] == 'EQUIP_DRESS'):
                        ### 冠
                        character_parth_json = reliquary_status_dic(character_parth_json,reliquary_info_list,name_data_json,'crown')
            ## キャラの元素
            character_parth_json['元素'] = element_name
    return json.dumps(character_parth_json,indent=2, ensure_ascii=False)

# テストでは僕のUIDでキャラは胡桃、計算方法は攻撃力%です。
# ``API_Return_JSON_Data_Cache``はキャッシュしたAPI返り値(JSON辞書型配列)を指定してください。
#print(score_json_parth('824242386','10000046','FIGHT_PROP_ATTACK_PERCENT',API_Return_JSON_Data_Cache))

# ArtifacterImageGenに渡すJSONファイル(辞書型配列)がコンソールに出力されます。

# 画像生成して返り値に画像を返す関数

def image_gene(uid_input,character_id_input,calt_type_input,usr_info_cache_json):
    return Generater.generation(json.loads(score_json_parth(uid_input,character_id_input,calt_type_input,usr_info_cache_json)))

#image = image_gene('824242386','10000046','FIGHT_PROP_ATTACK_PERCENT',API_Return_JSON_Data_Cache)
#image.show()