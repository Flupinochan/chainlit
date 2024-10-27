"""Simple Chatbot"""

from __future__ import annotations

import chainlit as cl
from botocore.config import Config

from utils import add_assistant_message, add_user_message, generate_message

"""環境変数"""
BOTO3_CONFIG = Config(
    retries={"max_attempts": 30, "mode": "standard"},
    read_timeout=900,
    connect_timeout=900,
)
SYSTEM_PROMPT = """
あなたは優秀な生成AIアシスタントです
マークダウン形式で回答してください"""


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> cl.User | None:
    """ユーザ名 + パスワード認証"""
    # ユーザ名: metalmental, パスワード: metalmental に設定
    if (username, password) == ("metalmental", "metalmental"):
        # ユーザ情報をreturnすることでチャット画面に遷移
        return cl.User(
            identifier=username,
            metadata={"role": "admin", "provider": "credentials"},
        )
    return None


@cl.on_chat_start
async def on_chat_start() -> None:
    """チャット開始時の処理"""
    # セッション変数を初期化
    cl.user_session.set("history", [])


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """メッセージ受信時の処理"""
    # cl.user_session.get/.set でセッション変数を定義/取得可能
    history = cl.user_session.get("history")
    history = add_user_message(history, message.content)
    # 生成AIのメッセージを送信
    msg = cl.Message(content="")
    async for text in generate_message(
        BOTO3_CONFIG,
        SYSTEM_PROMPT,
        history,
    ):
        await msg.stream_token(text)
    history = add_assistant_message(history, msg.content)
    await msg.update()
