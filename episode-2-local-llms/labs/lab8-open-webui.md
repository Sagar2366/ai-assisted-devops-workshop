# Lab 8: Open Web UI — ChatGPT for Your Team, Free & Private

> **Mission:** Launch a ChatGPT-like web interface connected to your local Ollama models — one Docker command.

---

## The Concept

Open Web UI is an open-source ChatGPT clone that connects to Ollama. It gives your team a familiar chat interface without:
- Paying for ChatGPT Team ($25/user/month)
- Sending data to OpenAI's servers
- Managing API keys for every team member

One `docker run` command. All your Ollama models appear in the dropdown. Data stays on your network.

```
  Browser → Open Web UI (Docker, port 3000) → Ollama (localhost:11434) → Local Model
```

---

## What You'll Build

A Python script that:
1. Checks Docker and Ollama are running
2. Launches Open Web UI as a Docker container
3. Waits for the UI to become ready
4. Verifies models are detected

---

## Step 1: Pre-Flight Checks

The script checks that Docker and Ollama are running before attempting the launch.

---

## Step 2: Launch with Docker

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui-workshop \
  ghcr.io/open-webui/open-webui:main
```

Key flags:
- `-p 3000:8080` — map local port 3000 to container's 8080
- `--add-host=host.docker.internal:host-gateway` — let the container reach your host machine
- `-e OLLAMA_BASE_URL=...` — tell Open Web UI where Ollama is running
- `--name open-webui-workshop` — easy to stop/remove later

---

## Step 3: Access the UI

Open [http://localhost:3000](http://localhost:3000) in your browser.

First visit:
1. Create an admin account (stored locally — no external auth)
2. Select a model from the dropdown (these are your Ollama models)
3. Start chatting

---

## Step 4: Run It

```bash
python3 demos/ollama/task8_open_webui.py
```

---

## Cleanup

When you're done:
```bash
docker stop open-webui-workshop
docker rm open-webui-workshop
```

---

## What Success Looks Like

Open Web UI running at `localhost:3000`, showing all your Ollama models in the model selector. You can chat with any model through a familiar ChatGPT-like interface.

---

## Key Takeaway

ChatGPT-like interface, zero cost, fully private. Runs on your machine or your team's server. All Ollama models appear automatically. No data ever leaves your network. Share with your team — one Docker command.

---

**All 8 Ollama tasks complete!**

Next episode part: Multi-Provider Showdown, Prompt Caching, Unified Client.
