"""
Inference and dialogue generation script for DLA.

Load trained models and generate dialogue responses interactively or from prompts.

Usage:
    python src/generate.py --checkpoint checkpoint_epoch_final
    python src/generate.py --checkpoint checkpoint_epoch_final --interactive
"""

import os
import sys
import argparse
import pickle
import tensorflow as tf
from tensorflow import keras

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from model import build_generator
from utils import Tokenizer


class DialogueGenerator:
    """
    Interactive dialogue generation using trained DLA model.
    
    Loads trained Generator and Tokenizer to produce dialogue responses.
    Supports various generation strategies (temperature, top-k sampling).
    """
    
    def __init__(self, checkpoint_dir):
        """
        Initialize generator from checkpoint.
        
        Args:
            checkpoint_dir: Path to checkpoint directory containing model and tokenizer
        """
        self.checkpoint_dir = checkpoint_dir
        self.config = Config
        
        print("Loading DLA Dialogue Generator...")
        print("="*60)
        
        # Load tokenizer
        tokenizer_path = os.path.join(checkpoint_dir, "tokenizer.pkl")
        if not os.path.exists(tokenizer_path):
            raise FileNotFoundError(f"Tokenizer not found at: {tokenizer_path}")
        
        with open(tokenizer_path, 'rb') as f:
            self.tokenizer = pickle.load(f)
        
        print(f"✓ Tokenizer loaded (vocab size: {len(self.tokenizer.word2idx)})")
        
        # Build generator model
        self.generator = build_generator(self.config)
        
        # Load weights
        weights_path = os.path.join(checkpoint_dir, "generator.weights.h5")
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Generator weights not found at: {weights_path}")
        
        # Dummy forward pass to build model
        dummy_input = tf.constant([[1, 2, 3]])
        _ = self.generator(dummy_input, training=False)
        
        # Load trained weights
        self.generator.load_weights(weights_path)
        print(f"✓ Generator loaded from: {checkpoint_dir}")
        print("="*60 + "\n")
    
    def generate_response(self, context="", max_length=50, temperature=1.0, 
                         top_k=50, top_p=0.95):
        """
        Generate dialogue response given context.
        
        Args:
            context (str): Input context/prompt (can be empty for unconditional generation)
            max_length (int): Maximum length of generated response
            temperature (float): Sampling temperature (higher = more random)
                - 0.5: More conservative, coherent
                - 1.0: Balanced
                - 1.5: More creative, diverse
            top_k (int): Only sample from top-k most likely words
            top_p (float): Nucleus sampling - sample from smallest set with cumulative prob >= p
        
        Returns:
            generated_text (str): Generated dialogue response
        """
        # If context provided, convert to sequence
        if context:
            context_seq = self.tokenizer.text_to_sequence(context, add_start_end=False)
            # Start with context
            start_token = context_seq[0] if context_seq else self.tokenizer.START
        else:
            # Start with <START> token for unconditional generation
            start_token = self.tokenizer.START
        
        # Generate sequence
        generated_indices = self.generator.generate_sequence(
            start_token=start_token,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k
        )
        
        # Decode to text
        generated_text = self.tokenizer.sequence_to_text(generated_indices)
        
        return generated_text
    
    def interactive_mode(self):
        """
        Interactive dialogue generation mode.
        
        User enters context/prompts and model generates responses.
        """
        print("\n" + "="*60)
        print("Interactive Dialogue Generation Mode")
        print("="*60)
        print("\nInstructions:")
        print("  - Enter a dialogue context/prompt")
        print("  - Press Enter for random generation (no context)")
        print("  - Type 'quit' or 'exit' to stop")
        print("  - Type 'settings' to adjust generation parameters")
        print("\n" + "="*60 + "\n")
        
        # Default generation settings
        settings = {
            'max_length': 50,
            'temperature': 1.0,
            'top_k': 50,
            'top_p': 0.95
        }
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Check for commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                if user_input.lower() == 'settings':
                    self._adjust_settings(settings)
                    continue
                
                # Generate response
                print("\nGenerating...", end=" ")
                
                response = self.generate_response(
                    context=user_input,
                    max_length=settings['max_length'],
                    temperature=settings['temperature'],
                    top_k=settings['top_k'],
                    top_p=settings['top_p']
                )
                
                print(f"\rDLA: {response}\n")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye! 👋")
                break
            
            except Exception as e:
                print(f"\nError: {e}")
                continue
    
    def _adjust_settings(self, settings):
        """
        Allow user to adjust generation settings.
        
        Args:
            settings (dict): Current settings dictionary to modify
        """
        print("\n" + "-"*60)
        print("Current Settings:")
        print("-"*60)
        for key, value in settings.items():
            print(f"  {key}: {value}")
        print("-"*60)
        
        try:
            # Max length
            new_max = input(f"\nMax length (current: {settings['max_length']}): ").strip()
            if new_max:
                settings['max_length'] = int(new_max)
            
            # Temperature
            new_temp = input(f"Temperature (current: {settings['temperature']}): ").strip()
            if new_temp:
                settings['temperature'] = float(new_temp)
            
            # Top-k
            new_topk = input(f"Top-k (current: {settings['top_k']}): ").strip()
            if new_topk:
                settings['top_k'] = int(new_topk)
            
            print("\n✓ Settings updated!")
            print("-"*60 + "\n")
        
        except ValueError:
            print("\n✗ Invalid input. Settings unchanged.\n")
    
    def batch_generate(self, prompts, temperature=1.0, top_k=50):
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts (list): List of context strings
            temperature (float): Sampling temperature
            top_k (int): Top-k sampling parameter
        
        Returns:
            responses (list): List of generated responses
        """
        responses = []
        
        print(f"\nGenerating responses for {len(prompts)} prompts...")
        print("="*60)
        
        for i, prompt in enumerate(prompts, 1):
            response = self.generate_response(
                context=prompt,
                temperature=temperature,
                top_k=top_k
            )
            responses.append(response)
            
            print(f"\n{i}. Prompt: {prompt}")
            print(f"   Response: {response}")
        
        print("="*60)
        return responses
    
    def autocomplete(self, partial_text, num_completions=3):
        """
        Generate multiple completions for partial dialogue.
        
        Args:
            partial_text (str): Partial dialogue text to complete
            num_completions (int): Number of different completions to generate
        
        Returns:
            completions (list): List of completed dialogues
        """
        print(f"\nAutocompleting: '{partial_text}'")
        print("="*60)
        
        completions = []
        
        # Generate with varying temperature for diversity
        temperatures = [0.7, 1.0, 1.3]
        
        for i in range(num_completions):
            temp = temperatures[i % len(temperatures)]
            
            completion = self.generate_response(
                context=partial_text,
                temperature=temp,
                top_k=50
            )
            
            completions.append(completion)
            print(f"\n{i+1}. [temp={temp}] {completion}")
        
        print("="*60)
        return completions


def main():
    """Main entry point for generation script."""
    parser = argparse.ArgumentParser(
        description="Generate dialogues using trained DLA model"
    )
    
    parser.add_argument(
        '--checkpoint',
        type=str,
        default='checkpoint_epoch_final',
        help='Checkpoint directory name (relative to outputs/models/)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        default=None,
        help='Single prompt for generation'
    )
    
    parser.add_argument(
        '--temperature',
        type=float,
        default=1.0,
        help='Sampling temperature (0.1 to 2.0)'
    )
    
    parser.add_argument(
        '--top_k',
        type=int,
        default=50,
        help='Top-k sampling parameter'
    )
    
    parser.add_argument(
        '--max_length',
        type=int,
        default=50,
        help='Maximum generation length'
    )
    
    parser.add_argument(
        '--num_samples',
        type=int,
        default=5,
        help='Number of samples to generate (non-interactive mode)'
    )
    
    args = parser.parse_args()
    
    # Build full checkpoint path
    checkpoint_path = os.path.join(Config.MODEL_DIR, args.checkpoint)
    
    if not os.path.exists(checkpoint_path):
        print(f"Error: Checkpoint not found at {checkpoint_path}")
        print(f"\nAvailable checkpoints:")
        if os.path.exists(Config.MODEL_DIR):
            checkpoints = [d for d in os.listdir(Config.MODEL_DIR) 
                          if os.path.isdir(os.path.join(Config.MODEL_DIR, d))]
            for cp in checkpoints:
                print(f"  - {cp}")
        else:
            print(f"  (No checkpoints found - have you trained the model?)")
        return 1
    
    try:
        # Initialize generator
        generator = DialogueGenerator(checkpoint_path)
        
        # Interactive mode
        if args.interactive:
            generator.interactive_mode()
        
        # Single prompt
        elif args.prompt:
            print(f"\nPrompt: {args.prompt}")
            response = generator.generate_response(
                context=args.prompt,
                max_length=args.max_length,
                temperature=args.temperature,
                top_k=args.top_k
            )
            print(f"Response: {response}\n")
        
        # Generate random samples
        else:
            print(f"\nGenerating {args.num_samples} random dialogues...\n")
            print("="*60)
            
            for i in range(args.num_samples):
                response = generator.generate_response(
                    context="",
                    max_length=args.max_length,
                    temperature=args.temperature,
                    top_k=args.top_k
                )
                print(f"{i+1}. {response}\n")
            
            print("="*60)
        
        return 0
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
