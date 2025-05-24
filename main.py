from datetime import datetime
from langchain_community.chat_models import ChatOllama
from langgraph.graph import END, MessageGraph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def get_current_time() -> dict:
    """Return current UTC time in ISO‑8601 format"""
    from datetime import datetime, timezone
    return {"utc": datetime.now(timezone.utc).isoformat()}



model = ChatOllama(
    model="llama3.2:latest",
    temperature=0,
)

workflow = MessageGraph()

def needs_time_tool(query: str) -> bool:
    time_keywords = ["time", "час", "время", "который час", "текущее время", "сколько времени"]
    query = query.lower().strip(",.!?")
    return any(keyword in query for keyword in time_keywords)

def route_request(state):
    if not state or not isinstance(state[-1], HumanMessage):
        return END
    return "get_time" if needs_time_tool(state[-1].content) else "generate_response"

def get_time(state):
    try:
        current_time = get_current_time.invoke({})
        return AIMessage(content=f"Текущее время UTC: {current_time['utc']}")
    except Exception as e:
        logger.error(f"Time error: {e}")
        return AIMessage(content="Ошибка определения времени")

def generate_response(state):
    try:
        response = model.invoke(state)
        return response
    except Exception as e:
        logger.error(f"Model error: {e}")
        return AIMessage(content=" Ошибка при обработке")

# Граф обработки
workflow.add_node("route", route_request)
workflow.add_node("get_time", get_time)
workflow.add_node("generate_response", generate_response)

workflow.add_edge("get_time", END)
workflow.add_edge("generate_response", END)

workflow.add_conditional_edges(
    "route",
    route_request,
    {"get_time": "get_time", "generate_response": "generate_response"}
)

workflow.set_entry_point("route")
app = workflow.compile()

if __name__ == "__main__":
    print("⏰ Точное время: Бот готов (введите 'выход' для завершения)")
    
    while True:
        try:
            user_input = input("Вы: ").strip()
            if user_input.lower() in ('выход', 'exit', 'quit'):
                break
                
            result = app.invoke([HumanMessage(content=user_input)])
            
            if result and isinstance(result[-1], AIMessage):
                print("Бот:", result[-1].content)
                
        except Exception as e:
            logger.error(f"System error: {e}")
            print("Бот: Временная ошибка системы")