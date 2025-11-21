from langchain.agents import Tool, initialize_agent, AgentExecutor
from langchain.agents import AgentType
from langchain.llms import LlamaCpp
from api.agents.tools import run_benchmark_tool, trigger_retrain_tool, diagnose_quality_tool

class AgentController:
    def __init__(self, model_path: str = None):
        try:
            self.llm = LlamaCpp(model_path=model_path or 'models/tinyllama.bin', n_ctx=1024, n_threads=2)
        except Exception:
            self.llm = None
        tools = [
            Tool(name='run_benchmark', func=run_benchmark_tool, description='Run benchmarks'),
            Tool(name='trigger_retrain', func=trigger_retrain_tool, description='Trigger retraining'),
            Tool(name='diagnose_quality', func=diagnose_quality_tool, description='Diagnose quality issues'),
        ]
        if self.llm:
            self.agent = initialize_agent(tools, self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
        else:
            self.agent = None

    def summarize(self, text: str, category: str, confidence: float, rag_exp: str) -> str:
        if not self.agent:
            return f"Predicted '{category}' with confidence {confidence:.2f}. Rationale: {rag_exp}"
        prompt = f"Transaction: {text}\nPredicted: {category} ({confidence:.2f})\nRationale: {rag_exp}\nProvide a concise (1-2 sentence) summary of reasoning and suggested actions."
        resp = self.agent.run(prompt)
        return resp
