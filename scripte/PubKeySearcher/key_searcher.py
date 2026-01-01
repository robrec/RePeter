#!/usr/bin/env python3
"""
Ed25519 Public Key Pattern Searcher
Searches for ed25519 Public Keys with special patterns at the start (Base58)
Utilizes all available CPU cores for maximum performance
"""

import os
import multiprocessing as mp
import argparse
from datetime import datetime
from pathlib import Path
from typing import Set, List
import hashlib

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    import base58
except ImportError as e:
    print(f"ERROR: Required library not installed: {e}")
    print("Please install with: pip install cryptography base58")
    exit(1)


class KeySearcher:
    def __init__(self, patterns_file: str = "searchFor.txt", output_dir: str = "found_keys", max_pattern_length: int = 7):
        self.patterns = self.load_patterns(patterns_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_pattern_length = max_pattern_length
        
        print(f"Loaded Patterns: {len(self.patterns)}")
        print(f"Output Directory: {self.output_dir.absolute()}")
        print(f"Max Pattern Length for Duplicate Prevention: {self.max_pattern_length}")
    
    def load_patterns(self, filename: str) -> Set[str]:
        """Loads patterns from file"""
        patterns = set()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignore empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except FileNotFoundError:
            print(f"ERROR: {filename} not found!")
            exit(1)
        
        return patterns
    
    def generate_and_check_key(self, worker_id: int, check_count: int, shared_counter, shared_found, found_patterns_dict, max_pattern_length: int, session_found_list, start_time) -> None:
        """
        Generates keys and checks them against patterns
        Runs in a separate process
        """
        local_checked = 0
        local_found = 0
        
        try:
            while True:
                # Generiere neuen ed25519 Key
                private_key = ed25519.Ed25519PrivateKey.generate()
                public_key = private_key.public_key()
                
                # Konvertiere Public Key zu Bytes und dann zu Base58
                public_bytes = public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
                public_base58 = base58.b58encode(public_bytes).decode('ascii')
                
                # Check all patterns
                for pattern in self.patterns:
                    if public_base58.startswith(pattern):
                        # Check if short pattern (<=max_pattern_length) already found
                        if len(pattern) <= max_pattern_length:
                            if pattern in found_patterns_dict:
                                # Already found, skip
                                continue
                            else:
                                # Mark as found
                                found_patterns_dict[pattern] = True
                                # Add to session list
                                session_found_list.append(pattern)
                        
                        # Match found!
                        self.save_key(private_key, public_key, public_base58, pattern)
                        local_found += 1
                        with shared_found.get_lock():
                            shared_found.value += 1
                        print(f"\n🎉 Worker {worker_id}: MATCH found! Pattern: {pattern}")
                        print(f"   Public Key: {public_base58[:32]}...")
                        break
                
                local_checked += 1
                
                # Update global counter every 1000 keys
                if local_checked % 1000 == 0:
                    with shared_counter.get_lock():
                        shared_counter.value += 1000
                
                # Progress update every 10000 keys
                if local_checked % 10000 == 0:
                    total = shared_counter.value
                    found = shared_found.value
                    # Calculate keys per second
                    elapsed = datetime.now().timestamp() - start_time
                    keys_per_sec = int(total / elapsed) if elapsed > 0 else 0
                    # Show patterns found in this session
                    session_patterns = list(session_found_list)
                    patterns_str = ', '.join(sorted(session_patterns)) if session_patterns else 'none'
                    print(f"Worker {worker_id}: {local_checked:,} Keys checked | "
                          f"Total: {total:,} | Found: {found} | {keys_per_sec:,} keys/sec | Session: [{patterns_str}]")
        
        except KeyboardInterrupt:
            print(f"\nWorker {worker_id} stopping...")
            return
    
    def save_key(self, private_key, public_key, public_base58: str, pattern: str) -> None:
        """Saves found key to a file"""
        epoch = int(datetime.now().timestamp())
        filename = f"{epoch}_{pattern}.txt"
        filepath = self.output_dir / filename
        
        # Convert keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Pattern Match: {pattern}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Public Key (Base58): {public_base58}\n")
            f.write(f"\n{'='*70}\n")
            f.write(f"PRIVATE KEY (KEEP SECURE!):\n")
            f.write(f"{'='*70}\n\n")
            f.write(private_pem)
            f.write(f"\n{'='*70}\n")
            f.write(f"PUBLIC KEY:\n")
            f.write(f"{'='*70}\n\n")
            f.write(public_pem)
        
        print(f"   Saved: {filepath.name}")
    
    def load_existing_patterns(self) -> Set[str]:
        """Loads already found patterns from existing files in found_keys folder"""
        existing_patterns = set()
        
        if not self.output_dir.exists():
            return existing_patterns
        
        for file in self.output_dir.glob("*.txt"):
            # Extract pattern from filename (Format: epoch_PATTERN.txt)
            parts = file.stem.split('_', 1)
            if len(parts) >= 2:
                pattern = parts[1]  # Pattern is after the epoch timestamp
                
                # Only consider patterns up to max_pattern_length
                if len(pattern) <= self.max_pattern_length:
                    existing_patterns.add(pattern)
        
        return existing_patterns
    
    def run(self, num_workers: int = None) -> None:
        """
        Starts the key search with multiple processes
        """
        if num_workers is None:
            num_workers = mp.cpu_count()
        
        # Load already found patterns
        existing_patterns = self.load_existing_patterns()
        
        print(f"\n{'='*70}")
        print(f"Ed25519 Public Key Pattern Searcher (Base58)")
        print(f"{'='*70}")
        print(f"CPU Cores: {num_workers}")
        print(f"Patterns: {len(self.patterns)}")
        print(f"Already found (will be skipped): {len(existing_patterns)}")
        if existing_patterns:
            print(f"  -> {', '.join(sorted(existing_patterns))}")
        print(f"Note: Patterns up to {self.max_pattern_length} characters will only be saved once")
        print(f"\nStarting search... (Ctrl+C to stop)\n")
        
        # Shared counter for statistics
        shared_counter = mp.Value('i', 0)
        shared_found = mp.Value('i', 0)
        
        # Shared dict for already found short patterns
        manager = mp.Manager()
        found_patterns_dict = manager.dict()
        
        # Shared list for patterns found in this session
        session_found_list = manager.list()
        
        # Initialize with already existing patterns
        for pattern in existing_patterns:
            found_patterns_dict[pattern] = True
        
        # Record start time for keys/sec calculation
        start_time = datetime.now().timestamp()
        
        # Start worker processes
        processes = []
        try:
            for i in range(num_workers):
                p = mp.Process(
                    target=self.generate_and_check_key,
                    args=(i, 0, shared_counter, shared_found, found_patterns_dict, self.max_pattern_length, session_found_list, start_time)
                )
                p.start()
                processes.append(p)
            
            # Wait for all processes
            for p in processes:
                p.join()
        
        except KeyboardInterrupt:
            print("\n\nStopping all workers...")
            for p in processes:
                p.terminate()
                p.join()
            
            elapsed = datetime.now().timestamp() - start_time
            keys_per_sec = int(shared_counter.value / elapsed) if elapsed > 0 else 0
            
            print(f"\n{'='*70}")
            if session_found_list:
                print(f"Patterns found in this session: {', '.join(sorted(session_found_list))}")
            print(f"Search stopped!")
            print(f"Keys checked: {shared_counter.value:,}")
            print(f"Matches found: {shared_found.value}")
            print(f"Average speed: {keys_per_sec:,} keys/sec")
            print(f"{'='*70}\n")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Ed25519 Public Key Pattern Searcher for MeshCore',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--max-pattern-length',
        type=int,
        default=int(os.getenv('MAX_PATTERN_LENGTH', '7')),
        help='Maximum pattern length for duplicate prevention (Default: 7, can also be set via MAX_PATTERN_LENGTH ENV)'
    )
    parser.add_argument(
        '--patterns-file',
        type=str,
        default=os.getenv('PATTERNS_FILE', 'searchFor.txt'),
        help='Path to pattern file (Default: searchFor.txt, can also be set via PATTERNS_FILE ENV)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='found_keys',
        help='Output directory for found keys (Default: found_keys)'
    )
    
    args = parser.parse_args()
    
    searcher = KeySearcher(
        patterns_file=args.patterns_file,
        output_dir=args.output_dir,
        max_pattern_length=args.max_pattern_length
    )
    
    # Use all available CPU cores
    searcher.run()


if __name__ == "__main__":
    main()
