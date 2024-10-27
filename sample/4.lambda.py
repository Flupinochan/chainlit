"""Lambda関数"""

from __future__ import annotations

import json

import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.config import Config

"""環境変数"""
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
BOTO3_CONFIG = Config(
    retries={"max_attempts": 30, "mode": "standard"},
    read_timeout=900,
    connect_timeout=900,
)
SYSTEM_PROMPT = """
あなたは優秀な生成AIアシスタントです
マークダウン形式で回答してください"""


# "messages": [
#     {"role": "user", "content": [{"type": "text", "text": "ことわざを一つお願いいたします"}]}
#     {"role": "assistant", "content": [{"type": "text", "text": "猿も木から落ちる"}]}
#     {"role": "user", "content": [{"type": "text", "text": "ことわざを英語に翻訳してください"}]}
# ]
# "messages": [
#     {"role": "user", "content": [{"type": "text", "text": message}]},
# ],
def generate_message(system_prompt: str, message: str) -> dict:
    """生成AIでメッセージを生成"""
    bedrock_runtime = boto3.client("bedrock-runtime", config=BOTO3_CONFIG)
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": message}]},
            ],
        },
    )
    response = bedrock_runtime.invoke_model(body=body, modelId=MODEL_ID)
    response_body = json.loads(response.get("body").read())
    return response_body["content"][0]["text"]


# event = {"message": "入力値"}
def lambda_handler(event: dict, _context: LambdaContext) -> dict:
    """Lambda関数"""
    message = event.get("message")
    response_body = generate_message(SYSTEM_PROMPT, message)
    return response_body
