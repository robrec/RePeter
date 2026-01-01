# Ed25519 Public Key Pattern Searcher

A Python script for **MeshCore** that uses all available CPU cores to search for ed25519 Public Keys with special patterns at the beginning. The goal is to generate unique and easily recognizable keys for repeaters to avoid confusion.

## Features

- Multi-core processing for maximum performance
- Search for custom patterns at the beginning of the Public Key (Base58)
- Automatic saving of found key pairs
- Duplicate prevention: Patterns up to 7 characters are saved only once (configurable)
- Live statistics during search with session tracking
- Epoch timestamp for chronological sorting
- 🐳 **Docker support**: Easy containerization for portable deployment

## Installation

### Option 1: Docker (recommended)

**Advantages:**

- ✅ No local Python installation required
- ✅ Isolated environment
- ✅ Portable on any system (Windows, Linux, macOS)
- ✅ Easy deployment on servers
- ✅ Automatic dependency management

**Requirements:**

- Docker & Docker Compose installed

**Quick Start:**

```bash
docker-compose up
```

📖 **Complete Docker documentation:** [DOCKER.md](DOCKER.md)

### Option 2: Python (local)

**Requirements:**

- Python 3.7 or higher
- pip (Python Package Manager)

**Install dependencies:**

```bash
pip install cryptography base58
```

## Usage

### 1. Define Patterns

Edit the file `searchFor.txt` and add the desired patterns (one pattern per line).

Example:

```
AAAAAA
DEADBEEF
123456
CAFE
D0000000
```

The included list already contains many interesting patterns!

### 2. Start Script

**Python (direct):**

```bash
python key_searcher.py
```

**With options:**

```bash
# Set duplicate limit to 10 characters
python key_searcher.py --max-pattern-length 10

# Use different pattern file
python key_searcher.py --patterns-file custom_patterns.txt

# Show help
python key_searcher.py --help
```

**Docker:**

```bash
# Start container
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

👉 **More Docker options:** See [DOCKER.md](DOCKER.md) for advanced configuration, CPU/Memory limits, multi-container setup, etc.

The script automatically uses all available CPU cores.

#### Configuration

**Environment Variable (Docker):**

In `docker-compose.yml`:

```yaml
environment:
  - MAX_PATTERN_LENGTH=10  # Save patterns up to 10 characters only once
```

**Command-Line Arguments (Python):**

- `--max-pattern-length N` - Maximum pattern length for duplicate prevention (default: 7)
- `--patterns-file FILE` - Path to pattern file (default: searchFor.txt)
- `--output-dir DIR` - Output directory (default: found_keys)

### 3. Stop Script

Press `Ctrl+C` to stop the search. All already found keys remain saved.

## Output

Found keys are saved in the `found_keys/` folder with the following format:

- **Filename**: `{EPOCH}_{PATTERN}.txt` (e.g., `1735700000_CAFE.txt`)
- **Content**: Private Key (PEM), Public Key (PEM), Public Key (Base58)

**Public Key Format**: The Base58-encoded Public Key is the key you distribute!

```
Example: CAFEM37BEuiceCLzuduYBHiYTsjfWSTaCtYdnas5JGkV
```

**⚠️ IMPORTANT:** The Private Keys are NOT encrypted! Keep these files secure and do not share them!

## Duplicate Prevention

The script automatically detects already found patterns (up to 7 characters, configurable) in the `found_keys/` folder:

- All existing files are scanned at startup
- Already found patterns are skipped
- Only new patterns are searched and saved

**Example output at startup:**

```
Already found (will be skipped): 9
  -> 1337, ACAB, BABE, BEEF, CAFE, DEAD, DEED, FADE, FEED
