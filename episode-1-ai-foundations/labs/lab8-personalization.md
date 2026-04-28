# Lab 8: Personalization — Profile-Driven Responses

> **Mission:** Extract a structured user profile from conversation history and use it to personalize every AI response.

---

## The Concept

Take summarization one step further: instead of a free-text summary, extract a structured **JSON profile** from conversation history. Then inject it into the system prompt. Every response is now tailored to the engineer's specific stack, team size, and tools.

```
  GENERIC:                        PERSONALIZED:
  "Use a CI/CD pipeline to        "Set up ArgoCD to auto-rollback
   handle rollbacks."               your EKS deployments when
                                    payment-svc health checks fail.
  (could be for anyone)             Budget note: ArgoCD is free."

                                  (knows your stack, your problem,
                                   your budget)
```

---

## What You'll Build

1. Feed a sample SRE conversation into the model
2. Ask it to extract a JSON profile (cloud provider, tools, team size, pain points)
3. Ask the same question twice — once generic, once with the profile injected
4. Compare: generic advice vs tailored recommendations

---

## Step 1: Extract a JSON Profile

```python
extraction_prompt = """Extract a user profile from this conversation as JSON.
Include: name, role, company, cloud_provider, tools, team_size, pain_points, budget.

Conversation:
User: I'm Sagar, SRE at Acme Corp. We run EKS with 50 microservices.
User: We use ArgoCD for deployments and Prometheus for monitoring.
User: Team of 5 SREs covering 3 time zones. Budget is $500/month for AI tools.
User: Biggest pain point is OOM kills on payment-service after every deploy."""
```

**Anthropic:**
```python
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=512,
    messages=[{"role": "user", "content": extraction_prompt}]
)
profile = message.content[0].text
print("PROFILE:", profile)
```

---

## Step 2: Ask a Generic Question (No Profile)

```python
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[{"role": "user", "content": "How should I handle a failed deployment?"}]
)
print("GENERIC:", message.content[0].text)
```

---

## Step 3: Ask the Same Question WITH the Profile

```python
system_prompt = f"""You are a DevOps assistant. User profile:
{profile}
Tailor all responses to this user's specific stack, tools, and constraints."""

message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system=system_prompt,
    messages=[{"role": "user", "content": "How should I handle a failed deployment?"}]
)
print("PERSONALIZED:", message.content[0].text)
```

---

## Run It

```bash
python3 demos/{your-provider}/task8_personalization.py
```

---

## What Success Looks Like

**Generic:** "Use a CI/CD pipeline with rollback capabilities. Consider blue-green deployments." Could be for anyone.

**Personalized:** "Configure ArgoCD auto-rollback on your EKS cluster. Set health checks on payment-service to trigger automatic rollback when OOM is detected. Since your budget is $500/month, ArgoCD is free and already in your stack." References your actual tools, your specific problem, your budget.

---

## Key Takeaway

Personalization = profile extraction + system prompt injection. The AI stops giving generic advice and starts referencing your actual tools, stack, and constraints. This is the foundation for building AI assistants that know your team.

---

## What You've Mastered

| Concept | Lab | One-Sentence Summary |
|---------|-----|---------------------|
| LLM API call | 1 | Send a prompt, get tokens back — that's inference |
| System prompts | 2 | One line turns a chatbot into a senior SRE |
| Persona swap | 3 | Same input, different system prompt = different expert |
| Limitations | 4 | LLMs hallucinate, can't access live systems, can't execute |
| Memory | 5 | Send full conversation history = short-term memory |
| Context window | 6 | When history overflows, slide the window |
| Summarization | 7 | Compress old messages instead of dropping them |
| Personalization | 8 | Extract profile, tailor every response |
| Tool use | 9 | Define tools, model decides when to call them |

### The Agent Formula

```
  THINK  (LLM reasons about the task)
     |
  ACT    (tools execute actions)
     |
  OBSERVE (read the result)
     |
  LOOP   (repeat until done)
```

You just built all the pieces. In Episode 4, you connect them into a real agent.

---

