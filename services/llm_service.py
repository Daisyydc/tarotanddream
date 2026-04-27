import requests

DEEPSEEK_API_URL = "YOUR_DEEPSEEK_API_URL"
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"


def generate_text(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()

    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
