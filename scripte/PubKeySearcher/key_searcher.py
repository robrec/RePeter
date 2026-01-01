#!/usr/bin/env python3
"""
BreMesh MeshCore PubKey Searcher
Searches for ed25519 Public Keys with special patterns at the start (HEX)
Utilizes all available CPU cores for maximum performance
"""

import os
import sys
import multiprocessing as mp
import argparse
from datetime import datetime
from pathlib import Path
from typing import Set
import json
import threading
import time

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    import psutil
except ImportError as e:
    print(f"ERROR: Required library not installed: {e}")
    print("Please install with: pip install cryptography rich psutil")
    exit(1)


class KeySearcher:
    def __init__(self, patterns_file: str = "searchFor.txt", output_dir: str = "found_keys", max_pattern_length: int = 7, single_pattern: str = None):
        self.single_pattern_mode = single_pattern is not None
        if single_pattern:
            self.patterns = {single_pattern.upper()}
            print(f"Searching for single pattern: {single_pattern.upper()}")
        else:
            self.patterns = self.load_patterns(patterns_file)
            print(f"Loaded Patterns: {len(self.patterns)}")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_pattern_length = max_pattern_length
        self.stats_file = Path(".total_stats.json")
        self.total_all_time = self.load_total_stats()
        
        print(f"Output Directory: {self.output_dir.absolute()}")
        print(f"Max Pattern Length for Duplicate Prevention: {self.max_pattern_length}")
        print(f"Total Keys Checked All-Time: {self.total_all_time:,}")
    
    def load_patterns(self, filename: str) -> Set[str]:
        """Loads patterns from file"""
        patterns = set()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except FileNotFoundError:
            print(f"ERROR: {filename} not found!")
            exit(1)
        return patterns
    
    def load_total_stats(self) -> int:
        """Loads total all-time key count from stats file"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('total_keys_checked', 0)
        except Exception:
            pass
        return 0
    
    def save_total_stats(self, total_keys: int) -> None:
        """Saves total all-time key count to stats file"""
        try:
            data = {
                'total_keys_checked': self.total_all_time + total_keys,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    @staticmethod
    def format_number(num: int) -> str:
        """Format number with k/M suffix"""
        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}k"
        return str(num)
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds to readable time string"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m"
        elif seconds < 86400:
            return f"{seconds / 3600:.1f}h"
        elif seconds < 31536000:
            return f"{seconds / 86400:.1f}d"
        return f"{seconds / 31536000:.1f}y"
    
    @staticmethod
    def estimate_time(pattern_length: int, keys_per_sec: int) -> str:
        """Estimate time to find a pattern of given length"""
        if keys_per_sec == 0:
            return "N/A"
        possibilities = 16 ** pattern_length
        seconds = possibilities / keys_per_sec
        return KeySearcher.format_time(seconds)
    
    @staticmethod
    def display_process(display_queue, total_all_time, start_time, num_workers, pause_event, startup_info):
        """Dedicated process for displaying live statistics using Rich Live"""
        from rich.live import Live
        
        console = Console()
        last_total = 0
        last_found = 0
        found_keys_list = []
        is_paused = False
        # Track found patterns by length category - start with existing counts
        found_by_len = {k: v for k, v in startup_info['existing_counts'].items()}
        
        def build_panel():
            """Build the combined stats panel"""
            nonlocal is_paused
            is_paused = not pause_event.is_set()
            
            elapsed = max(0.1, datetime.now().timestamp() - start_time)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            keys_per_sec = int(last_total / elapsed) if elapsed > 0 else 0
            all_time_total = total_all_time + last_total
            
            content = Table.grid(padding=(0, 2))
            content.add_column(justify="right", style="bright_cyan")
            content.add_column(justify="left", style="bright_white")
            content.add_column(justify="right", style="bright_cyan")
            content.add_column(justify="left", style="bright_white")
            
            # Config section
            content.add_row(
                "[bold bright_cyan]Patterns:[/bold bright_cyan]", f"[bold green]{startup_info['num_patterns']}[/bold green]",
                "[bold bright_cyan]Workers:[/bold bright_cyan]", f"[bold cyan]{num_workers}[/bold cyan]"
            )
            if startup_info['existing_patterns']:
                content.add_row(
                    "[bold bright_cyan]Already Found:[/bold bright_cyan]", f"[bold yellow]{startup_info['num_existing']}[/bold yellow]",
                    "", ""
                )
            
            # Separator
            content.add_row("[dim]" + "─" * 40 + "[/dim]", "", "", "")
            
            # Status
            if is_paused:
                status = "[bold yellow]⏸ PAUSED[/bold yellow]"
            else:
                status = "[bold green]▶ RUNNING[/bold green]"
            content.add_row("[bold bright_cyan]Status:[/bold bright_cyan]", status, "", "")
            
            # Stats
            content.add_row(
                "[bold bright_cyan]Session:[/bold bright_cyan]", f"[bold green]{KeySearcher.format_number(last_total)}[/bold green] keys",
                "[bold bright_cyan]All-Time:[/bold bright_cyan]", f"[bold blue]{KeySearcher.format_number(all_time_total)}[/bold blue] keys"
            )
            content.add_row(
                "[bold bright_cyan]Found:[/bold bright_cyan]", f"[bold yellow]{last_found}[/bold yellow] matches",
                "[bold bright_cyan]Speed:[/bold bright_cyan]", f"[bold magenta]{KeySearcher.format_number(keys_per_sec)}[/bold magenta] keys/s"
            )
            
            # CPU bar with better visuals
            bar_width = 20
            filled = int(cpu_percent / 100 * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            bar_color = "red" if cpu_percent > 80 else ("yellow" if cpu_percent > 50 else "green")
            content.add_row(
                "[bold bright_cyan]Duration:[/bold bright_cyan]", f"[bold white]{KeySearcher.format_time(elapsed)}[/bold white]",
                "[bold bright_cyan]CPU:[/bold bright_cyan]", f"[{bar_color}]{bar}[/{bar_color}] [bold white]{cpu_percent:.0f}%[/bold white]"
            )
            
            # WoW-style rarity colors
            COLOR_ARTIFACT = "#FF8000"   # 10+ chars - Orange
            COLOR_EPIC = "#A335EE"       # 9 chars - Purple
            COLOR_RARE = "#0070DD"       # 8 chars - Blue
            COLOR_UNCOMMON = "#1EFF00"   # 7 chars - Green
            COLOR_COMMON = "#FFFFFF"     # 6 chars - White
            COLOR_POOR = "#9D9D9D"       # <=5 chars - Gray
            
            # Remaining patterns to find (total and by length)
            # found_by_len already includes existing + session found
            total_found = sum(found_by_len.values())
            remaining = startup_info['num_patterns'] - total_found
            pc = startup_info['pattern_counts']
            # Format: found/total for each category
            fbl = found_by_len
            
            # Estimates section
            content.add_row("", "", "", "")
            content.add_row("[dim]" + "─" * 40 + "[/dim]", "", "", "")
            content.add_row(
                "[bold bright_yellow]Time Estimates:[/bold bright_yellow]", "",
                "[bold bright_cyan]Remaining:[/bold bright_cyan]", f"[bold white]{remaining}[/bold white] patterns"
            )
            content.add_row(
                "[dim]  5 chars:[/dim]", f"[{COLOR_POOR}]{KeySearcher.estimate_time(5, keys_per_sec)}[/{COLOR_POOR}]  [dim]({fbl[5]}/{pc[5]})[/dim]",
                "[dim]  6 chars:[/dim]", f"[{COLOR_COMMON}]{KeySearcher.estimate_time(6, keys_per_sec)}[/{COLOR_COMMON}]  [dim]({fbl[6]}/{pc[6]})[/dim]"
            )
            content.add_row(
                "[dim]  7 chars:[/dim]", f"[{COLOR_UNCOMMON}]{KeySearcher.estimate_time(7, keys_per_sec)}[/{COLOR_UNCOMMON}]  [dim]({fbl[7]}/{pc[7]})[/dim]",
                "[dim]  8 chars:[/dim]", f"[{COLOR_RARE}]{KeySearcher.estimate_time(8, keys_per_sec)}[/{COLOR_RARE}]  [dim]({fbl[8]}/{pc[8]})[/dim]"
            )
            content.add_row(
                "[dim]  9 chars:[/dim]", f"[{COLOR_EPIC}]{KeySearcher.estimate_time(9, keys_per_sec)}[/{COLOR_EPIC}]  [dim]({fbl[9]}/{pc[9]})[/dim]",
                "[dim]  10+ chars:[/dim]", f"[{COLOR_ARTIFACT}]{KeySearcher.estimate_time(10, keys_per_sec)}[/{COLOR_ARTIFACT}]  [dim]({fbl[10]}/{pc[10]})[/dim]"
            )
            
            # Found keys section with WoW-style rarity indicators
            if found_keys_list:
                content.add_row("", "", "", "")
                content.add_row("[dim]" + "─" * 40 + "[/dim]", "", "", "")
                content.add_row("[bold green]Found Keys:[/bold green]", "", "", "")
                for pattern, preview in found_keys_list[-5:]:
                    pattern_len = len(pattern)
                    # WoW-style rarity indicators based on pattern length
                    if pattern_len >= 10:
                        symbol = f"[{COLOR_ARTIFACT}]⭐💎[/{COLOR_ARTIFACT}]"
                        pattern_style = f"[bold {COLOR_ARTIFACT}]"
                        end_style = f"[/bold {COLOR_ARTIFACT}]"
                    elif pattern_len >= 9:
                        symbol = f"[{COLOR_EPIC}]⭐[/{COLOR_EPIC}]"
                        pattern_style = f"[bold {COLOR_EPIC}]"
                        end_style = f"[/bold {COLOR_EPIC}]"
                    elif pattern_len >= 8:
                        symbol = f"[{COLOR_RARE}]✨[/{COLOR_RARE}]"
                        pattern_style = f"[bold {COLOR_RARE}]"
                        end_style = f"[/bold {COLOR_RARE}]"
                    elif pattern_len >= 7:
                        symbol = f"[{COLOR_UNCOMMON}]•[/{COLOR_UNCOMMON}]"
                        pattern_style = f"[{COLOR_UNCOMMON}]"
                        end_style = f"[/{COLOR_UNCOMMON}]"
                    elif pattern_len >= 6:
                        symbol = f"[{COLOR_COMMON}]•[/{COLOR_COMMON}]"
                        pattern_style = f"[{COLOR_COMMON}]"
                        end_style = f"[/{COLOR_COMMON}]"
                    else:
                        symbol = f"[{COLOR_POOR}]•[/{COLOR_POOR}]"
                        pattern_style = f"[{COLOR_POOR}]"
                        end_style = f"[/{COLOR_POOR}]"
                    
                    # Pad pattern for alignment
                    padded_pattern = pattern.ljust(16)
                    content.add_row(
                        f"  {symbol} {pattern_style}{padded_pattern}{end_style}", 
                        f"[dim]{preview}...[/dim]", 
                        "", ""
                    )
            
            return Panel(
                content,
                title="[bold bright_white on blue] 🔍 BreMesh MeshCore PubKey Searcher [/bold bright_white on blue]",
                subtitle="[dim white]Ctrl+C to stop • P to pause • R to resume[/dim white]",
                border_style="bright_blue",
                padding=(1, 2)
            )
        
        try:
            # Use Live with screen=True for flicker-free updates
            with Live(build_panel(), console=console, screen=True, refresh_per_second=4) as live:
                while True:
                    try:
                        msg = display_queue.get(timeout=0.5)
                        
                        if msg == 'STOP':
                            break
                        
                        if isinstance(msg, dict):
                            if msg.get('force_update'):
                                live.update(build_panel())
                                continue
                            
                            last_total = msg.get('total', last_total)
                            last_found = msg.get('found', last_found)
                            
                            if 'new_key' in msg:
                                found_keys_list.append((msg['new_key']['pattern'], msg['new_key']['key_preview']))
                                # Update found count by length
                                plen = len(msg['new_key']['pattern'])
                                if plen <= 5:
                                    found_by_len[5] += 1
                                elif plen >= 10:
                                    found_by_len[10] += 1
                                else:
                                    found_by_len[plen] += 1
                            
                            live.update(build_panel())
                    
                    except Exception:
                        # Timeout - auto refresh
                        live.update(build_panel())
        
        except KeyboardInterrupt:
            pass
    
    def generate_and_check_key(self, worker_id: int, shared_counter, shared_found,
                                found_patterns_dict, session_found_list, start_time,
                                display_queue, pause_event, stop_event, single_pattern_mode) -> None:
        """Worker process for key generation"""
        local_checked = 0
        
        try:
            while not stop_event.is_set():
                pause_event.wait()
                
                private_key = ed25519.Ed25519PrivateKey.generate()
                public_key = private_key.public_key()
                
                public_bytes = public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
                public_hex = public_bytes.hex().upper()
                
                private_bytes = private_key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                for pattern in self.patterns:
                    if public_hex.startswith(pattern.upper()):
                        if len(pattern) <= self.max_pattern_length:
                            if pattern in found_patterns_dict:
                                continue
                            found_patterns_dict[pattern] = True
                            session_found_list.append(pattern)
                        
                        self.save_key(private_bytes, public_bytes, public_hex, pattern)
                        
                        with shared_found.get_lock():
                            shared_found.value += 1
                        
                        # All workers send new_key message
                        display_queue.put({
                            'total': shared_counter.value,
                            'found': shared_found.value,
                            'new_key': {'pattern': pattern, 'key_preview': public_hex[:16]}
                        })
                        
                        # In single pattern mode, signal all workers to stop
                        if single_pattern_mode:
                            stop_event.set()
                        break
                
                local_checked += 1
                
                if local_checked % 1000 == 0:
                    with shared_counter.get_lock():
                        shared_counter.value += 1000
                
                if worker_id == 0 and local_checked % 10000 == 0:
                    total = shared_counter.value
                    display_queue.put({'total': total, 'found': shared_found.value})
                    
                    if total % 1000000 < 10000:
                        self.save_total_stats(total)
        
        except KeyboardInterrupt:
            return
    
    def save_key(self, private_bytes: bytes, public_bytes: bytes, public_hex: str, pattern: str) -> None:
        """Save found key to file"""
        epoch = int(datetime.now().timestamp())
        filepath = self.output_dir / f"{epoch}_{pattern}.txt"
        private_hex = (private_bytes + public_bytes).hex().upper()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Pattern Match: {pattern}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Public Key (HEX): {public_hex}\n")
            f.write(f"Private Key (HEX): {private_hex}\n")
            f.write(f"\n{'='*70}\n")
            f.write(f"MeshCore Import Format:\n")
            f.write(f"{'='*70}\n\n")
            f.write('{\n')
            f.write(f'  "public_key": "{public_hex}",\n')
            f.write(f'  "private_key": "{private_hex}"\n')
            f.write('}\n')
    
    def load_existing_patterns(self) -> Set[str]:
        """Load already found patterns"""
        existing = set()
        if not self.output_dir.exists():
            return existing
        
        for file in self.output_dir.glob("*.txt"):
            parts = file.stem.split('_', 1)
            if len(parts) >= 2:
                existing.add(parts[1])
        return existing
    
    def run(self, num_workers: int = None) -> None:
        """Start the key search"""
        if num_workers is None:
            num_workers = mp.cpu_count()
        
        existing_patterns = self.load_existing_patterns()
        console = Console()
        
        # Count patterns by length category
        pattern_counts = {5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}  # 10 = 10+
        for p in self.patterns:
            plen = len(p)
            if plen <= 5:
                pattern_counts[5] += 1
            elif plen >= 10:
                pattern_counts[10] += 1
            else:
                pattern_counts[plen] += 1
        
        # Count already found (existing) patterns by length
        # Only count patterns that are in the current search list
        existing_counts = {5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        patterns_upper = {p.upper() for p in self.patterns}
        for p in existing_patterns:
            if p.upper() not in patterns_upper:
                continue  # Skip patterns not in current search list
            plen = len(p)
            if plen <= 5:
                existing_counts[5] += 1
            elif plen >= 10:
                existing_counts[10] += 1
            else:
                existing_counts[plen] += 1
        
        # Prepare startup info for display process
        startup_info = {
            'num_patterns': len(self.patterns),
            'max_pattern_length': self.max_pattern_length,
            'output_dir': str(self.output_dir.absolute()),
            'num_existing': len(existing_patterns),
            'existing_patterns': ', '.join(sorted(existing_patterns)) if existing_patterns else '',
            'pattern_counts': pattern_counts,
            'existing_counts': existing_counts
        }
        
        # Shared state
        shared_counter = mp.Value('i', 0)
        shared_found = mp.Value('i', 0)
        manager = mp.Manager()
        found_patterns_dict = manager.dict()
        session_found_list = manager.list()
        display_queue = manager.Queue()
        pause_event = mp.Event()
        pause_event.set()
        stop_event = mp.Event()  # For single pattern mode auto-exit
        
        for pattern in existing_patterns:
            found_patterns_dict[pattern] = True
        
        start_time = datetime.now().timestamp()
        
        # Keyboard listener
        def keyboard_listener():
            try:
                import msvcrt
                while True:
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8', errors='ignore').upper()
                        if key == 'P' and pause_event.is_set():
                            pause_event.clear()
                            display_queue.put({'force_update': True})
                        elif key == 'R' and not pause_event.is_set():
                            pause_event.set()
                            display_queue.put({'force_update': True})
                    time.sleep(0.1)
            except Exception:
                pass
        
        kb_thread = threading.Thread(target=keyboard_listener, daemon=True)
        kb_thread.start()
        
        # Start display process
        display_proc = mp.Process(
            target=self.display_process,
            args=(display_queue, self.total_all_time, start_time, num_workers, pause_event, startup_info)
        )
        display_proc.start()
        
        # Start workers
        processes = []
        try:
            for i in range(num_workers):
                p = mp.Process(
                    target=self.generate_and_check_key,
                    args=(i, shared_counter, shared_found, found_patterns_dict,
                          session_found_list, start_time, display_queue, pause_event,
                          stop_event, self.single_pattern_mode)
                )
                p.start()
                processes.append(p)
            
            for p in processes:
                p.join()
            
            # Workers finished (single pattern found or all patterns found)
            if stop_event.is_set():
                time.sleep(0.5)  # Let display catch up
                display_queue.put('STOP')
                display_proc.join(timeout=2)
                if display_proc.is_alive():
                    display_proc.terminate()
                
                self.save_total_stats(shared_counter.value)
                
                elapsed = datetime.now().timestamp() - start_time
                keys_per_sec = int(shared_counter.value / elapsed) if elapsed > 0 else 0
                
                # Success Summary
                summary = Table.grid(padding=(0, 2))
                summary.add_column(style="cyan", justify="right")
                summary.add_column(style="bright_white", justify="left")
                
                summary.add_row("Session Keys:", f"[bold green]{shared_counter.value:,}[/bold green]")
                summary.add_row("All-Time Keys:", f"[bold blue]{self.total_all_time + shared_counter.value:,}[/bold blue]")
                summary.add_row("Matches Found:", f"[bold yellow]{shared_found.value}[/bold yellow]")
                summary.add_row("Average Speed:", f"[bold magenta]{keys_per_sec:,} keys/sec[/bold magenta]")
                summary.add_row("Duration:", f"[cyan]{self.format_time(elapsed)}[/cyan]")
                
                if session_found_list:
                    summary.add_row("")
                    summary.add_row("Found Patterns:", f"[bold green]{', '.join(sorted(session_found_list))}[/bold green]")
                
                console.print("\n")
                console.print(Panel(
                    summary,
                    title="[bold green]✓ Pattern Found![/bold green]",
                    border_style="green",
                    padding=(1, 2)
                ))
                console.print("\n")
                return
        
        except KeyboardInterrupt:
            display_queue.put('STOP')
            
            for p in processes:
                p.terminate()
                p.join()
            
            display_proc.join(timeout=2)
            if display_proc.is_alive():
                display_proc.terminate()
            
            self.save_total_stats(shared_counter.value)
            
            elapsed = datetime.now().timestamp() - start_time
            keys_per_sec = int(shared_counter.value / elapsed) if elapsed > 0 else 0
            
            # Summary
            summary = Table.grid(padding=(0, 2))
            summary.add_column(style="cyan", justify="right")
            summary.add_column(style="bright_white", justify="left")
            
            summary.add_row("Session Keys:", f"[bold green]{shared_counter.value:,}[/bold green]")
            summary.add_row("All-Time Keys:", f"[bold blue]{self.total_all_time + shared_counter.value:,}[/bold blue]")
            summary.add_row("Matches Found:", f"[bold yellow]{shared_found.value}[/bold yellow]")
            summary.add_row("Average Speed:", f"[bold magenta]{keys_per_sec:,} keys/sec[/bold magenta]")
            summary.add_row("Duration:", f"[cyan]{self.format_time(elapsed)}[/cyan]")
            
            if session_found_list:
                summary.add_row("")
                summary.add_row("Found Patterns:", f"[bold green]{', '.join(sorted(session_found_list))}[/bold green]")
            
            console.print("\n")
            console.print(Panel(
                summary,
                title="[bold red]⏸️  Search Stopped[/bold red]",
                border_style="red",
                padding=(1, 2)
            ))
            console.print("\n")


def main():
    parser = argparse.ArgumentParser(description='Ed25519 Public Key Pattern Searcher for MeshCore')
    parser.add_argument('--max-pattern-length', type=int, default=int(os.getenv('MAX_PATTERN_LENGTH', '7')))
    parser.add_argument('--patterns-file', type=str, default=os.getenv('PATTERNS_FILE', 'searchFor.txt'))
    parser.add_argument('--output-dir', type=str, default='found_keys')
    parser.add_argument('--pattern', '-p', type=str, help='Search for a single pattern instead of using patterns file')
    
    args = parser.parse_args()
    
    searcher = KeySearcher(
        patterns_file=args.patterns_file,
        output_dir=args.output_dir,
        max_pattern_length=args.max_pattern_length,
        single_pattern=args.pattern
    )
    searcher.run()


if __name__ == "__main__":
    main()
