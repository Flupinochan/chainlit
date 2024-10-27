"""ChainlitでLangchainを使う"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import chainlit as cl
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_aws import ChatBedrock
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.pydantic_v1 import BaseModel, Field

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """メモリ上のチャット履歴実装"""

    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """履歴にメッセージを追加"""
        self.messages.extend(messages)

    def clear(self) -> None:
        """履歴をクリア"""
        self.messages = []


store: dict[tuple[str, str], InMemoryHistory] = {}


def get_session_history(user_id: str, conversation_id: str) -> BaseChatMessageHistory:
    """セッション履歴を取得"""
    if (user_id, conversation_id) not in store:
        store[(user_id, conversation_id)] = InMemoryHistory()
    return store[(user_id, conversation_id)]


@cl.set_starters
async def set_starters() -> list[cl.Starter]:
    """スターター設定"""
    return [
        cl.Starter(
            label="今日の運勢",
            message="今日の運勢、仕事運、金運、健康運を教えてください",
        ),
    ]


@cl.on_chat_start
async def on_chat_start() -> None:
    """新しいチャット作成時の処理、モデルとプロンプトを初期化します。"""
    model = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        model_kwargs={"temperature": 0},
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "あなたは優秀な生成AIアシスタントです",
            ),
            ("human", "{question}"),
        ],
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """ユーザからメッセージを受信した際の処理"""
    runnable = cast(Runnable, cl.user_session.get("runnable"))

    msg = cl.Message(content="")
    print(message.content)
    print(cl.chat_context.to_openai())

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
