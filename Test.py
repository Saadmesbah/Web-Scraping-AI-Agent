import openai

client = openai.OpenAI(
    api_key="API-key",
    base_url="https://openrouter.ai/api/v1"
)

resp = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=[{"role":"user","content":"Say hello"}],
    max_tokens=50
)

print(resp.choices[0].message.content)