```

## Live Statistics

During the search, the script shows detailed progress updates:

```
Worker 0: 300,000 Keys checked | Total: 1,200,000 | Found: 3 | Session: [ABC123, C0DED, FACE]
```

**Display elements:**
- **Worker N**: Which CPU core is working
- **Keys checked**: Number of keys checked by this worker
- **Total**: Total number of all checked keys (all workers)
- **Found**: Number of matches found in this session
- **Session**: List of patterns found in this session (alphabetically sorted)

**At session end:**
```
======================================================================
Search completed!
Checked Keys: 5,234,567
Found Matches: 5
Found Patterns in this session: BABE, C0DE, DEAD, FACE, FEED
======================================================================
```

## Performance

Speed depends on your CPU. Typical values:

- 4 Cores: ~100,000 - 150,000 Keys/second
- 8 Cores: ~200,000 - 300,000 Keys/second
- 16 Cores: ~400,000 - 600,000 Keys/second

**Note:** The longer the pattern, the less likely a match will be found!

**Example search:**
- 1 million keys in ~10 seconds (4 cores)
- Patterns with 4 characters: Average 1 match per ~10-20 million keys
- Patterns with 6 characters: Very rare, can take hours to days

## Probabilities

Probability of finding a pattern (Base58 alphabet has 58 characters):

- 4 characters (e.g., DEAD): ~1 in 11.3 million
- 6 characters (e.g., AAAAAA): ~1 in 38 billion
- 8 characters (e.g., DEADBEEF): ~1 in 128 trillion

**Tip:** Shorter patterns (4-7 characters) are realistic to find!

## MeshCore Integration

These keys are used for **MeshCore Repeaters** to:

- Ensure unique identification
- Avoid confusion
- Have easily recognizable and memorable addresses

The Base58 Public Key can be used directly as a repeater identifier.

### Setting up Private Key in MeshCore Repeater

To use a found Private Key in a MeshCore Repeater:

1. **Connect repeater via USB**
2. **Open CLI Console** (e.g., via Serial Monitor, PuTTY, or the MeshCore Console)
3. **Set Private Key** with the command:

   ```
   set prv.key <PRIVATE_KEY>
   ```

   Where `<PRIVATE_KEY>` is the Private Key from the generated file (without PEM header/footer, only the Base64 part or according to MeshCore format).
4. **Restart repeater** for the changes to take effect

**Example:**

```bash
set prv.key MC4CAQAwBQYDK2VwBCIEINO1JWgy+o2iLVy+mZZaVqewr/YKZZbVxOBaHP44t0cX
```

**Note:** The Public Key is automatically derived from the Private Key and should then start with the desired pattern (e.g., `CAFE...`).

## Security Notes

⚠️ **Keep Private Keys secure!**

- Never upload Private Keys to public repositories
- The `.gitignore` is already configured to exclude `found_keys/`
- Encrypt Private Keys with a strong password when storing long-term
- Keep backups of keys in a secure location

## Technical Details

- **Algorithm**: Ed25519 (Elliptic Curve Digital Signature Algorithm)
- **Key Length**: 256 Bit (32 Bytes)
- **Public Key Format**: Base58 encoding (like Bitcoin/Solana)
- **Public Key Length**: ~44 characters in Base58
- **Multiprocessing**: Uses Python's `multiprocessing` module
- **File Format**: Epoch timestamp for chronological sorting

## File Structure

```
PubKeySearcher/
├── key_searcher.py      # Main script
├── searchFor.txt        # Pattern list
├── .gitignore          # Git protection for keys
├── README.md           # This documentation
├── DOCKER.md           # Docker documentation
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
└── found_keys/         # Found keys (not in Git)
    ├── 1735700000_CAFE.txt
    ├── 1735700123_DEAD.txt
    └── ...
```

## Pattern Examples

The included `searchFor.txt` contains interesting patterns such as:

### Nice Repeating Patterns
- **AAAAAA, BBBBBB, CCCCCC** etc. - All same characters
- **000000, 111111, 222222** etc. - All same digits

### Hex Words (Geek Culture)
- **DEADBEEF, CAFEBABE, C0FFEE** - Classic hex words
- **BADC0DE, FACADE, DECADE** - More creative terms
- **FEED, FACE, BABE, BEEF** - Short memorable words

### Special Patterns
- **B0000000 to BF000000** - All B*000000 variants
- **123456, ABCDEF** - Sequences
- **1337, ACAB** - Culture numbers

## Troubleshooting

### "ModuleNotFoundError: No module named 'cryptography'" or "'base58'"

Install the required libraries:

```bash
pip install cryptography base58
```

### Script is slow

- Check if all CPU cores are being used (Task Manager / htop)
- Shorter patterns have higher success rates
- Modern CPUs with more cores are faster

### No matches found

This is normal! Depending on the pattern, it can take hours or days until a match is found.

**Recommendation:** Start with 4-6 character patterns for realistic success chances.

### PEM key doesn't start with pattern

This is correct! The **Base58 Public Key** (not the PEM format) starts with the pattern. The PEM format contains additional metadata and is intended for other purposes.

## License

This script is intended for personal and educational use as well as for MeshCore.

Dieses Script ist für persönliche und Bildungszwecke sowie für MeshCore gedacht.
