from typing import Union, Any, Optional
from sparkai.llm.llm import ChatSparkLLM, AsyncCallbackHandler, GenerationChunk, ChatGenerationChunk
from sparkai.core.messages import ChatMessage

from ..config import Config

class AsyncChunkPrintHandler(AsyncCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, color: Optional[str] = None) -> None:
        """Initialize callback handler."""
        super().__init__()
        self.color = color


    async def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM generates a new token.

        Args:
            token (str): The new token.
        """

async def chat_spark(msg: str):
    messages = [{"role": "user",
                 "content": msg}]
    spark = ChatSparkLLM(
        spark_api_url="wss://spark-api.xf-yun.com/v1.1/chat",
        spark_app_id=Config.spark_app_id,
        spark_api_key=Config.spark_app_key,
        spark_api_secret=Config.spark_api_secret,
        spark_llm_domain="general",
        streaming=True,
        max_tokens= 4096,
    )
    messages = [ChatMessage(role="user",content=messages[0]["content"])]
    handler = AsyncChunkPrintHandler()
    a = spark.astream(messages, config={"callbacks": [handler]})
    msg = ""
    async for message in a:
        msg += message.content
    return msg