#!/usr/bin/env python3
"""
Script to generate audio version of a conversation from sample_conversation.json
Uses the AudioGenerator class to create MP3 files for each speaker turn.
"""

import json
import os
import sys
from audio_generator import AudioGenerator


def load_conversation(conversation_path="conversations/sample_conversation.json"):
    """Load conversation data from JSON file."""
    with open(conversation_path, "r") as f:
        data = json.load(f)
    return data.get("conversation", [])


def main(conversation_path="conversations/sample_conversation.json", output_path="audio_output/conversation.mp3"):
    # Initialize the audio generator
    print("Initializing AudioGenerator...")
    generator = AudioGenerator(
        env_path=".env",
        model_name="gpt-4o-mini-tts",
        user_config_path="user_config.json"
    )
    
    # Load conversation
    print(f"Loading conversation from {conversation_path}...")
    conversation = load_conversation(conversation_path)
    
    if not conversation:
        print("No conversation data found!")
        sys.exit(1)
    
    print(f"Found {len(conversation)} turns in conversation.\n")
    
    # Generate merged audio for the entire conversation
    print("Generating merged audio for entire conversation...")
    audio_file = generator.generate_conversation_audio(
        conversation,
        output_dir=os.path.dirname(output_path),
        output_filename=os.path.basename(output_path)
    )
    
    print(f"\n✓ Successfully generated conversation audio!")
    print(f"Output: {audio_file}")


if __name__ == "__main__":
    main(conversation_path="conversations/loan_conversation_2.json", output_path="audio_output/loan_conversation_v2.mp3")