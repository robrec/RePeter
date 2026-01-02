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
from typing import Set, Dict, Tuple
import json
import threading
import time
import re

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
    import psutil
except ImportError as e:
    print(f"ERROR: Required library not installed: {e}")
    print("Please install with: pip install cryptography rich psutil")
    exit(1)

# Default configuration
DEFAULT_UNIQUE_MIN = 8  # Patterns with length <= this value are kept unique


class KeySearcher:
    # Rarity colors by pattern length
    COLOR_ARTIFACT = "#FF8000"   # 10+ chars - Orange
    COLOR_EPIC = "#A335EE"       # 9 chars - Purple
    COLOR_RARE = "#0070DD"       # 8 chars - Blue
    COLOR_UNCOMMON = "#1EFF00"   # 7 chars - Green
    COLOR_COMMON = "#FFFFFF"     # 6 chars - White
    COLOR_POOR = "#9D9D9D"       # <=5 chars - Gray
    
    @staticmethod
    def is_regex_pattern(pattern: str) -> bool:
        """Check if pattern contains regex special characters"""
        regex_chars = r'.[]*+?{}()|^$\\'
        return any(c in regex_chars for c in pattern)
    
    @staticmethod
    def calculate_regex_possibilities(pattern: str) -> int:
        """Calculate total number of possible keys for a regex pattern"""
        if not KeySearcher.is_regex_pattern(pattern):
            return 1  # Plain pattern = 1 possibility
        
        # Special case: for patterns with variable-length quantifiers like {1,57}
        # These represent multiple different patterns (different lengths)
        # Count the number of different patterns, not combinations
        
        # Check for {min,max} quantifiers that create multiple pattern lengths
        range_quantifiers = re.findall(r'\{(\d+),(\d+)\}', pattern)
        if range_quantifiers:
            # For patterns like DEADBEE{1,57}F
            # This represents 57 different patterns (one for each length)
            total_patterns = 0
            for min_val, max_val in range_quantifiers:
                total_patterns += int(max_val) - int(min_val) + 1
            if total_patterns > 1:
                return total_patterns
        
        possibilities = 1
        temp_pattern = pattern
        
        # Count character classes [0-9A-F] = 16 possibilities
        char_classes = re.findall(r'\[[^\]]+\]', pattern)
        for cc in char_classes:
            # Count unique chars in character class
            if '0-9A-F' in cc or '0-9a-f' in cc or 'A-F0-9' in cc:
                count = 16  # Full HEX range
            elif '0-9' in cc:
                count = 10  # Digits only
            elif 'A-F' in cc or 'a-f' in cc:
                count = 6  # Letters only
            else:
                # Count individual characters
                chars = cc.replace('[', '').replace(']', '')
                count = len(set(chars.upper()))
            
            # Find quantifiers for this class
            # Replace the class with a placeholder
            temp_pattern = temp_pattern.replace(cc, 'X', 1)
            
            # Check if followed by quantifier
            match = re.search(r'X\{(\d+)(?:,(\d*))?\}', temp_pattern)
            if match:
                min_count = int(match.group(1))
                max_count = int(match.group(2)) if match.group(2) else min_count
                # Use minimum count for calculation
                possibilities *= (count ** min_count)
                temp_pattern = temp_pattern.replace(match.group(0), '', 1)
            else:
                possibilities *= count
        
        return possibilities
    
    @staticmethod
    def validate_pattern(pattern: str) -> Tuple[bool, str, int]:
        """Validate pattern - supports both plain HEX and regex patterns.
        Returns: (is_valid, error_message, effective_length)
        """
        if not pattern:
            return False, "Pattern is empty", 0
        
        # Check if it's a regex pattern
        if KeySearcher.is_regex_pattern(pattern):
            try:
                # Try to compile the regex
                compiled = re.compile(pattern, re.IGNORECASE)
                
                # Validate that the pattern only contains HEX-compatible elements
                # Check for character classes containing only HEX chars
                # Remove valid HEX patterns to see if anything invalid remains
                temp_check = pattern
                # Remove HEX character classes
                temp_check = re.sub(r'\[0-9A-Fa-f\-\]]+', '', temp_check)
                # Remove HEX literals
                temp_check = re.sub(r'[0-9A-Fa-f]', '', temp_check)
                # Remove valid regex syntax
                temp_check = re.sub(r'[\{\}\*\+\?\|\(\)\^\\]', '', temp_check)
                # Remove numbers (for quantifiers)
                temp_check = re.sub(r'\d+', '', temp_check)
                
                # If anything remains that's not whitespace/comma, it might be invalid
                remaining = temp_check.replace(',', '').strip()
                if remaining and any(c.isalpha() and c not in 'xXdDwWsS' for c in remaining):
                    return False, "Regex pattern contains non-HEX elements", 0
                
                # Calculate effective length (minimum match length)
                # For regex patterns, calculate the actual minimum match length
                effective_length = 0
                
                # Remove character classes and count fixed characters
                temp_pattern = pattern
                # Replace character classes like [0-9A-F] with single placeholder
                temp_pattern = re.sub(r'\[[^\]]+\]', 'X', temp_pattern)
                # Replace quantifiers {n} with n repetitions of previous char
                for match in re.finditer(r'(.?)\{(\d+)(?:,\d*)?\}', temp_pattern):
                    char_before = match.group(1) if match.group(1) else 'X'
                    count = int(match.group(2))
                    effective_length += count
                    # Remove the quantifier from pattern
                    temp_pattern = temp_pattern.replace(match.group(0), '', 1)
                
                # Count remaining characters (fixed chars and placeholders)
                effective_length += len(re.sub(r'[^A-Z0-9X]', '', temp_pattern))
                
                effective_length = max(1, effective_length)
                
                return True, "", effective_length
                
            except re.error as e:
                return False, f"Invalid regex pattern: {e}", 0
        else:
            # Plain HEX pattern
            if not all(c in '0123456789ABCDEFabcdef' for c in pattern):
                return False, "Pattern contains non-HEX characters (allowed: 0-9, A-F)", 0
            return True, "", len(pattern)
    
    def __init__(self, patterns_file: str = "searchFor.txt", output_dir: str = "found_keys", unique_min: int = DEFAULT_UNIQUE_MIN, single_pattern: str = None, verbose: bool = False, simple_console: bool = False, simple_console_long: bool = False):
        self.is_regex_search = single_pattern and self.is_regex_pattern(single_pattern)
        # single_pattern_mode = auto-exit after first find (only for fixed patterns, not regex)
        self.single_pattern_mode = single_pattern is not None and not self.is_regex_search
        self.verbose = verbose
        self.simple_console = simple_console or simple_console_long
        self.pattern_regexes: Dict[str, re.Pattern] = {}  # Store compiled regex patterns
        self.simple_console_long = simple_console_long
        self.patterns_file = patterns_file  # Store for hot-reload
        self.pattern_metadata = {}  # Store pattern metadata (effective_length, possibilities)
        
        # Set output_dir early so it's available for load_existing_regex_keys
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if single_pattern:
            is_valid, error_msg, effective_len = self.validate_pattern(single_pattern)
            if not is_valid:
                print(f"\n❌ ERROR: {error_msg}")
                print("Allowed: HEX characters (0-9, A-F) or regex patterns\n")
                exit(1)
            
            pattern_key = single_pattern.upper() if not self.is_regex_pattern(single_pattern) else single_pattern
            self.patterns = {pattern_key}
            
            # Store metadata
            possibilities = self.calculate_regex_possibilities(single_pattern)
            self.pattern_metadata[pattern_key] = {
                'effective_length': effective_len,
                'possibilities': possibilities,
                'found_keys': set()  # Track found keys for this pattern
            }
            
            # Load already found keys if this is a regex pattern
            if self.is_regex_pattern(single_pattern) and possibilities > 1:
                existing_keys = self.load_existing_regex_keys(single_pattern)
                if existing_keys:
                    self.pattern_metadata[pattern_key]['found_keys'] = existing_keys
                    # Check if all possibilities are found
                    if len(existing_keys) >= possibilities:
                        console = Console()
                        safe_name = re.sub(r'[^\w]', '_', single_pattern)
                        console.print(f"\n✅ [bold green]All {possibilities} keys for pattern '{single_pattern}' already found![/bold green]")
                        console.print(f"   [dim]File: found_keys/{safe_name}_all.txt[/dim]\n")
                        exit(0)
                    else:
                        console = Console()
                        percent = len(existing_keys) / possibilities * 100
                        console.print(f"\n[bold yellow]Continuing search for pattern '{single_pattern}'[/bold yellow]")
                        console.print(f"   [dim]Already found: {len(existing_keys)}/{possibilities} ({percent:.1f}%)[/dim]")
                        console.print(f"   [dim]Searching for remaining: {possibilities - len(existing_keys)} keys[/dim]\n")
                        import time
                        time.sleep(2)  # Pause so user can see the message
            
            # Compile if regex
            if self.is_regex_pattern(single_pattern):
                self.pattern_regexes[pattern_key] = re.compile(single_pattern, re.IGNORECASE)
        else:
            self.patterns = self.load_patterns(patterns_file)
        
        self.unique_min = unique_min
        self.stats_file = Path(".total_stats.json")
        self.total_all_time = self.load_total_stats()
    
    def load_patterns(self, filename: str) -> Set[str]:
        """Loads patterns from file"""
        patterns = set()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    line = line.strip()
                    if line and not line.startswith('#'):
                        is_valid, error_msg, effective_len = self.validate_pattern(line)
                        if not is_valid:
                            print(f"ERROR: Invalid pattern '{line}' on line {line_num} in {filename}")
                            print(f"       {error_msg}")
                            exit(1)
                        
                        # Store uppercase for plain patterns, original for regex
                        pattern_key = line.upper() if not self.is_regex_pattern(line) else line
                        patterns.add(pattern_key)
                        
                        # Store metadata for all patterns
                        possibilities = self.calculate_regex_possibilities(line)
                        self.pattern_metadata[pattern_key] = {
                            'effective_length': effective_len,
                            'possibilities': possibilities,
                            'found_keys': set()
                        }
                        
                        # Load existing keys for regex patterns
                        if self.is_regex_pattern(line) and possibilities > 1:
                            existing_keys = self.load_existing_regex_keys(line)
                            if existing_keys:
                                self.pattern_metadata[pattern_key]['found_keys'] = existing_keys
                        
                        # Compile regex patterns
                        if self.is_regex_pattern(line):
                            try:
                                self.pattern_regexes[pattern_key] = re.compile(line, re.IGNORECASE)
                            except re.error:
                                pass  # Already validated, but just in case
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
    def get_rarity_style(pattern_length: int):
        """Get symbol and style for a pattern based on its length"""
        if pattern_length >= 11:
            return "[bold red]***[/bold red]", "[bold red]", "[/bold red]"
        elif pattern_length >= 10:
            return f"[{KeySearcher.COLOR_ARTIFACT}]**[/{KeySearcher.COLOR_ARTIFACT}]", f"[bold {KeySearcher.COLOR_ARTIFACT}]", f"[/bold {KeySearcher.COLOR_ARTIFACT}]"
        elif pattern_length >= 9:
            return f"[{KeySearcher.COLOR_EPIC}]*[/{KeySearcher.COLOR_EPIC}]", f"[bold {KeySearcher.COLOR_EPIC}]", f"[/bold {KeySearcher.COLOR_EPIC}]"
        elif pattern_length >= 8:
            return f"[{KeySearcher.COLOR_RARE}]+[/{KeySearcher.COLOR_RARE}]", f"[bold {KeySearcher.COLOR_RARE}]", f"[/bold {KeySearcher.COLOR_RARE}]"
        elif pattern_length >= 7:
            return f"[{KeySearcher.COLOR_UNCOMMON}]•[/{KeySearcher.COLOR_UNCOMMON}]", f"[{KeySearcher.COLOR_UNCOMMON}]", f"[/{KeySearcher.COLOR_UNCOMMON}]"
        elif pattern_length >= 6:
            return f"[{KeySearcher.COLOR_COMMON}]•[/{KeySearcher.COLOR_COMMON}]", f"[{KeySearcher.COLOR_COMMON}]", f"[/{KeySearcher.COLOR_COMMON}]"
        else:
            return f"[{KeySearcher.COLOR_POOR}]•[/{KeySearcher.COLOR_POOR}]", f"[{KeySearcher.COLOR_POOR}]", f"[/{KeySearcher.COLOR_POOR}]"
    
    @staticmethod
    def build_found_keys_table(found_keys_list):
        """Build the found keys table content"""
        found_content = Table.grid(padding=(0, 2))
        found_content.add_column(justify="left")
        found_content.add_column(justify="left")
        
        for pattern, preview, effective_len in found_keys_list[-5:]:
            symbol, pattern_style, end_style = KeySearcher.get_rarity_style(effective_len)
            padded_pattern = pattern.ljust(16)
            found_content.add_row(
                f"{symbol} {pattern_style}{padded_pattern}{end_style}", 
                f"[dim]{preview}[/dim]"
            )
        
        return found_content
    
    @staticmethod
    def display_process(display_queue, total_all_time, start_time, num_workers, pause_event, cpu_limit_event, startup_info):
        """Dedicated process for displaying live statistics using Rich Live"""
        from rich.live import Live
        
        console = Console()
        last_total = 0
        last_found = 0
        found_keys_list = []
        is_paused = False
        # Track found patterns by length category - start with existing counts
        found_by_len = {k: v for k, v in startup_info['existing_counts'].items()}
        # Track remaining pattern lengths for ETA calculation
        remaining_lengths = list(startup_info['remaining_pattern_lengths'])
        # Track remaining possibilities per pattern for accurate ETA
        pattern_metadata = {p: dict(meta) for p, meta in startup_info['pattern_metadata'].items()}
        last_find_time = start_time  # Time of last found key (or start)
        
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
            is_cpu_limited = cpu_limit_event.is_set()
            workers_text = f"[bold cyan]{num_workers}[/bold cyan]"
            if is_cpu_limited:
                workers_paused = max(1, int(num_workers * 0.25))
                workers_active = num_workers - workers_paused
                workers_text = f"[bold cyan]{num_workers}[/bold cyan] [dim yellow](Limit: {workers_active})[/dim yellow]"
            
            content.add_row(
                "[bold bright_cyan]Patterns:[/bold bright_cyan]", f"[bold green]{startup_info['num_patterns']}[/bold green]",
                "[bold bright_cyan]Workers:[/bold bright_cyan]", workers_text
            )
            if startup_info['existing_patterns']:
                content.add_row(
                    "[bold bright_cyan]Already Found:[/bold bright_cyan]", f"[bold yellow]{startup_info['num_existing']}[/bold yellow]",
                    "", ""
                )
            content.add_row(
                "[bold bright_cyan]Unique Min:[/bold bright_cyan]", f"[dim]≤{startup_info['unique_min']} chars[/dim]",
                "", ""
            )
            
            # Separator
            content.add_row("[dim]" + "─" * 40 + "[/dim]", "", "", "")
            
            # Status
            is_cpu_limited = cpu_limit_event.is_set()
            if is_paused:
                status = "[bold yellow]⏸ PAUSED[/bold yellow]"
            else:
                status = "[bold green]▶ RUNNING[/bold green]"
                if is_cpu_limited:
                    workers_paused = max(1, int(num_workers * 0.25))
                    workers_active = num_workers - workers_paused
                    target_pct = int((workers_active / num_workers) * 100)
                    status += f" [dim yellow](CPU ~{target_pct}%)[/dim yellow]"
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
            
            # Remaining patterns to find (total and by length)
            # For regex patterns, we need to count total possible keys, not pattern count
            total_found = sum(found_by_len.values())
            pc = startup_info['pattern_counts']
            total_possible = sum(pc.values())  # Total possible keys across all patterns
            remaining = total_possible - total_found
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
                "[dim]  1 char:[/dim]", f"[{KeySearcher.COLOR_POOR}]{KeySearcher.estimate_time(1, keys_per_sec)}[/{KeySearcher.COLOR_POOR}]  [dim]({fbl.get(1,0)}/{pc.get(1,0)})[/dim]",
                "[dim]  2 chars:[/dim]", f"[{KeySearcher.COLOR_POOR}]{KeySearcher.estimate_time(2, keys_per_sec)}[/{KeySearcher.COLOR_POOR}]  [dim]({fbl.get(2,0)}/{pc.get(2,0)})[/dim]"
            )
            content.add_row(
                "[dim]  3 chars:[/dim]", f"[{KeySearcher.COLOR_POOR}]{KeySearcher.estimate_time(3, keys_per_sec)}[/{KeySearcher.COLOR_POOR}]  [dim]({fbl.get(3,0)}/{pc.get(3,0)})[/dim]",
                "[dim]  4 chars:[/dim]", f"[{KeySearcher.COLOR_POOR}]{KeySearcher.estimate_time(4, keys_per_sec)}[/{KeySearcher.COLOR_POOR}]  [dim]({fbl.get(4,0)}/{pc.get(4,0)})[/dim]"
            )
            content.add_row(
                "[dim]  5 chars:[/dim]", f"[{KeySearcher.COLOR_POOR}]{KeySearcher.estimate_time(5, keys_per_sec)}[/{KeySearcher.COLOR_POOR}]  [dim]({fbl.get(5,0)}/{pc.get(5,0)})[/dim]",
                "[dim]  6 chars:[/dim]", f"[{KeySearcher.COLOR_COMMON}]{KeySearcher.estimate_time(6, keys_per_sec)}[/{KeySearcher.COLOR_COMMON}]  [dim]({fbl.get(6,0)}/{pc.get(6,0)})[/dim]"
            )
            content.add_row(
                "[dim]  7 chars:[/dim]", f"[{KeySearcher.COLOR_UNCOMMON}]{KeySearcher.estimate_time(7, keys_per_sec)}[/{KeySearcher.COLOR_UNCOMMON}]  [dim]({fbl.get(7,0)}/{pc.get(7,0)})[/dim]",
                "[dim]  8 chars:[/dim]", f"[{KeySearcher.COLOR_RARE}]{KeySearcher.estimate_time(8, keys_per_sec)}[/{KeySearcher.COLOR_RARE}]  [dim]({fbl.get(8,0)}/{pc.get(8,0)})[/dim]"
            )
            content.add_row(
                "[dim]  9 chars:[/dim]", f"[{KeySearcher.COLOR_EPIC}]{KeySearcher.estimate_time(9, keys_per_sec)}[/{KeySearcher.COLOR_EPIC}]  [dim]({fbl.get(9,0)}/{pc.get(9,0)})[/dim]",
                "[dim]  10+ chars:[/dim]", f"[{KeySearcher.COLOR_ARTIFACT}]{KeySearcher.estimate_time(10, keys_per_sec)}[/{KeySearcher.COLOR_ARTIFACT}]  [dim]({fbl.get(10,0)}/{pc.get(10,0)})[/dim]"
            )
            
            # Build main panel
            main_panel = Panel(
                content,
                title="[bold bright_white on blue] 🔍 BreMesh MeshCore Ed25519 PubKey Prefix Searcher [/bold bright_white on blue]",
                subtitle="[dim white]Ctrl+C to stop • P to pause • R to resume • L to limit CPU[/dim white]",
                border_style="bright_blue",
                padding=(1, 2)
            )
            
            # Calculate ETA for next key based on remaining patterns
            # For regex patterns: use actual remaining possibilities
            # For plain patterns: use 16^length
            progress_panel = None  # Default: no progress panel
            if keys_per_sec > 0 and remaining_lengths:
                # Calculate combined probability using per-length distribution
                # For variable-length patterns, each length has different probability
                from collections import Counter
                len_counts = Counter(remaining_lengths)
                combined_prob = 0.0
                for length, count in len_counts.items():
                    # Probability per generated key for this length
                    prob_per_key = count / (16 ** length)
                    combined_prob += prob_per_key
                if combined_prob > 0:
                    expected_keys = 1.0 / combined_prob
                    expected_seconds = expected_keys / keys_per_sec
                    time_since_last = datetime.now().timestamp() - last_find_time
                    
                    # Session expected: how many keys should we have found by now?
                    session_elapsed = datetime.now().timestamp() - start_time
                    session_expected_keys = session_elapsed * keys_per_sec * combined_prob
                    
                    # Progress: time since last find / expected time per key
                    # Resets to 0 when a key is found, grows towards 100%
                    progress = (time_since_last / expected_seconds) if expected_seconds > 0 else 0
                    
                    # Bar is capped at 0-100%, but percentage display can go outside
                    bar_progress = max(0.0, min(1.0, progress))
                    
                    # Color changes based on progress
                    if progress < 0.5:
                        bar_color = "bright_cyan"
                    elif progress < 1.0:
                        bar_color = "bright_yellow"
                    else:
                        bar_color = "bright_green"  # Overdue - should find soon!
                    
                    eta_str = KeySearcher.format_time(expected_seconds)
                    elapsed_str = KeySearcher.format_time(time_since_last)
                    percent_str = f"{progress * 100:.0f}%"
                    
                    # Dynamic progress bar - use console width minus panel padding/border
                    terminal_width = console.size.width
                    bar_width = max(20, terminal_width - 8)  # -8 for panel borders and padding
                    filled = int(bar_progress * bar_width)  # Bar capped at 100%
                    
                    # Build progress bar with percentage in the middle
                    center_pos = bar_width // 2 - len(percent_str) // 2
                    bar_chars = []
                    for i in range(bar_width):
                        if i >= center_pos and i < center_pos + len(percent_str):
                            # Character from percent string
                            char_idx = i - center_pos
                            char = percent_str[char_idx]
                            if i < filled:
                                bar_chars.append(f"[bold black on {bar_color}]{char}[/bold black on {bar_color}]")
                            else:
                                bar_chars.append(f"[bold {bar_color}]{char}[/bold {bar_color}]")
                        else:
                            # Bar character
                            if i < filled:
                                bar_chars.append(f"[{bar_color}]█[/{bar_color}]")
                            else:
                                bar_chars.append("[dim]░[/dim]")
                    
                    progress_bar = "".join(bar_chars)
                    
                    # Build per-length ETA timers with rarity colors
                    from collections import Counter
                    len_counts = Counter(remaining_lengths)
                    eta_timers = []
                    # Collect counts for 11+ separately
                    count_11_plus = sum(c for l, c in len_counts.items() if l >= 11)
                    for length in sorted(len_counts.keys()):
                        if length > 10:
                            continue  # Skip individual lengths > 10, handled as 11+
                        count = len_counts[length]
                        if count > 0 and keys_per_sec > 0:
                            prob = count / (16 ** length)
                            eta_secs = 1.0 / (prob * keys_per_sec)
                            # Color based on length
                            if length >= 10:
                                color = KeySearcher.COLOR_ARTIFACT
                            elif length == 9:
                                color = KeySearcher.COLOR_EPIC
                            elif length == 8:
                                color = KeySearcher.COLOR_RARE
                            elif length == 7:
                                color = KeySearcher.COLOR_UNCOMMON
                            elif length == 6:
                                color = KeySearcher.COLOR_COMMON
                            else:
                                color = KeySearcher.COLOR_POOR
                            eta_timers.append(f"[dim]{length}:[/dim][{color}]{KeySearcher.format_time(eta_secs)}[/{color}]")
                    # Add 11+ in red if there are any patterns >= 11
                    if count_11_plus > 0 and keys_per_sec > 0:
                        prob_11 = count_11_plus / (16 ** 11)
                        eta_secs_11 = 1.0 / (prob_11 * keys_per_sec)
                        eta_timers.append(f"[dim]11+:[/dim][bold red]{KeySearcher.format_time(eta_secs_11)}[/bold red]")
                    eta_timers_str = "  ".join(eta_timers) if eta_timers else ""
                    
                    # Progress panel content with expected vs found keys
                    expected_found_str = f"[dim]Session:[/dim] [bold white]{last_found}[/bold white] [dim]/[/dim] [bold yellow]{session_expected_keys:.2f}[/bold yellow]"
                    progress_text = f"[bold bright_magenta]Next Key ETA:[/bold bright_magenta] [bold white]{eta_str}[/bold white]    [dim]Elapsed:[/dim] [dim white]{elapsed_str}[/dim white]    {expected_found_str}    {eta_timers_str}\n{progress_bar}"
                    
                    # Show formula only in verbose mode
                    if startup_info.get('verbose', False):
                        formula_parts = []
                        for length in sorted(len_counts.keys()):
                            count = len_counts[length]
                            formula_parts.append(f"{count}/16^{length}")
                        formula_str = f"[dim]ETA = 1 / (({' + '.join(formula_parts)}) × {KeySearcher.format_number(keys_per_sec)}) = {eta_str}[/dim]"
                        progress_text += f"\n{formula_str}"
                    
                    progress_panel = Panel(
                        progress_text,
                        border_style="bright_magenta",
                        padding=(0, 2)
                    )
                    
                    # Build found keys panel (third panel)
                    if found_keys_list:
                        found_panel = Panel(
                            KeySearcher.build_found_keys_table(found_keys_list),
                            title=f"[bold green]🔑 Found Keys ({len(found_keys_list)})[/bold green]",
                            border_style="green",
                            padding=(0, 2)
                        )
                        
                        return Group(main_panel, progress_panel, found_panel)
                    
                    return Group(main_panel, progress_panel)
            
            # No progress panel case (keys_per_sec == 0 or no remaining patterns)
            if found_keys_list:
                found_panel = Panel(
                    KeySearcher.build_found_keys_table(found_keys_list),
                    title=f"[bold green]🔑 Found Keys ({len(found_keys_list)})[/bold green]",
                    border_style="green",
                    padding=(0, 2)
                )
                
                return Group(main_panel, found_panel)
            
            return main_panel
        
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
                            
                            # Handle pattern hot-reload notification
                            if msg.get('patterns_reloaded'):
                                startup_info['num_patterns'] = msg['new_count']
                                # Add new patterns to remaining_lengths (assuming average length)
                                for _ in range(msg['added']):
                                    remaining_lengths.append(7)  # Default assumption for new patterns
                                live.update(build_panel())
                                continue
                            
                            last_total = msg.get('total', last_total)
                            last_found = msg.get('found', last_found)
                            
                            if 'new_key' in msg:
                                pattern = msg['new_key']['pattern']
                                public_key = msg['new_key']['public_key']
                                plen = msg['new_key'].get('effective_length', len(pattern))
                                found_keys_list.append((pattern, public_key, plen))
                                
                                # Update pattern metadata (track found keys for this pattern)
                                if pattern in pattern_metadata:
                                    pattern_metadata[pattern]['found_keys'].add(public_key)
                                
                                # Update found count by length (use effective_length if available)
                                if plen >= 10:
                                    found_by_len[10] += 1
                                else:
                                    # Track 1-9 individually
                                    found_by_len[plen] += 1
                                
                                # Remove pattern from remaining ONLY if it's a plain pattern <= unique_min
                                # For regex patterns: check if all possibilities are found
                                # For plain patterns > unique_min: can be found multiple times
                                is_regex = pattern in pattern_metadata and pattern_metadata[pattern]['possibilities'] > 1
                                if is_regex:
                                    # Check if all possibilities for this regex pattern are found
                                    remaining_for_pattern = pattern_metadata[pattern]['possibilities'] - len(pattern_metadata[pattern]['found_keys'])
                                    if remaining_for_pattern == 0 and plen in remaining_lengths:
                                        # All possibilities found, remove from remaining
                                        remaining_lengths.remove(plen)
                                else:
                                    # Plain pattern: remove if <= unique_min
                                    if plen <= startup_info['unique_min'] and plen in remaining_lengths:
                                        remaining_lengths.remove(plen)
                                
                                # Reset last_find_time to now (for Elapsed timer)
                                last_find_time = datetime.now().timestamp()
                            
                            live.update(build_panel())
                    
                    except Exception:
                        # Timeout - auto refresh
                        live.update(build_panel())
        
        except KeyboardInterrupt:
            pass
    
    def generate_and_check_key(self, worker_id: int, shared_counter, shared_found,
                                found_patterns_dict, session_found_list, shared_patterns, shared_regex_patterns, start_time,
                                display_queue, pause_event, stop_event, worker_pause_event, single_pattern_mode) -> None:
        """Worker process for key generation"""
        local_checked = 0
        local_patterns_cache = set(shared_patterns.keys())  # Local cache for performance
        local_regex_cache = {}  # Compile regex patterns locally
        for regex_pattern_str in shared_regex_patterns.keys():
            try:
                local_regex_cache[regex_pattern_str] = re.compile(regex_pattern_str, re.IGNORECASE)
            except re.error:
                pass  # Skip invalid patterns
        last_cache_update = 0
        
        try:
            while not stop_event.is_set():
                # Main wait for pause/resume
                pause_event.wait()
                # Worker-specific pause (for CPU limiting)
                worker_pause_event.wait()
                
                if stop_event.is_set():
                    break
                
                # Refresh pattern cache every 10000 keys
                local_checked_total = local_checked
                if local_checked_total - last_cache_update >= 10000:
                    local_patterns_cache = set(shared_patterns.keys())
                    # Also update regex cache for hot-reloaded regex patterns
                    for regex_pattern_str in shared_regex_patterns.keys():
                        if regex_pattern_str not in local_regex_cache:
                            try:
                                local_regex_cache[regex_pattern_str] = re.compile(regex_pattern_str, re.IGNORECASE)
                            except re.error:
                                pass  # Skip invalid patterns
                    last_cache_update = local_checked_total
                
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
                
                for pattern in local_patterns_cache:
                    # Check if pattern matches (either plain string or regex)
                    matches = False
                    if pattern in local_regex_cache:
                        # Regex pattern
                        matches = local_regex_cache[pattern].match(public_hex) is not None
                    else:
                        # Plain string pattern
                        matches = public_hex.startswith(pattern)
                    
                    if matches:
                        # Calculate effective length for unique_min check
                        _, _, effective_length = self.validate_pattern(pattern)
                        
                        # Extract actual matched prefix for duplicate tracking
                        # For regex patterns, get the actual match length
                        if pattern in local_regex_cache:
                            match_obj = local_regex_cache[pattern].match(public_hex)
                            matched_prefix = match_obj.group(0) if match_obj else public_hex[:effective_length]
                        else:
                            matched_prefix = public_hex[:effective_length]
                        
                        # Check unique_min for both plain and regex patterns
                        if not single_pattern_mode and len(matched_prefix) <= self.unique_min:
                            # Use the actual matched prefix as key, not the pattern
                            if matched_prefix in found_patterns_dict:
                                continue
                            found_patterns_dict[matched_prefix] = True
                            session_found_list.append(matched_prefix)
                        
                        self.save_key(private_bytes, public_bytes, public_hex, pattern)
                        
                        with shared_found.get_lock():
                            shared_found.value += 1
                        
                        # All workers send new_key message
                        display_queue.put({
                            'total': shared_counter.value,
                            'found': shared_found.value,
                            'new_key': {
                                'pattern': pattern,
                                'public_key': public_hex,
                                'private_key': private_bytes.hex().upper(),
                                'effective_length': effective_length
                            }
                        })
                        
                        # Check if regex pattern is complete (all possibilities found)
                        if pattern in self.pattern_metadata:
                            total_possible = self.pattern_metadata[pattern]['possibilities']
                            if shared_found.value >= total_possible:
                                # All keys found for this regex pattern
                                stop_event.set()
                        
                        # In single pattern mode (non-regex), signal all workers to stop
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
    
    def sort_regex_file(self, pattern: str) -> None:
        """Sort the _all.txt file for regex patterns alphabetically by matched prefix"""
        safe_pattern = re.sub(r'[^\w]', '_', pattern)
        filepath = self.output_dir / f"{safe_pattern}_all.txt"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into header and entries
            parts = content.split("="*70 + "\n\n", 1)
            if len(parts) != 2:
                return  # Invalid format
            
            header = parts[0] + "="*70 + "\n\n"
            entries_text = parts[1]
            
            # Split entries by separator
            entries = entries_text.split("-"*70 + "\n\n")
            entries = [e.strip() for e in entries if e.strip()]
            
            # Sort by the "Match:" line (first line of each entry)
            def get_match_prefix(entry):
                for line in entry.split('\n'):
                    if line.startswith("Match: "):
                        return line.split("Match: ")[1].split("...")[0]
                return ""
            
            entries.sort(key=get_match_prefix)
            
            # Rebuild file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header)
                for entry in entries:
                    f.write(entry + "\n")
                    f.write("-"*70 + "\n\n")
        except Exception:
            pass  # Silently fail if sorting doesn't work
    
    def save_key(self, private_bytes: bytes, public_bytes: bytes, public_hex: str, pattern: str) -> None:
        """Save found key to file"""
        # Sanitize pattern for filename (replace regex chars with underscores)
        safe_pattern = re.sub(r'[^\w]', '_', pattern)
        
        # Check if this is a regex pattern
        is_regex = self.is_regex_pattern(pattern)
        possibilities = self.calculate_regex_possibilities(pattern) if is_regex else 1
        
        if is_regex and possibilities > 1:
            # For regex patterns: one file with all found keys
            filepath = self.output_dir / f"{safe_pattern}_all.txt"
            
            # Standard Ed25519 format (128 chars)
            private_hex_standard = private_bytes.hex().upper()
            # MeshCore format (192 chars: private + public)
            private_hex_meshcore = (private_bytes + public_bytes).hex().upper()
            
            # Extract the actual matched prefix for display
            _, _, effective_len = self.validate_pattern(pattern)
            matched_prefix = public_hex[:effective_len]
            
            # Append to file (create if doesn't exist)
            mode = 'a' if filepath.exists() else 'w'
            with open(filepath, mode, encoding='utf-8') as f:
                if mode == 'w':
                    # Header for new file
                    f.write(f"Regex Pattern: {pattern}\n")
                    f.write(f"Effective Length: {effective_len} chars\n")
                    f.write(f"Total Possibilities: {possibilities}\n")
                    f.write(f"="*70 + "\n\n")
                
                # Add entry
                f.write(f"Match: {matched_prefix}...\n")
                f.write(f"Public Key:  {public_hex}\n")
                f.write(f"Private Key: {private_hex_standard}\n")
                f.write(f"MeshCore:    {private_hex_meshcore}\n")
                f.write("-"*70 + "\n\n")
        else:
            # For plain patterns: separate files with counter
            counter = 1
            filepath = self.output_dir / f"{safe_pattern}_{counter}.txt"
            while filepath.exists():
                counter += 1
                filepath = self.output_dir / f"{safe_pattern}_{counter}.txt"
            
            # Standard Ed25519 format (128 chars)
            private_hex_standard = private_bytes.hex().upper()
            # MeshCore format (192 chars: private + public)
            private_hex_meshcore = (private_bytes + public_bytes).hex().upper()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Pattern Match: {pattern}\n")
                f.write(f"Public Key (HEX): {public_hex}\n\n")
                f.write(f"# Standard Ed25519 Format (128 characters)\n")
                f.write(f"# This is the pure private key as generated by the Ed25519 algorithm\n")
                f.write(f"Private Key (Standard): {private_hex_standard}\n\n")
                f.write(f"# MeshCore Format (192 characters)\n")
            f.write(f"# This format concatenates the private key (128 chars) with the public\n")
            f.write(f"# key (64 chars) for convenience. Use this format for MeshCore devices.\n")
            f.write(f"Private Key (MeshCore): {private_hex_meshcore}\n")
            f.write(f"\n{'='*70}\n")
            f.write(f"MeshCore Import Format:\n")
            f.write(f"{'='*70}\n\n")
            f.write('{\n')
            f.write(f'  "public_key": "{public_hex}",\n')
            f.write(f'  "private_key": "{private_hex_meshcore}"\n')
            f.write('}\n')
            f.write(f"\n{'='*70}\n")
            f.write(f"Repeater Configuration Instructions\n")
            f.write(f"{'='*70}\n\n")
            f.write("METHOD 1: Repeater + Computer (USB Serial)\n")
            f.write("-" * 70 + "\n")
            f.write("If you can connect your repeater directly to a computer, this is the\n")
            f.write("fastest method:\n\n")
            f.write("1. Connect via USB Serial\n")
            f.write("   Connect your repeater device to your computer via USB serial connection.\n\n")
            f.write("2. Access the Console\n")
            f.write("   Open the MeshCore Web Console or use any terminal application to\n")
            f.write("   connect to your device.\n\n")
            f.write("   Tip: The web console at flasher.meshcore.co.uk provides an easy\n")
            f.write("   interface with repeater configuration command reference.\n\n")
            f.write("3. Set the Private Key\n")
            f.write("   Run the following command in the console:\n\n")
            f.write(f"   set prv.key {private_hex_meshcore}\n\n")
            f.write("   Important: Make sure to use the complete 192-character MeshCore format\n")
            f.write("   private key. The command will change the device's private key immediately.\n\n")
            f.write("4. Verify the Change\n")
            f.write("   You can verify the key change by checking the device's public key\n")
            f.write("   display in settings.\n\n")
            f.write("Why use the Serial Console?\n")
            f.write("  - No need to flash companion firmware\n")
            f.write("  - Change the key on the spot without switching firmware\n")
            f.write("  - Quick if you're comfortable using a console\n")
            f.write("  - Works with MeshCore web console or any terminal app\n\n")
            f.write(f"{'='*70}\n")
            f.write("Troubleshooting\n")
            f.write(f"{'='*70}\n\n")
            f.write("Common Issues:\n")
            f.write("  - Key not appearing: Make sure you tapped the checkmark to save changes\n")
            f.write("  - Wrong key format: Ensure you're copying the entire 128-character\n")
            f.write("    private key\n")
            f.write("  - App not detecting device: Try disconnecting and reconnecting the USB\n")
            f.write("    cable\n")
            f.write("  - Firmware flash fails: Try a different USB cable or USB port\n")
            f.write("  - Key import fails: Verify the key was generated correctly and try again\n\n")
            f.write("Verification Steps:\n")
            f.write("  - Check that the public key displayed matches your generated key\n")
            f.write(f"  - Verify the first characters match your desired prefix: {pattern}\n")
            f.write("  - Test the connection to ensure the device is working properly\n")
            f.write("  - Check the MeshCore network to see your device with the new identifier\n\n")
            f.write("Pro Tip: Keep a backup of your private key in a secure location. You'll\n")
            f.write("need it if you ever need to restore your device configuration.\n")
    
    def load_existing_regex_keys(self, pattern: str) -> Set[str]:
        """Load already found keys from _all.txt file for a regex pattern"""
        found_keys = set()
        safe_pattern = re.sub(r'[^\w]', '_', pattern)
        filepath = self.output_dir / f"{safe_pattern}_all.txt"
        
        if not filepath.exists():
            return found_keys
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("Public Key:"):
                        # Extract public key
                        public_key = line.split("Public Key:")[1].strip()
                        found_keys.add(public_key)
        except Exception:
            pass  # Silently ignore errors
        
        return found_keys
    
    def load_existing_patterns(self) -> Set[str]:
        """Load already found patterns"""
        existing = set()
        if not self.output_dir.exists():
            return existing
        
        for file in self.output_dir.glob("*.txt"):
            # File format: pattern_1.txt, pattern_2.txt, etc.
            stem = file.stem
            # Remove counter suffix (_1, _2, etc.)
            if '_' in stem:
                parts = stem.rsplit('_', 1)
                if parts[1].isdigit():
                    stem = parts[0]
            existing.add(stem)
        return existing
    
    def get_pattern_length_distribution(self, pattern: str) -> dict:
        """Get distribution of possibilities across length categories for a pattern.
        Returns dict with length as key and possibility count as value."""
        _, _, min_length = self.validate_pattern(pattern)
        
        # Check if pattern has variable length quantifiers
        range_match = re.search(r'\{(\d+),(\d+)\}', pattern)
        if range_match:
            min_repeat = int(range_match.group(1))
            max_repeat = int(range_match.group(2))
            
            # For variable-length patterns, we need to calculate possibilities for EACH length
            # Example: DEADBEE{1,57}F has 1 possibility per length (8 through 64)
            # The pattern represents different lengths, each with 1 possibility
            
            distribution = {}
            for repeat in range(min_repeat, max_repeat + 1):
                length = min_length + (repeat - min_repeat)
                if length >= 10:
                    distribution[10] = distribution.get(10, 0) + 1
                else:
                    distribution[length] = distribution.get(length, 0) + 1
            return distribution
        else:
            # Fixed length pattern - calculate actual possibilities
            possibilities = self.calculate_regex_possibilities(pattern) if self.is_regex_pattern(pattern) else 1
            if min_length >= 10:
                return {10: possibilities}
            else:
                return {min_length: possibilities}
    
    def run(self, num_workers: int = 0) -> None:
        """Start the key search"""
        # 0 means all cores, otherwise use specified number (capped at available cores)
        max_workers = mp.cpu_count()
        if num_workers == 0:
            num_workers = max_workers
        else:
            num_workers = min(num_workers, max_workers)
        
        existing_patterns = self.load_existing_patterns()
        console = Console()
        
        # Count patterns by length category
        # For regex patterns with variable length, distribute across categories
        pattern_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}  # 10 = 10+
        for p in self.patterns:
            distribution = self.get_pattern_length_distribution(p)
            for length, count in distribution.items():
                pattern_counts[length] += count
        
        # Count already found (existing) patterns by length
        # For regex patterns: count actual found keys from pattern_metadata
        # For plain patterns: count from existing_patterns files
        existing_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        
        for p in self.patterns:
            _, _, plen = self.validate_pattern(p)
            # Check if this is a regex pattern with loaded keys
            if p in self.pattern_metadata and len(self.pattern_metadata[p]['found_keys']) > 0:
                # Regex pattern: count actual found keys
                found_count = len(self.pattern_metadata[p]['found_keys'])
                # For variable-length patterns, distribute found keys across lengths
                if self.is_regex_pattern(p):
                    distribution = self.get_pattern_length_distribution(p)
                    for length, count in distribution.items():
                        if length >= 10:
                            existing_counts[10] += found_count
                        else:
                            existing_counts[length] += found_count
                else:
                    if plen >= 10:
                        existing_counts[10] += found_count
                    else:
                        existing_counts[plen] += found_count
            else:
                # Plain pattern: check if in existing_patterns
                patterns_upper = {p.upper() for p in self.patterns}
                if p.upper() in {ep.upper() for ep in existing_patterns}:
                    if plen >= 10:
                        existing_counts[10] += 1
                    else:
                        existing_counts[plen] += 1
        
        # Build list of remaining pattern lengths (excluding already found)
        # Patterns > unique_min are ALWAYS included (can be found multiple times)
        # In single pattern mode, ALWAYS include the pattern for ETA display
        remaining_pattern_lengths = []
        existing_upper = {ep.upper() for ep in existing_patterns}
        for p in self.patterns:
            # For regex patterns, use length distribution
            if self.is_regex_pattern(p):
                _, _, plen = self.validate_pattern(p)
                # Include if: single pattern mode OR not found yet OR pattern is longer than unique_min (repeatable)
                if self.single_pattern_mode or p.upper() not in existing_upper or plen > self.unique_min:
                    # Add all lengths from the distribution with their possibility counts
                    distribution = self.get_pattern_length_distribution(p)
                    for length, count in distribution.items():
                        remaining_pattern_lengths.extend([length] * count)
            else:
                plen = len(p)
                # Include if: single pattern mode OR not found yet OR pattern is longer than unique_min (repeatable)
                if self.single_pattern_mode or p.upper() not in existing_upper or plen > self.unique_min:
                    remaining_pattern_lengths.append(plen)
        
        # Prepare startup info for display process
        startup_info = {
            'num_patterns': len(self.patterns),
            'unique_min': self.unique_min,
            'output_dir': str(self.output_dir.absolute()),
            'num_existing': len(existing_patterns),
            'existing_patterns': ', '.join(sorted(existing_patterns)) if existing_patterns else '',
            'pattern_counts': pattern_counts,
            'existing_counts': existing_counts,
            'remaining_pattern_lengths': remaining_pattern_lengths,
            'verbose': self.verbose,
            'pattern_metadata': {p: self.pattern_metadata[p] for p in self.patterns}  # Include pattern metadata for ETA
        }
        
        # Shared state
        shared_counter = mp.Value('i', 0)
        shared_found = mp.Value('i', 0)
        manager = mp.Manager()
        found_patterns_dict = manager.dict()
        session_found_list = manager.list()
        shared_patterns = manager.dict()  # Shared patterns for hot-reload
        shared_regex_patterns = manager.dict({p: p for p in self.patterns if self.is_regex_pattern(p)})
        shared_pattern_metadata = manager.dict(self.pattern_metadata)  # Share metadata with workers
        display_queue = manager.Queue()
        pause_event = mp.Event()
        pause_event.set()
        stop_event = mp.Event()  # For single pattern mode auto-exit
        cpu_limit_event = mp.Event()  # CPU limit toggle (default: off)
        
        # Create individual pause events for each worker
        worker_pause_events = [mp.Event() for _ in range(num_workers)]
        for event in worker_pause_events:
            event.set()  # All workers start running
        
        # Initialize shared patterns
        for pattern in self.patterns:
            shared_patterns[pattern.upper()] = True
        
        for pattern in existing_patterns:
            found_patterns_dict[pattern] = True
        
        start_time = datetime.now().timestamp()
        
        # Pattern hot-reload thread (reload every 30 seconds)
        def pattern_reload_thread():
            if self.single_pattern_mode:
                return  # No reload in single pattern mode
            last_count = len(self.patterns)
            while not stop_event.is_set():
                time.sleep(30)  # Check every 30 seconds
                if stop_event.is_set():
                    break
                try:
                    new_patterns = self.load_patterns(self.patterns_file)
                    added = 0
                    for p in new_patterns:
                        # For plain patterns: use uppercase key
                        # For regex patterns: use original pattern
                        p_key = p.upper() if not self.is_regex_pattern(p) else p
                        if p_key not in shared_patterns:
                            shared_patterns[p_key] = True
                            # If regex, also add to shared_regex_patterns
                            if self.is_regex_pattern(p):
                                shared_regex_patterns[p] = p
                            added += 1
                    if added > 0:
                        display_queue.put({
                            'patterns_reloaded': True,
                            'new_count': len(shared_patterns),
                            'added': added
                        })
                except Exception:
                    pass  # Ignore reload errors
        
        reload_thread = threading.Thread(target=pattern_reload_thread, daemon=True)
        reload_thread.start()
        
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
                        elif key == 'L':
                            if cpu_limit_event.is_set():
                                cpu_limit_event.clear()
                                # Resume all workers
                                for event in worker_pause_events:
                                    event.set()
                            else:
                                cpu_limit_event.set()
                                # Pause 25% of workers (min 1)
                                workers_to_pause = max(1, int(num_workers * 0.25))
                                for i in range(workers_to_pause):
                                    worker_pause_events[i].clear()
                            display_queue.put({'force_update': True})
                    time.sleep(0.1)
            except Exception:
                pass
        
        kb_thread = threading.Thread(target=keyboard_listener, daemon=True)
        kb_thread.start()
        
        # Simple console mode - wait for key(s) without display process
        if self.simple_console and (self.single_pattern_mode or self.is_regex_search):
            # Start workers
            processes = []
            found_keys = []
            
            try:
                for i in range(num_workers):
                    p = mp.Process(
                        target=self.generate_and_check_key,
                        args=(i, shared_counter, shared_found, found_patterns_dict,
                              session_found_list, shared_patterns, shared_regex_patterns, start_time, display_queue, pause_event,
                              stop_event, worker_pause_events[i], self.single_pattern_mode)
                    )
                    p.start()
                    processes.append(p)
                
                # Wait for key(s) to be found
                while not stop_event.is_set():
                    try:
                        msg = display_queue.get(timeout=0.5)
                        if isinstance(msg, dict) and 'new_key' in msg:
                            found_keys.append(msg['new_key'])
                            
                            # Output private key immediately
                            private_key = msg['new_key']['private_key']
                            if self.simple_console_long:
                                # Long format: MeshCore 192 chars (private + public)
                                public_key = msg['new_key']['public_key']
                                print(private_key + public_key)
                            else:
                                # Short format: Standard Ed25519 128 chars (private only)
                                print(private_key)
                            
                            # Exit only for single_pattern_mode (not regex)
                            if self.single_pattern_mode:
                                break
                    except:
                        pass
                
                # Terminate workers
                for p in processes:
                    p.terminate()
                    p.join()
                
                self.save_total_stats(shared_counter.value)
                return
                
            except KeyboardInterrupt:
                for p in processes:
                    p.terminate()
                    p.join()
                self.save_total_stats(shared_counter.value)
                return
        
        # Start display process (normal Rich UI mode)
        display_proc = mp.Process(
            target=self.display_process,
            args=(display_queue, self.total_all_time, start_time, num_workers, pause_event, cpu_limit_event, startup_info)
        )
        display_proc.start()
        
        # Start workers
        processes = []
        try:
            for i in range(num_workers):
                p = mp.Process(
                    target=self.generate_and_check_key,
                    args=(i, shared_counter, shared_found, found_patterns_dict,
                          session_found_list, shared_patterns, shared_regex_patterns, start_time, display_queue, pause_event,
                          stop_event, worker_pause_events[i], self.single_pattern_mode)
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
                
                # Sort regex pattern files if they exist
                for pattern in self.patterns:
                    if self.is_regex_pattern(pattern):
                        self.sort_regex_file(pattern)
                
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
            
            # Sort regex pattern files before showing summary
            for pattern in self.patterns:
                if self.is_regex_pattern(pattern):
                    self.sort_regex_file(pattern)
            
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
                title="[bold bright_white]Search Stopped[/bold bright_white]",
                border_style="bright_blue",
                padding=(1, 2)
            ))
            console.print("\n")


