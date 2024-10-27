"""テスト"""

from botocore.config import Config

from utils import add_user_message, generate_message

config = Config(
    retries={"max_attempts": 30, "mode": "standard"},
    read_timeout=900,
    connect_timeout=900,
)
system_prompt = "あなたは優秀な生成AIアシスタントです"
text = "こんにちは"
messages = add_user_message([], text)

if __name__ == "__main__":
    for response in generate_message(config, system_prompt, messages):
        print(response, end="", flush=True)
