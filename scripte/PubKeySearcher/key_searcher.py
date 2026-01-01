#!/usr/bin/env python3
"""
Ed25519 Public Key Pattern Searcher
Sucht nach ed25519 Public Keys mit speziellen Patterns am Anfang (Base58)
Nutzt alle verfügbaren CPU-Kerne für maximale Performance
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
    print(f"FEHLER: Benötigte Library nicht installiert: {e}")
    print("Bitte installieren mit: pip install cryptography base58")
    exit(1)


class KeySearcher:
    def __init__(self, patterns_file: str = "searchFor.txt", output_dir: str = "found_keys", max_pattern_length: int = 7):
        self.patterns = self.load_patterns(patterns_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_pattern_length = max_pattern_length
        
        print(f"Geladene Patterns: {len(self.patterns)}")
        print(f"Ausgabeordner: {self.output_dir.absolute()}")
        print(f"Max. Pattern-Länge für Duplikat-Vermeidung: {self.max_pattern_length}")
    
    def load_patterns(self, filename: str) -> Set[str]:
        """Lädt die Patterns aus der Datei"""
        patterns = set()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignoriere leere Zeilen und Kommentare
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except FileNotFoundError:
            print(f"FEHLER: {filename} nicht gefunden!")
            exit(1)
        
        return patterns
    
    def generate_and_check_key(self, worker_id: int, check_count: int, shared_counter, shared_found, found_patterns_dict, max_pattern_length: int) -> None:
        """
        Generiert Keys und prüft sie gegen die Patterns
        Läuft in einem separaten Prozess
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
                
                # Prüfe alle Patterns
                for pattern in self.patterns:
                    if public_base58.startswith(pattern):
                        # Prüfe ob kurzes Pattern (<=max_pattern_length) bereits gefunden wurde
                        if len(pattern) <= max_pattern_length:
                            if pattern in found_patterns_dict:
                                # Bereits gefunden, überspringe
                                continue
                            else:
                                # Markiere als gefunden
                                found_patterns_dict[pattern] = True
                        
                        # Match gefunden!
                        self.save_key(private_key, public_key, public_base58, pattern)
                        local_found += 1
                        with shared_found.get_lock():
                            shared_found.value += 1
                        print(f"\n🎉 Worker {worker_id}: MATCH gefunden! Pattern: {pattern}")
                        print(f"   Public Key: {public_base58[:32]}...")
                        break
                
                local_checked += 1
                
                # Update globalen Counter alle 1000 Keys
                if local_checked % 1000 == 0:
                    with shared_counter.get_lock():
                        shared_counter.value += 1000
                
                # Progress Update alle 10000 Keys
                if local_checked % 10000 == 0:
                    total = shared_counter.value
                    found = shared_found.value
                    print(f"Worker {worker_id}: {local_checked:,} Keys geprüft | "
                          f"Total: {total:,} | Gefunden: {found}")
        
        except KeyboardInterrupt:
            print(f"\nWorker {worker_id} wird beendet...")
            return
    
    def save_key(self, private_key, public_key, public_base58: str, pattern: str) -> None:
        """Speichert gefundenen Key in einer Datei"""
        epoch = int(datetime.now().timestamp())
        filename = f"{epoch}_{pattern}.txt"
        filepath = self.output_dir / filename
        
        # Konvertiere Keys zu PEM Format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # Speichere in Datei
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Pattern Match: {pattern}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Public Key (Base58): {public_base58}\n")
            f.write(f"\n{'='*70}\n")
            f.write(f"PRIVATE KEY (SICHER AUFBEWAHREN!):\n")
            f.write(f"{'='*70}\n\n")
            f.write(private_pem)
            f.write(f"\n{'='*70}\n")
            f.write(f"PUBLIC KEY:\n")
            f.write(f"{'='*70}\n\n")
            f.write(public_pem)
        
        print(f"   Gespeichert: {filepath.name}")
    
    def load_existing_patterns(self) -> Set[str]:
        """Lädt bereits gefundene Patterns aus vorhandenen Dateien im found_keys Ordner"""
        existing_patterns = set()
        
        if not self.output_dir.exists():
            return existing_patterns
        
        for file in self.output_dir.glob("*.txt"):
            # Extrahiere Pattern aus Dateinamen (Format: epoch_PATTERN.txt)
            parts = file.stem.split('_', 1)
            if len(parts) >= 2:
                pattern = parts[1]  # Pattern ist nach dem Epoch-Timestamp
                
                # Nur Patterns bis max_pattern_length berücksichtigen
                if len(pattern) <= self.max_pattern_length:
                    existing_patterns.add(pattern)
        
        return existing_patterns
    
    def run(self, num_workers: int = None) -> None:
        """
        Startet die Key-Suche mit mehreren Prozessen
        """
        if num_workers is None:
            num_workers = mp.cpu_count()
        
        # Lade bereits gefundene Patterns
        existing_patterns = self.load_existing_patterns()
        
        print(f"\n{'='*70}")
        print(f"Ed25519 Public Key Pattern Searcher (Base58)")
        print(f"{'='*70}")
        print(f"CPU Kerne: {num_workers}")
        print(f"Patterns: {len(self.patterns)}")
        print(f"Bereits gefunden (werden übersprungen): {len(existing_patterns)}")
        if existing_patterns:
            print(f"  -> {', '.join(sorted(existing_patterns))}")
        print(f"Hinweis: Patterns bis {self.max_pattern_length} Zeichen werden nur 1x gespeichert")
        print(f"\nStarte Suche... (Strg+C zum Beenden)\n")
        
        # Shared Counter für Statistiken
        shared_counter = mp.Value('i', 0)
        shared_found = mp.Value('i', 0)
        
        # Shared dict für bereits gefundene kurze Patterns
        manager = mp.Manager()
        found_patterns_dict = manager.dict()
        
        # Initialisiere mit bereits vorhandenen Patterns
        for pattern in existing_patterns:
            found_patterns_dict[pattern] = True
        
        # Starte Worker Prozesse
        processes = []
        try:
            for i in range(num_workers):
                p = mp.Process(
                    target=self.generate_and_check_key,
                    args=(i, 0, shared_counter, shared_found, found_patterns_dict, self.max_pattern_length)
                )
                p.start()
                processes.append(p)
            
            # Warte auf alle Prozesse
            for p in processes:
                p.join()
        
        except KeyboardInterrupt:
            print("\n\nBeende alle Worker...")
            for p in processes:
                p.terminate()
                p.join()
            
            print(f"\n{'='*70}")
            print(f"Suche beendet!")
            print(f"Geprüfte Keys: {shared_counter.value:,}")
            print(f"Gefundene Matches: {shared_found.value}")
            print(f"{'='*70}\n")


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description='Ed25519 Public Key Pattern Searcher für MeshCore',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--max-pattern-length',
        type=int,
        default=int(os.getenv('MAX_PATTERN_LENGTH', '7')),
        help='Maximale Pattern-Länge für Duplikat-Vermeidung (Standard: 7, kann auch via MAX_PATTERN_LENGTH ENV gesetzt werden)'
    )
    parser.add_argument(
        '--patterns-file',
        type=str,
        default='searchFor.txt',
        help='Pfad zur Pattern-Datei (Standard: searchFor.txt)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='found_keys',
        help='Ausgabe-Verzeichnis für gefundene Keys (Standard: found_keys)'
    )
    
    args = parser.parse_args()
    
    searcher = KeySearcher(
        patterns_file=args.patterns_file,
        output_dir=args.output_dir,
        max_pattern_length=args.max_pattern_length
    )
    
    # Nutze alle verfügbaren CPU-Kerne
    searcher.run()


if __name__ == "__main__":
    main()
