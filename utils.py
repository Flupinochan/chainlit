"""Claude3を使用してメッセージを生成"""

from __future__ import annotations

import json
from typing import AsyncGenerator

import boto3
from botocore.config import Config


def add_user_message(history: list[dict], message: str) -> list[dict]:
    """ユーザメッセージを追加"""
    format_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": message},
        ],
    }
    history.append(format_message)
    return history


def add_assistant_message(history: list[dict], message: str) -> list[dict]:
    """生成AIメッセージを追加"""
    format_message = {
        "role": "assistant",
        "content": [
            {"type": "text", "text": message},
        ],
    }
    history.append(format_message)
    return history


async def generate_message(
    config: Config,
    system_prompt: str,
    messages: list[dict],
) -> AsyncGenerator[str, None]:
    """Claude3を使用してメッセージを非同期ストリーミング生成"""
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": messages,
        },
    )
    bedrock_runtime = boto3.client("bedrock-runtime", config=config)
    streaming_response = bedrock_runtime.invoke_model_with_response_stream(
        body=body,
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
    )
    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            yield chunk["delta"].get("text", "")
