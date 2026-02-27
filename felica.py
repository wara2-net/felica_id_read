from smartcard.System import readers
from smartcard.util import toHexString


def main():
    # 接続されているリーダーの一覧を取得
    r = readers()
    if not r:
        print('リーダーが見つかりません')
        return

    reader = r[0]
    print(f'使用するリーダー：{reader}')

    try:
        # リーダーに接続
        connection = reader.createConnection()
        connection.connect()

        # ATR (Answer To Reset) 取得
        atr = connection.getATR()
        atr_hex = toHexString(atr).replace(' ', '')

        print(f'カード検知')
        print(f'ATR: {atr_hex}')

        # FeliCa (NFC-F) の判定ロジック
        # 一般的なPaSori等のリーダーでは、ATRに '3BFC' や '11' (FeliCaを示すコード) が含まれます
        # 特に Windows の PCSC 経由では 0x11 が FeliCa の指標になることが多いです
        if "1100" in atr_hex or "1101" in atr_hex: 
            # リーダーや環境により位置は微差がありますが、FeliCa特有のパターンを探します
            card_type = 'FeliCa (NFC-F)'
        elif '0031C1' in atr_hex:
            # マイナンバーカード (Type B) の一般的なパターン
            card_type = 'My Number Card (Type B)'
        else:
            card_type = 'Other (Type A/B or Unknown)'

        print(f'判定結果: {card_type}')

        # IDMを取得するため(GET DATA) を送信
        # [CLA, INS, P1, P2, Le] -> FeliCaのIDm取得コマンド
        GET_DATA_COMMAND = [0xFF, 0xCA, 0x00, 0x00, 0x00]

        data , sw1, sw2 = connection.transmit(GET_DATA_COMMAND)

        # レスポンス判定 0x90、0x00 が成功
        if sw1 == 0x90 and sw2 == 0x00:
            idm = toHexString(data).replace(' ', '')
            print(f'成功 IDm: {idm} (長さ： {len(idm)} 桁) ')
        else:
            print(f'読み取りエラー：ステータスコード {sw1:02X} {sw2:02X}')
    except Exception as e:
        print(f'接続に失敗しました(カードが載っていない可能性があります):{e}')

if __name__ == '__main__':
    main()
