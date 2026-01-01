# BreMesh MeshCore Ed25519 PubKey Prefix Searcher

A high-performance Python script for generating Ed25519 key pairs with custom public key prefixes.

Perfect for memorable keys for **MeshCore** repeaters!

## Recommendation for Simple Keys

**For simple, single keys I recommend:** [https://gessaman.com/mc-keygen/](https://gessaman.com/mc-keygen/)

This website is perfect for quick, straightforward key generation and I highly recommend it. In fact, this site was my inspiration for this tool - I wanted to create a way to **search for multiple complex keys simultaneously**, to save resources and time when configuring multiple repeaters with custom patterns.

**GitHub:** [https://github.com/agessaman/meshcore-web-keygen](https://github.com/agessaman/meshcore-web-keygen)

**Use this tool when:**

- You want to search for multiple keys with different patterns simultaneously
- You need more complex/longer patterns (7+ characters)
- You have a pattern list and want to generate all keys in one run
- You want to utilize the full CPU power of your system

![Interface](interface.png)

## Features

### Performance

- **Multi-Core Processing** - Uses all available CPU cores for maximum speed
- **Optimized Key Generation** - Ed25519 Elliptic Curve Cryptography
- **HEX Format** - MeshCore-compatible format (64-character HEX Public Key)

### User Interface

- **Rich Live Display** - Flicker-free terminal UI using the `rich` framework
- **Alternate Screen Buffer** - Professional full-screen display like `htop`
- **Three-Panel Layout** - Main statistics, ETA progress bar, found keys
- **Color-Coded Display** - Clear presentation of all statistics
- **CPU Usage Display** - Graphical progress indicator with color coding
- **Rarity Indicators** - Color marking based on pattern length
- **Progress Display** - Shows found/searched patterns per length category

### Control

- **Pause/Resume** - Pause with `P`, resume with `R`
- **CPU Limiting** - Limit CPU to ~75% with `L` (pauses 25% of workers)
- **Graceful Shutdown** - Clean exit with `Ctrl+C` and summary
- **Keyboard Listener** - Responds to input during search
- **Single Pattern Mode** - Search for single pattern with auto-exit on find

### Statistics

- **Live Statistics** - Real-time display of progress and speed
- **Session Stats** - Current session: Keys checked, matches found, runtime
- **All-Time Stats** - Total keys checked across all sessions (persistent)
- **Time Estimates** - Calculated probabilities with progress (found/searched)
- **Remaining Counter** - Shows remaining patterns total and per category
- **Next Key ETA** - Mathematical estimate until next find with dynamic progress bar
- **Per-Length ETAs** - Individual ETA timers per pattern length (5-10, 11+ in red)
- **Session Progress** - Shows found vs. expected keys (e.g., `1 / 1.4`)
- **Verbose Mode** - Shows ETA calculation formula with `-v` flag

### Management

- **Pattern File** - External pattern list for easy customization
- **Hot-Reload** - Pattern file reloaded every 30 seconds (new patterns automatically added)
- **Duplicate Detection** - Prevents duplicate finds for short patterns (configurable via `--max-pattern-length`)
- **No Dup Cap** - Patterns above max-pattern-length can be found any number of times
- **Persistent Storage** - Found keys saved immediately
- **JSON Export** - MeshCore-compatible import format

## Installation

### Prerequisites

- Python 3.7+
- pip

### Install Dependencies

```bash
pip install cryptography rich psutil
```

## Usage

### Quick Start

```bash
python key_searcher.py
```

### Search for Single Pattern (with Auto-Exit)

```bash
python key_searcher.py --pattern CAFE
# or short:
python key_searcher.py -p BREMESH
```

The script automatically exits once the pattern is found.

### With Custom Pattern File

```bash
python key_searcher.py -f my_patterns.txt
# or:
python key_searcher.py --patterns-file my_patterns.txt
```

### With ETA Formula (Verbose Mode)

```bash
python key_searcher.py -v
```

### All Options

```bash
python key_searcher.py -f searchFor.txt --max-pattern-length 7 --output-dir found_keys -v
```

## Configuration

### Command Line Arguments

| Argument                    | Description                            | Default          |
| --------------------------- | -------------------------------------- | ---------------- |
| `--pattern`, `-p`       | Search for single pattern (auto-exit)  | -                |
| `--patterns-file`, `-f` | Path to pattern file                   | `searchFor.txt` |
| `--max-pattern-length`    | Max length for duplicate detection     | `7`            |
| `--output-dir`            | Output directory for found keys        | `found_keys`   |
| `--verbose`, `-v`       | Show ETA calculation formula           | -                |

### Environment Variables

Alternatively configurable via environment variables:

**Windows PowerShell:**

```powershell
$env:PATTERNS_FILE = "custom_patterns.txt"
$env:MAX_PATTERN_LENGTH = 8
python key_searcher.py
```

**Linux/Mac:**

```bash
export PATTERNS_FILE=custom_patterns.txt
export MAX_PATTERN_LENGTH=8
python key_searcher.py
```

### Create Pattern File

Create a text file with one pattern per line:

```
CAFE
DEAD
BEEF
1234
ABCD
BREMESH
```

**Notes:**

- Only HEX characters allowed: `0-9` and `A-F`
- Case insensitive
- Lines starting with `#` are comments
- Empty lines are ignored

## Operation

### During Search

| Key        | Action                                    |
| ---------- | ----------------------------------------- |
| `P`      | Pause search                              |
| `R`      | Resume search                             |
| `L`      | Limit CPU (~75%, pauses 25% of workers)   |
| `Ctrl+C` | Stop search                               |

### Display Elements

The interface consists of three separate panels:

1. **Main Statistics (blue frame)** - Config, Patterns, No Dup Cap, Status, Session/All-Time Stats, Time Estimates
2. **ETA Progress Bar (magenta frame)** - Expected/Elapsed time, Session Progress, Per-Length ETAs, progress bar
3. **Found Keys (green frame)** - Found keys with complete 64-character Public Key

![Interface](interface.png)

**Legend:**

- **No Dup Cap:** Shows from which pattern length multiple finds are allowed
- **Workers:** Shows number of active workers, with CPU limit: `4 (Limit: 3)`
- **Status:** Shows RUNNING/PAUSED, with CPU limit additionally: `(CPU ~75%)`
- **Time Estimates:** `Time estimate (found/searched)` per length category
- **Session:** Shows `found / expected` keys in current session
- **Per-Length ETAs:** Individual ETA timers for each pattern length in rarity colors:
  - Gray: 5 characters or less
  - White: 6 characters
  - Green: 7 characters
  - Blue: 8 characters
  - Purple: 9 characters
  - Orange: 10 characters
  - Red: 11+ characters
- **Next Key ETA:** Mathematically expected time until next find based on combined probability:
  ```
  ETA = 1 / ((n1/16^L1 + n2/16^L2 + ...) x keys_per_sec)
  ```
- **Progress Bar:** Shows elapsed time relative to expected time
  - Cyan (<50%): in progress
  - Yellow (50-100%): expected soon
  - Green (>100%): overdue - find should come soon

## Output Format

Found keys are saved in the `found_keys/` directory:

### Filename

```
{pattern}_1.txt
{pattern}_2.txt  (for duplicates of patterns >7 characters)
```

Example: `CAFE_1.txt`, `BREMESH_1.txt`, `BREMESH_2.txt`

### File Content

```
Pattern Match: CAFE
Public Key (HEX): CAFE1234567890ABCDEF...
Private Key (HEX): ABCDEF1234567890...

======================================================================
MeshCore Import Format:
======================================================================

{
  "public_key": "CAFE1234567890ABCDEF...",
  "private_key": "ABCDEF1234567890..."
}
```

The generated key files additionally contain detailed configuration instructions for your repeater.

## Configuring Keys on the Repeater

After successfully generating a key with your desired pattern, you need to configure it on your MeshCore repeater.

### Method: USB Serial Console (Recommended)

This is the fastest method when you can directly connect your repeater to a computer:

#### Step 1: Establish USB Connection

Connect your repeater to your computer via USB.

#### Step 2: Open Console

Open the MeshCore Web Console or use any terminal application:

- **Web Console**: Visit [flasher.meshcore.co.uk](https://flasher.meshcore.co.uk)
- **Terminal**: Use PuTTY, screen, or another serial terminal program

#### Step 3: Set Private Key

Execute the following command in the console:

```
set prv.key <YOUR_128_CHARACTER_PRIVATE_KEY>
```

Replace `<YOUR_128_CHARACTER_PRIVATE_KEY>` with the complete 128-character Private Key from your generated key file.

**Important:** Use the complete 128-character Private Key. The command changes the device's Private Key immediately.

#### Step 4: Verify Change

Verify the change by checking the Public Key in the device settings:

- The first characters should match your desired pattern
- The complete Public Key should match the generated key

### Advantages of Serial Console Method

- No companion firmware required
- Change occurs immediately without firmware switch
- Fast and straightforward with console experience
- Works with MeshCore Web Console or any terminal program

### Troubleshooting

**Common Issues:**

- **Key not displayed**: Make sure you saved the change
- **Incorrect key format**: Use the complete 128-character Private Key
- **App doesn't detect device**: Disconnect and reconnect USB cable
- **Firmware flash fails**: Try different USB cable or USB port
- **Key import fails**: Verify key generation and try again

**Verification Steps:**

1. Check that the displayed Public Key matches your generated key
2. Verify that the first characters match your desired pattern
3. Test the connection to ensure the device works
4. Check in the MeshCore network if your device is visible with the new identifier

**Pro Tip:** Keep a backup copy of your Private Key in a secure location. You'll need it if you have to restore your device configuration.

## Time Estimates

The probability of finding a specific prefix:

| Prefix Length | Possibilities     | At 30k keys/s |
| ------------- | ----------------- | ------------- |
| 4 characters  | 65,536            | ~2 seconds    |
| 5 characters  | 1,048,576         | ~35 seconds   |
| 6 characters  | 16,777,216        | ~9 minutes    |
| 7 characters  | 268,435,456       | ~2.5 hours    |
| 8 characters  | 4,294,967,296     | ~1.7 days     |
| 9 characters  | 68,719,476,736    | ~26 days      |
| 10 characters | 1,099,511,627,776 | ~1.2 years    |

## Technical Details

### Architecture

- **Multiprocessing** - One worker process per CPU core
- **Worker Management** - CPU limiting through selective pausing of workers
- **Shared Memory** - Shared counters for all workers
- **Queue-Based Communication** - Worker to display process
- **Event-Based Control** - Synchronized pause and CPU limiting across all workers

### Files

- `key_searcher.py` - Main script
- `searchFor.txt` - Default pattern file
- `.total_stats.json` - Persistent all-time statistics
- `found_keys/` - Output directory

### Dependencies

- `cryptography` - Ed25519 key generation
- `rich` - Terminal UI framework
- `psutil` - CPU usage monitoring

## License

MIT License

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

Good luck finding the perfect key!
