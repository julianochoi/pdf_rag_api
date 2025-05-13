from functools import lru_cache
from typing import Iterable

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.core import config

type LLMClientType = type[ChatOpenAI] | type[ChatGoogleGenerativeAI] | type[ChatAnthropic] | type[ChatGroq]


available_chats: dict[str, LLMClientType] = {
	"openai": ChatOpenAI,
	"google": ChatGoogleGenerativeAI,
	"anthropic": ChatAnthropic,
	"groq": ChatGroq,
}


def build_llm_client() -> BaseChatModel:
	settings = config.get_llm_settings()
	available = []
	for llm in settings.llms:
		if llm.provider not in available_chats:
			print(f"LLM provider {llm.provider} not supported.")
			continue
		try:
			chat_class = available_chats[llm.provider]
			chat = chat_class(  # type: ignore[call-arg]
				name=llm.name,
				model=llm.model,
				api_key=llm.api_key,
				temperature=0,
				max_retries=0,
			)
			available.append(chat)
		except Exception as e:
			print(f"Failed to create LLM client for {llm.provider}: {e}")
			continue
	if not available:
		raise ValueError("No available LLM providers found.")
	base_chat = available.pop(0)
	if len(available):
		# Fallback to the next available providers
		base_chat.with_fallbacks(available)
	print("Using LLM provider:", base_chat.__class__.__name__)
	print("Fallback providers:", [chat.__class__.__name__ for chat in available])
	return base_chat


class LLMProvider:
	def __init__(self) -> None:
		settings = config.get_llm_settings()
		self.settings = settings
		self.client = build_llm_client()


@lru_cache(maxsize=1)
def build_llm_provider() -> LLMProvider:
	return LLMProvider()


def build_rag_template() -> PromptTemplate:
	template = """Use the following pieces of context to answer the question at the end.
	If you don't know the answer, just say that you don't know, don't try to make up an answer.
	Use three sentences maximum and keep the answer as concise as possible.
	Always say "thanks for asking!" at the end of the answer.

	{context}

	Question: {question}

	Helpful Answer:"""
	return PromptTemplate.from_template(template)


def build_prompt(question: str, context_chunks: Iterable[str]) -> str:
	context = " ".join(context_chunks)
	prompt_template = build_rag_template()
	return prompt_template.format(
		context=context,
		question=question,
	)


def answer_question(question: str, context_chunks: Iterable[str]) -> BaseMessage:
	prompt = build_prompt(question, context_chunks)
	llm_provider = build_llm_provider()
	response = llm_provider.client.invoke(prompt)
	return response