def main():
    parser = argparse.ArgumentParser(description='Ed25519 Public Key Pattern Searcher for MeshCore')
    parser.add_argument('pattern', nargs='?', type=str, help='Pattern to search for (e.g., CAFE, DEAD, BEEF)')
    parser.add_argument('-u', '--unique-min', type=int, default=int(os.getenv('UNIQUE_MIN', str(DEFAULT_UNIQUE_MIN))), 
                        help=f'Patterns with length <= this value are kept unique (default: {DEFAULT_UNIQUE_MIN})')
    parser.add_argument('-w', '--workers', type=int, default=0,
                        help='Number of worker processes (0 = all available cores, default: 0)')
    parser.add_argument('-f', '--patterns-file', type=str, default=os.getenv('PATTERNS_FILE', 'searchFor.txt'),
                        help='Path to pattern file (default: searchFor.txt)')
    parser.add_argument('--output-dir', type=str, default='found_keys',
                        help='Output directory for found keys (default: found_keys)')
    parser.add_argument('-p', '--pattern-flag', type=str, dest='pattern_flag', help='Alternative way to specify pattern')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed ETA calculation formula')
    parser.add_argument('-osc', '--output-simple-console', action='store_true', dest='simple_console',
                        help='Simple console output (single pattern mode only): prints only the private key (128 chars)')
    parser.add_argument('-oscl', '--output-simple-console-long', action='store_true', dest='simple_console_long',
                        help='Simple console output (single pattern mode only): prints private+public key (192 chars)')
    
    args = parser.parse_args()
    
    # Priority: positional pattern > -p flag > None (use patterns file)
    single_pattern = args.pattern or args.pattern_flag
    
    searcher = KeySearcher(
        patterns_file=args.patterns_file,
        output_dir=args.output_dir,
        unique_min=args.unique_min,
        single_pattern=single_pattern,
        verbose=args.verbose,
        simple_console=args.simple_console,
        simple_console_long=args.simple_console_long
    )
    searcher.run(num_workers=args.workers)


if __name__ == "__main__":
    main()
