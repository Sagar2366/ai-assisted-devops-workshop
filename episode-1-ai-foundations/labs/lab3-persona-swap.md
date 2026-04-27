# Lab 3: Persona Swap — Same Alert, Different Experts

> **Mission:** Send the same K8s OOM alert to three different AI personas and compare how each expert analyzes it.

---

## The Concept

Same alert. Three different system prompts. Three completely different analyses.

- **SRE Engineer** — memory limits, resource requests, VPA, kubectl commands
- **Network Engineer** — connectivity, DNS resolution, network-level root causes
- **Security Engineer** — access controls, compliance, potential attack vectors

The system prompt doesn't just change tone — it fundamentally changes what the model pays attention to.

---

## What You'll Build

Loop through three personas, send the same OOM alert to each, and print all three responses side by side.

---

## Step 1: Define the Personas

```python
personas = [
    (
        "SRE Engineer",
        "You are a senior SRE with 10 years of Kubernetes experience. Focus on resource management, scaling, and reliability. Give kubectl commands."
    ),
    (
        "Network Engineer",
        "You are a senior network engineer. Focus on connectivity, DNS, network policies, and how network issues could cause this problem."
    ),
    (
        "Security Engineer",
        "You are a senior security engineer. Focus on security implications, access controls, container security, and compliance."
    ),
]
```

---

## Step 2: Loop Through Each Persona

Send the same alert from Lab 2 with each persona's system prompt.

**Anthropic:**
```python
for title, system_prompt in personas:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

    message = client.messages.create(
        model="claude-sonnet-4-6-latest",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": alert}]
    )
    print(message.content[0].text)
```

---

## Run It

```bash
python3 demos/{your-provider}/task3_persona_swap.py
```

---

## What Success Looks Like

**SRE Engineer:** Talks about memory limits, resource requests, VPA, kubectl set resources, rollout restart.

**Network Engineer:** Talks about DNS resolution failures, network policy blocking health checks, service mesh timeouts causing OOM from request queuing.

**Security Engineer:** Talks about container escape risk, resource limits as security boundaries, privilege escalation from crashlooping, audit logging.

Same alert — completely different analysis from each expert.

---

## Key Takeaway

The system prompt isn't decoration — it fundamentally changes what the model focuses on. In production, you can swap personas for multi-angle incident analysis: one alert, three expert opinions.

---

Next: [Lab 4: Limitations](lab4-limitations.md)