Next: [Lab 9: Basic Tool Use](lab9-basic-tool.md)

---

## Homework

1. Complete all 9 tasks with at least one provider
2. Pick a second provider — compare the SDK patterns (they're almost identical)
3. Try the hallucination test (Lab 4) with your own DevOps questions
4. Read [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) by Anthropic

---

## Complete Code (Anthropic)

If you get stuck, here's the full working script:

```python
#!/usr/bin/env python3
"""Task 8: Personalized Context — SRE Profile Extraction"""
import anthropic
import json
import re

def main():
    client = anthropic.Anthropic()
    system = "You are a helpful DevOps assistant that provides personalized recommendations."

    # Build conversation with SRE details
    conversation = []
    conversation_log = []
    user_messages = [
        "Hi, I'm Sagar, an SRE at Acme Corp",
        "We run EKS with about 50 microservices in production",
        "We use ArgoCD for deployments and Prometheus for monitoring",
        "Our team is 5 SREs covering 3 time zones",
        "Biggest pain point is OOM kills on payment-service after every deploy. Budget is $500/month for AI tools."
    ]

    for msg in user_messages:
        conversation.append({"role": "user", "content": msg})
        r = client.messages.create(
            model="claude-opus-4-7", max_tokens=256,
            system=system, messages=conversation
        )
        reply = r.content[0].text
        conversation.append({"role": "assistant", "content": reply})
        conversation_log.append({"user": msg, "assistant": reply})

    # Extract SRE profile
    conv_text = ""
    for ex in conversation_log:
        conv_text += f"User: {ex['user']}\nAssistant: {ex['assistant']}\n\n"

    extraction_prompt = f"""Extract a user profile from this conversation as JSON.
Include: name, role, company, cloud_provider, tools, team_size, pain_points, budget.

Conversation:
{conv_text}

Return ONLY a JSON object:
{{"name": "...", "role": "...", "company": "...", "cloud_provider": "...", "tools": [...], "team_size": "...", "pain_points": [...], "budget": "..."}}"""

    profile_response = client.messages.create(
        model="claude-opus-4-7", max_tokens=256,
        messages=[{"role": "user", "content": extraction_prompt}]
    )
    profile_json = profile_response.content[0].text

    try:
        json_match = re.search(r'\{[^}]+\}', profile_json, re.DOTALL)
        if json_match:
            profile_json = json_match.group(0)
        user_profile = json.loads(profile_json)
    except:
        user_profile = {"name": "Sagar", "role": "SRE", "company": "Acme Corp",
                       "cloud_provider": "EKS", "tools": ["ArgoCD", "Prometheus"],
                       "team_size": "5", "pain_points": ["OOM kills"], "budget": "$500/month"}

    print(f"Profile: {json.dumps(user_profile, indent=2)}")

    # Compare generic vs personalized
    test_query = "How should I handle a failed deployment?"

    # Generic
    print("\nGeneric (no context):")
    r = client.messages.create(
        model="claude-opus-4-7", max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": test_query}]
    )
    print(r.content[0].text[:200])

    # Personalized
    personalized_system = f"""{system}

You are talking to {user_profile.get('name', 'the user')}, {user_profile.get('role', 'an engineer')} at {user_profile.get('company', 'their company')}.
Cloud: {user_profile.get('cloud_provider', 'unknown')}.
Tools: {', '.join(user_profile.get('tools', []))}.
Team: {user_profile.get('team_size', 'unknown')} engineers.
Pain points: {', '.join(user_profile.get('pain_points', []))}.
Budget: {user_profile.get('budget', 'unknown')}.
Tailor all responses to their specific stack, tools, and constraints."""

    print("\nPersonalized (with profile):")
    r = client.messages.create(
        model="claude-opus-4-7", max_tokens=512,
        system=personalized_system,
        messages=[{"role": "user", "content": test_query}]
    )
    print(r.content[0].text[:200])

if __name__ == "__main__":
    main()
```

---

**Built by [Sagar Utekar](https://github.com/Sagar2366)** | CNCF Ambassador | Kubestronaut
