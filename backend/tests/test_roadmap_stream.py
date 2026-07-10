import httpx
import json

URL = "http://localhost:8000/api/roadmap/generate"
PROMPT = "I'm a backend engineer with 3 years of experience in Python and Django. I want to become an ML engineer."


def main():
    print(f"Sending prompt: {PROMPT}\n")
    print("=" * 60)

    full_response = []

    with httpx.stream("POST", URL, json={"prompt": PROMPT}, timeout=120) as r:
        for line in r.iter_lines():
            if not line.startswith("data:"):
                continue

            payload = line[len("data:"):].strip()

            if payload == "[DONE]":
                break

            data = json.loads(payload)

            if "error" in data:
                print(f"\n[ERROR] {data['error']}")
                break

            token = data.get("token", "") or data.get("chunk", "")
            print(token, end="", flush=True)
            full_response.append(token)

    print("\n" + "=" * 60)
    print(f"\nTotal characters received: {len(''.join(full_response))}")


if __name__ == "__main__":
    main()
