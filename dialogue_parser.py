"""
Multi-file parser for unstructured dialogue datasets
Handles various dialogue formats including anime scripts, conversations, and context-response pairs
"""

import os
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DialogueTurn:
    """Represents a single turn in a dialogue"""
    context: str
    response: str
    metadata: Optional[Dict] = None


class DialogueParser:
    """
    Flexible parser for various dialogue dataset formats
    Supports:
    - Context-response pairs separated by 'response:'
    - Pure dialogue with speaker labels
    - Mixed format with scene descriptions
    """
    
    def __init__(self):
        self.context_response_pattern = re.compile(
            r'context:\s*(.+?)\s*response:\s*(.+?)(?=\ncontext:|$)', 
            re.DOTALL | re.IGNORECASE
        )
        self.dialogue_pattern = re.compile(
            r'^(.+?):\s*(.+?)$',
            re.MULTILINE
        )
        
    def parse_file(self, filepath: str) -> List[DialogueTurn]:
        """
        Parse a single dialogue file
        
        Args:
            filepath: Path to the dialogue file
            
        Returns:
            List of DialogueTurn objects
        """
        logger.info(f"Parsing file: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try context-response format first
        turns = self._parse_context_response(content)
        
        if not turns:
            # Fall back to dialogue format
            turns = self._parse_dialogue_format(content)
        
        logger.info(f"Extracted {len(turns)} dialogue turns from {filepath}")
        return turns
    
    def _parse_context_response(self, content: str) -> List[DialogueTurn]:
        """Parse context: ... response: ... format"""
        matches = self.context_response_pattern.findall(content)
        turns = []
        
        for context, response in matches:
            # Clean up context (may contain multiple previous turns)
            context = self._clean_text(context)
            response = self._clean_text(response)
            
            if context and response:
                turns.append(DialogueTurn(
                    context=context,
                    response=response,
                    metadata={"format": "context_response"}
                ))
        
        return turns
    
    def _parse_dialogue_format(self, content: str) -> List[DialogueTurn]:
        """Parse speaker: dialogue format"""
        lines = content.strip().split('\n')
        turns = []
        context_buffer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line matches speaker: dialogue pattern
            match = self.dialogue_pattern.match(line)
            if match:
                speaker, dialogue = match.groups()
                dialogue = self._clean_text(dialogue)
                
                if context_buffer and dialogue:
                    # Create turn with previous context
                    context = " ".join(context_buffer[-3:])  # Last 3 turns as context
                    turns.append(DialogueTurn(
                        context=context,
                        response=dialogue,
                        metadata={
                            "format": "dialogue",
                            "speaker": speaker
                        }
                    ))
                
                # Add to context buffer
                context_buffer.append(f"{speaker}: {dialogue}")
            else:
                # Handle scene descriptions or other text
                if context_buffer:
                    context_buffer.append(line)
        
        return turns
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove backslash separators
        text = text.replace('\\', ' ')
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    def parse_directory(self, directory: str, pattern: str = "*.txt") -> List[DialogueTurn]:
        """
        Parse all files in a directory matching the pattern
        
        Args:
            directory: Directory containing dialogue files
            pattern: File pattern to match (e.g., "*.txt", "train-*.txt")
            
        Returns:
            Combined list of DialogueTurn objects from all files
        """
        import glob
        
        all_turns = []
        file_pattern = os.path.join(directory, pattern)
        files = glob.glob(file_pattern)
        
        logger.info(f"Found {len(files)} files matching pattern: {pattern}")
        
        for filepath in sorted(files):
            try:
                turns = self.parse_file(filepath)
                all_turns.extend(turns)
            except Exception as e:
                logger.error(f"Error parsing {filepath}: {e}")
                continue
        
        return all_turns
    
    def to_training_format(self, turns: List[DialogueTurn], format_type: str = "jsonl") -> str:
        """
        Convert dialogue turns to training format
        
        Args:
            turns: List of DialogueTurn objects
            format_type: Output format ("jsonl", "csv", "conversational")
            
        Returns:
            Formatted string ready for training
        """
        if format_type == "jsonl":
            import json
            lines = []
            for turn in turns:
                lines.append(json.dumps({
                    "context": turn.context,
                    "response": turn.response,
                    "metadata": turn.metadata
                }))
            return "\n".join(lines)
        
        elif format_type == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["context", "response"])  
            
            for turn in turns:
                writer.writerow([turn.context, turn.response])
            
            return output.getvalue()
        
        elif format_type == "conversational":
            # Format suitable for conversational AI training
            lines = []
            for turn in turns:
                lines.append(f"Human: {turn.context}")
                lines.append(f"Assistant: {turn.response}")
                lines.append("")  # Empty line between turns
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unknown format type: {format_type}")


class DatasetStatistics:
    """Calculate statistics for dialogue datasets"""
    
    @staticmethod
    def calculate_stats(turns: List[DialogueTurn]) -> Dict:
        """Calculate various statistics"""
        if not turns:
            return {}
        
        context_lengths = [len(turn.context.split()) for turn in turns]
        response_lengths = [len(turn.response.split()) for turn in turns]
        
        return {
            "total_turns": len(turns),
            "avg_context_length": sum(context_lengths) / len(context_lengths),
            "avg_response_length": sum(response_lengths) / len(response_lengths),
            "max_context_length": max(context_lengths),
            "max_response_length": max(response_lengths),
            "min_context_length": min(context_lengths),
            "min_response_length": min(response_lengths),
        }


# Example usage
if __name__ == "__main__":
    import sys
    
    parser = DialogueParser()
    
    # Check if directory/file path is provided
    if len(sys.argv) > 1:
        path = sys.argv[1]
        
        if os.path.isfile(path):
            # Parse a single file
            turns = parser.parse_file(path)
        elif os.path.isdir(path):
            # Parse entire directory
            turns = parser.parse_directory(path)
        else:
            print(f"Error: {path} is not a valid file or directory")
            sys.exit(1)
        
        # Calculate statistics
        stats = DatasetStatistics.calculate_stats(turns)
        print("\nDataset Statistics:")
        print("=" * 50)
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        # Show some example turns
        if turns:
            print("\nExample Dialogue Turns:")
            print("=" * 50)
            for i, turn in enumerate(turns[:3], 1):
                print(f"\nTurn {i}:")
                print(f"  Context: {turn.context[:100]}...")
                print(f"  Response: {turn.response[:100]}...")
                if turn.metadata:
                    print(f"  Metadata: {turn.metadata}")
        
        # Optionally save output
        if len(sys.argv) > 2:
            output_format = sys.argv[2]
            output = parser.to_training_format(turns, output_format)
            output_file = f"output.{output_format}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\nSaved output to {output_file}")
    else:
        print("Usage: python dialogue_parser.py <file_or_directory> [output_format]")
        print("  output_format: jsonl, csv, or conversational (optional)")
        print("\nExample:")
        print("  python dialogue_parser.py messy_dataset/")
        print("  python dialogue_parser.py sample_dialogues.txt jsonl")
