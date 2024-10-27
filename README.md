## Install

https://docs.chainlit.io/get-started/installation

## Run port 8001

`-w` is watch mode
`--port 8001` is the port to run the server on

```bash
chainlit run main.py -w --port 8001
```

## デコレータ一覧

https://docs.chainlit.io/concepts/chat-lifecycle

## パスワード認証

https://docs.chainlit.io/authentication/password

JWTシークレットを環境変数に設定する必要がある

```bash
chainlit create-secret
# 表示されたシークレットを環境変数に設定する
export CHAINLIT_AUTH_SECRET="sgQ1Rw0Z3Kss.r7Db:Z-jrCAeZ/M~r7Vd8wuxl1c:eU2i4W-mp3y%rGXAMrrvW@t"
```

## 日本語設定

https://docs.chainlit.io/customisation/translation#translate-chainlit-md-file

`.chainlit/translations` ディレクトリに日本語訳した「ja.json」を追加する

```bash
chainlit lint-translations
```

## チャット履歴
https://github.com/Chainlit/chainlit/blob/main/cypress/e2e/data_layer/main.py#L200