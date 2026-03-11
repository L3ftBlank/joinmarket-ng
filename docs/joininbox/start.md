# Quickstart

The Quickstart menu provides the most essential functions for new users to get started with JoinMarket quickly.

## Access the Quickstart Menu

From the main menu, select **START** or run:

```bash
menu
# Select: START
```

## Menu Options

```
┌─────────────────────────────────────────────────────────────────┐
│                   Quickstart options                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [GEN]      Generate a new wallet                               │
│  [m0]       Show the first mixdepth to deposit to               │
│  [DISPLAY]  Show the contents of all mixdepths                  │
│  [MAKER]    Run the Yield Generator                             │
│  [DOCS]     Link to the documentation                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| Option | Description |
|--------|-------------|
| **GEN** | Create a new JoinMarket wallet |
| **m0** | Display deposit address with QR code for funding |
| **DISPLAY** | Show all mixdepths and their contents |
| **MAKER** | Start the Yield Generator to earn fees |
| **DOCS** | Open documentation link with QR code |

---

## GEN - Generate a New Wallet

Creates a new JoinMarket wallet with a recovery seed.

### What Happens

1. Prompts for a wallet name (e.g., `mywallet.jmdat`)
2. Asks for an encryption password
3. Generates a 12-word recovery seed
4. Displays the seed **IMPORTANT: Write this down!**
5. Creates the wallet file in `~/.joinmarket/wallets/`

### Security Warning

!!! danger "Backup Your Seed"

    The recovery seed is only shown once. Write it down on paper and store it securely. Never store it digitally or online.

### After Creation

Use **m0** to display your first deposit address.

---

## m0 - Show First Mixdepth Deposit Address

Displays the first unused address from mixdepth 0 with a QR code for easy funding.

### What Happens

1. Prompts to select a wallet
2. Displays wallet contents
3. Shows the first "new" address from mixdepth 0
4. Displays address as QR code

### Example Output

```
Fund the wallet on the first 'new' address to get started:

bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

████████████████████████████
████████████████████████████
████████████████████████████
... (QR code)
```

### Why Mixdepth 0?

- Mixdepth 0 is the entry point for new funds
- Coins automatically move to higher mixdepths during CoinJoins
- Starting at mixdepth 0 ensures proper privacy flow

---

## DISPLAY - Show Wallet Contents

Displays all addresses and balances across all 5 mixdepths.

### What Happens

1. Prompts to select a wallet
2. Shows all mixdepths (0-4)
3. Lists addresses with balances
4. Indicates which addresses are "new" (unused)

### Example Output

```
Mixdepth 0:
  address           bc1q...  balance: 0.05000000 BTC  new
  address           bc1q...  balance: 0.00000000 BTC  used

Mixdepth 1:
  address           bc1q...  balance: 0.02500000 BTC  new
  ...

Total balance: 0.07500000 BTC
```

---

## MAKER - Run Yield Generator

Starts the Yield Generator to earn fees by providing liquidity.

### What Happens

1. Prompts to select a wallet
2. Asks for the wallet password
3. Starts the Yield Generator service
4. Displays logs and status

### Prerequisites

- Funded wallet with UTXOs in mixdepth 0
- Sufficient confirmations (typically 5+)
- Running Bitcoin Core connection

!!! tip "Learn More"

    For detailed Yield Generator configuration, see [Yield Generator](maker.md).

---

## DOCS - Documentation Link

Displays a link to the JoininBox documentation with a QR code.

### Output

```
Find a collection of written documentation and links to videos at:
https://github.com/openoms/joininbox#more-info

████████████████████████████
████████████████████████████
... (QR code)
```

---

## Typical Quickstart Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Quickstart Workflow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. GEN         Create a new wallet                             │
│       ↓                                                         │
│  2. m0          Get deposit address + QR code                   │
│       ↓                                                         │
│  3. Fund        Send Bitcoin to the address                     │
│       ↓                                                         │
│  4. Wait        Wait for confirmations (5+ recommended)         │
│       ↓                                                         │
│  5. DISPLAY     Verify funds arrived                            │
│       ↓                                                         │
│  6. MAKER       Start earning fees (optional)                   │
│       or                                                        │
│  6. SEND        Send a CoinJoin payment (optional)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tips for New Users

| Tip | Description |
|-----|-------------|
| **Start with small amounts** | Test the workflow with small amounts first |
| **Wait for confirmations** | 5+ confirmations recommended for Maker |
| **Use Tor** | Enable Tor in CONFIG for privacy |
| **Backup your seed** | Write it down, never store digitally |
| **Start with DISPLAY** | Always verify your wallet before operations |

---

## Next Steps

After completing the quickstart:

| Goal | Menu Path |
|------|-----------|
| Send a private payment | [SEND](send.md) |
| Earn fees as a Maker | [Yield Generator](maker.md) |
| Advanced wallet options | [WALLET](wallet.md) |
| Configure connections | [CONFIG](config.md) |
