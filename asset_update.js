const https = require('https');
const fs = require('fs');
const path = require('path');

// ファイルのダウンロード関数
function downloadFile(url,filename) {
    const get_filename = path.basename(url);
    https.get(url, (res) => {
        if(!(res.statusCode === 404)) {// 画像が存在しない場合はダウンロードしない
        const fileStream = fs.createWriteStream(filename);
            res.pipe(fileStream);
            fileStream.on('finish', () => {
                fileStream.close();
                console.log('Download '+url);
            });
        }
    })
}

const { EnkaClient, Weapon } = require("enka-network-api");
const { dir } = require('console');
const enka = new EnkaClient({ showFetchCacheLog: true, cacheDirectory: "./cache", defaultLanguage: "jp"});

// キャッシュ
enka.cachedAssetsManager.cacheDirectorySetup();
enka.cachedAssetsManager.fetchAllContents();

// 全部のデータを取得
const characters = enka.getAllCharacters();
const costumes = enka.getAllCostumes();
const weapons = enka.getAllWeapons();
const artifacts = enka.getAllArtifacts();

// キャラクター
//console.log('Character');
characters.forEach(w => {
    if(!(w.releasedAt === null)) {
        character_name = w.name.get();
        let dir_path = `./ArtifacterImageGen/character/${character_name}`;
        if( fs.existsSync(dir_path) ) {
            // キャラスキップ
            //console.log(`Skip: ${dir_path}/`);
            return;
        } else {
            // ディレクトリ作成
            fs.mkdir(dir_path, (err) => {
                //画像ダウンロード
                //console.log('Character_Name: '+character_name);
                // 星座(凸)
                let constellations = w.constellations;
                let count = 0;
                constellations.forEach(t => {
                    if(!(t.isHidden)) {// 非表示のスキルかどうか
                        count++;
                        /*
                        console.log('TalentId: ' + t.id + `(${count})`);// ID
                        console.log('TalentIcon: '+ t.icon.url);// アイコン
                        */
                        downloadFile(t.icon.url,`${dir_path}/${count}.png`);
                    }
                });
                // キャラ画像
                //console.log(`AvatarImage: ` + w.splashImage.url);
                downloadFile(w.splashImage.url,`${dir_path}/avatar.png`);
                // 元素スキル
                if(!(w.elementalSkill === null)) {
                    //console.log('SkillIcon: '+w.elementalSkill.icon.url);
                    downloadFile(w.elementalSkill.icon.url,`${dir_path}/スキル.png`);
                }
                // 元素爆発
                if(!(w.elementalBurst === null)) {
                    //console.log('elementalBurstIcon: '+w.elementalBurst.icon.url);
                    downloadFile(w.elementalBurst.icon.url,`${dir_path}/爆発.png`);
                }
                // 通常攻撃
                //console.log('NormalAtackIcon: '+w.normalAttack.icon.url);
                downloadFile(w.normalAttack.icon.url,`${dir_path}/通常.png`);
                // 処理終了
                console.log('\n');
            });
        }
    } else {
        return;
    }
});

// コスチューム
//console.log('Costume');
costumes.forEach(w => {
    let costume_id = w.id;
    let character_name = enka.getCharacterById(w.characterId).name;
    let dir_path = `./ArtifacterImageGen/character/${character_name}`;
    if( fs.existsSync(`${dir_path}/${costume_id}.png`) ) {
        // コスチュームスキップ
        //console.log(`Skip: ${dir_path}/${costume_id}.png`);
        return;
    } else {
        if(!(w.stars === null)) {
            //console.log('Character_Name: '+character_name);
            downloadFile(w.splashImage.url,`${dir_path}/${costume_id}.png`);
        }
    }
});

// 武器
//console.log('Weapon');
weapons.forEach(w => {
    let weapon_name = w.name;
    let dir_path = `./ArtifacterImageGen/weapon`;
    if( fs.existsSync(`${dir_path}/${weapon_name}.png`) ) {
        // コスチュームスキップ
        //console.log(`Skip: ${dir_path}/${weapon_name}.png`);
        return;
    } else {
        if(!(w.stars === null)) {
            //console.log('Weapon_Name: '+weapon_name);
            downloadFile(w.icon.url,`${dir_path}/${weapon_name}.png`);
        }
    }
});

// Artifacts
//console.log('Artifact');
artifacts.forEach(w => {
    let artifact_set_name = w.set.name;
    let artifact_type_name_ori = w.equipType;
    let artifact_type_name
    switch(artifact_type_name_ori) {
        case 'EQUIP_BRACER':
            artifact_type_name='flower';
            break;
        case 'EQUIP_NECKLACE':
            artifact_type_name='wing';
            break;
        case 'EQUIP_SHOES':
            artifact_type_name='clock';
            break;
        case 'EQUIP_RING':
            artifact_type_name='cup';
            break;
        case 'EQUIP_DRESS':
            artifact_type_name='crown';
            break;
    }
    //console.log('Set_Name: '+artifact_set_name+artifact_type_name);
    let dir_path = `./ArtifacterImageGen/Artifact/${artifact_set_name}`;
    if( fs.existsSync(`${dir_path}/${artifact_type_name}.png`) ) {
        // キャラスキップ
        //console.log(`Skip: ${dir_path}/${artifact_type_name}.png`);
        //return;
    } else {
        //console.log(`ArtifactName: ${dir_path}/${artifact_type_name}.png`);
        // ディレクトリが存在するかどうか
        if( fs.existsSync(dir_path) ) {
            //ディレクトリ存在
            downloadFile(w.icon.url,`${dir_path}/${artifact_type_name}.png`);
        } else {
            // ディレクトリ作成
            fs.mkdir(dir_path, (err) => {
                downloadFile(w.icon.url,`${dir_path}/${artifact_type_name}.png`);
            });
        }
    }
});