#!/usr/bin/env python3
"""
Task 1: First Gemini API Call — Google Gemini
Make your first call to Google's Gemini model and inspect the response.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export GOOGLE_API_KEY="your-key-here"   # Free from aistudio.google.com
  pip install google-generativeai
"""

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def main():
    print("=" * 65)
    print("Task 1: Your First API Call — Google Gemini")
    print("=" * 65)

    model = genai.GenerativeModel("gemini-2.5-flash")

    # Experiment 1: Basic API call
    print("\nExperiment 1: Basic API Call")
    print("-" * 65)

    response = model.generate_content("What is Kubernetes and why do DevOps engineers use it?")
    print(response.text)

    # Experiment 2: Different question
    print("\n" + "-" * 65)
    print("Experiment 2: Different Question")
    print("-" * 65)

    response2 = model.generate_content("Explain Prometheus in 3 sentences")
    print(response2.text)

    # Experiment 3: Token usage
    print("\n" + "-" * 65)
    print("Experiment 3: Token Usage")
    print("-" * 65)

    usage = response2.usage_metadata
    print(f"Prompt tokens:   {usage.prompt_token_count}")
    print(f"Response tokens: {usage.candidates_token_count}")
    print(f"Total tokens:    {usage.total_token_count}")

    print("\n" + "=" * 65)
    print("Key Learning: Gemini is FREE via Google AI Studio.")
    print("Pattern: GenerativeModel() -> generate_content() -> response.text")
    print("=" * 65)

    print("\nTask 1 Complete!")
    print("Next: python3 demos/google/task2_system_prompts.py")


if __name__ == "__main__":
    main()
