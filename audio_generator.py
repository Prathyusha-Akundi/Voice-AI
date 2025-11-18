from openai import OpenAI
import os
import json
import io
from dotenv import load_dotenv
from pydub import AudioSegment

class AudioGenerator:
    def __init__(self, env_path = "/Users/prathyushaakundi/Documents/prathyusha/projects/Voice-AI/.env", model_name="gpt-4o-mini-tts", user_config_path = "user_config.json"):
        load_dotenv(env_path)
        kwargs = {
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "organization": os.environ.get("OPENAI_ORG")
        }
        self.client = OpenAI(**kwargs)
        self.model_name = model_name
    
        with open(user_config_path, "r") as f:
            self.user_profiles = json.load(f)

    def list_voices(self):
        response = self.client.voices.list()
        return response
    
    def generate_audio(self, text, user_profile_name):
        user_profile = self.user_profiles.get(user_profile_name)
        if not user_profile:
            raise ValueError(f"User profile '{user_profile_name}' not found.")
        
        instructions = user_profile.get("instructions", "")
        role = user_profile.get("role", "narrator")
        gender = user_profile.get("gender", "neutral")
        language = user_profile.get("language", "en-US")
        tone = user_profile.get("tone", "neutral")
        description = user_profile.get("description", "")
        name = user_profile.get("name", "Voice AI")

        final_instructions = f"You are a {role} named {name}. Description: {description} Speak in a {tone} tone. {instructions}"

        response = self.client.audio.speech.create(
            model=self.model_name,
            instructions=final_instructions,
            voice=user_profile.get("voice", "alloy"),
            input=text
        )
        return response.content
    
    def generate_conversation_audio(self, conversation_data, output_dir="audio_output", output_filename="conversation.mp3"):
        """
        Generate a single audio file for an entire conversation by merging all turns.
        
        Args:
            conversation_data: List of conversation turns with 'role' and 'text' keys
            output_dir: Directory to save the merged audio file
            output_filename: Name of the output MP3 file
            
        Returns:
            Path to the generated audio file
        """
        
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        merged_audio = AudioSegment.empty()
        
        for idx, turn in enumerate(conversation_data):
            role = turn.get("role")
            text = turn.get("text")
            
            if not role or not text:
                print(f"Skipping turn {idx}: missing role or text")
                continue
            
            try:
                print(f"Generating audio for turn {idx}: {role} - '{text[:50]}...'")
                audio_response = self.generate_audio(text, role)
                
                # Convert response bytes to AudioSegment using BytesIO
                audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_response))
                
                # Add to merged audio with a small pause between turns (500ms)
                merged_audio += audio_segment
                merged_audio += AudioSegment.silent(duration=500)
                
            except Exception as e:
                print(f"Error generating audio for turn {idx}: {e}")
                continue
        
        # Save merged audio to file
        output_path = os.path.join(output_dir, output_filename)
        merged_audio.export(output_path, format="mp3")
        print(f"\n✓ Merged audio saved to: {output_path}")
        
        return output_path