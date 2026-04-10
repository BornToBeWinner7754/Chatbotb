# app/tools.py

async def get_weather(city: str):
    # mock tool
    return f"The weather in {city} is 30°C and sunny"

async def calculator(expression: str):
    try:
        return str(eval(expression))
    except Exception:
        return "Invalid expression"