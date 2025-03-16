# agent.py
from openai import OpenAI

class Agent:
    def __init__(self, system_prompt: str, api_key: str):
        """AI 법률 상담 챗봇을 위한 Agent 클래스"""
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]  # 초기 프롬프트 포함
        self.user_queries = []
        self.client = OpenAI(api_key=api_key)  # OpenAI API 클라이언트

    def __call__(self, message: str) -> str:
        """사용자의 입력을 받아 AI 응답을 생성"""
        self.messages.append({"role": "user", "content": message})
        self.user_queries.append(message)

        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self) -> str:
        """AI에게 메시지를 보내고 응답을 받음"""
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=self.messages
        )
        return completion.choices[0].message.content

    def summarize_conversation(self) -> str:
        """사용자 상담 내용을 한 문장으로 요약"""
        summary_prompt = f"""
        다음 사용자의 질문을 한 문장으로 요약하세요: {self.user_queries}
        """
        print(self.user_queries)

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[{"role": "system", "content": "대화 내용을 한 문장으로 요약하는 역할을 수행합니다."},
                      {"role": "user", "content": summary_prompt}]
        )
        return completion.choices[0].message.content
