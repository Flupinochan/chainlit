"""メモリ上のチャット履歴実装"""

from __future__ import annotations

from langchain_aws import ChatBedrock
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import ConfigurableFieldSpec, RunnableWithMessageHistory
from pydantic import BaseModel, Field

# Model定義
model = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    model_kwargs={"temperature": 0},
)


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """メモリ上のチャット履歴実装"""

    messages: list[BaseMessage] = Field(default_factory=list)

    class Config:
        """型設定"""

        arbitrary_types_allowed = True

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        """履歴をクリア"""
        self.messages = []


# storeにチャット履歴を格納
store: dict[str, InMemoryHistory] = {}


# def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
#     """セッションIDを指定して各チャット履歴を取得する場合"""
#     if session_id not in store:
#         store[session_id] = InMemoryHistory()
#     return store[session_id]


def get_session_history(user_id: str, conversation_id: str) -> BaseChatMessageHistory:
    """ユーザーIDと会話IDから各チャット履歴を取得する場合"""
    if (user_id, conversation_id) not in store:
        store[(user_id, conversation_id)] = InMemoryHistory()
    return store[(user_id, conversation_id)]


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "あなたは優秀なAIアシスタントです"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ],
)

chain = prompt | model | StrOutputParser()

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="history",
    history_factory_config=[
        ConfigurableFieldSpec(
            id="user_id",
            annotation=str,
            name="User ID",
            description="ユーザーID",
            default="",
            is_shared=True,
        ),
        ConfigurableFieldSpec(
            id="conversation_id",
            annotation=str,
            name="Conversation ID",
            description="会話ID",
            default="",
            is_shared=True,
        ),
    ],
)

result = with_message_history.stream(
    {"question": "日本語は分かりますか?"},
    config={"configurable": {"user_id": "123", "conversation_id": "1"}},
)

# history = get_by_session_id("1")
# history.add_message(AIMessage(content="hello"))
for chunk in result:
    print(chunk, end="", flush=True)
