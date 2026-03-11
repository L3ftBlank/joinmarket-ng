# Wallet

The Wallet menu provides comprehensive wallet management options for creating, recovering, displaying, and managing JoinMarket wallets.

## Access the Wallet Menu

From the main menu, select **WALLET** or run:

```bash
menu
# Select: WALLET
```

## Menu Options

```
┌─────────────────────────────────────────────────────────────────┐
│                     WALLET OPTIONS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [GEN]      Generate a new wallet                               │
│  [RECOVER]  Recover a wallet from seed words                    │
│  [DISPLAY]  Display all addresses and balances                  │
│  [SHOWSEED] Show the wallet seed words                          │
│  [HISTORY]  Show recent transactions                            │
│  [BALANCE]  Show total balance                                  │
│  [RESCAN]   Rescan the blockchain                               │
│  [LOCK]     Lock the wallet                                     │
│  [UNLOCK]   Remove wallet lockfile                              │
│  [FREEZE]   Freeze/unfreeze UTXOs                               │
│  [FIDELITY] Fidelity bond options                               │
│  [QR]       Show address as QR code                             │
│  [UTXO]     List all UTXOs                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| Option | Description |
|--------|-------------|
| **GEN** | Create a new JoinMarket wallet |
| **RECOVER** | Restore a wallet from 12-word seed |
| **DISPLAY** | Show all addresses and balances per mixdepth |
| **SHOWSEED** | Display the wallet seed for backup |
| **HISTORY** | Show recent transaction history |
| **BALANCE** | Display total wallet balance |
| **RESCAN** | Rescan blockchain for transactions |
| **LOCK** | Lock wallet to prevent concurrent access |
| **UNLOCK** | Remove lockfile if wallet is stuck |
| **FREEZE** | Freeze or unfreeze specific UTXOs |
| **FIDELITY** | Create and manage fidelity bonds |
| **QR** | Display an address as QR code |
| **UTXO** | List all unspent transaction outputs |

---

## GEN - Generate a New Wallet

Creates a new JoinMarket wallet with a 12-word recovery seed.

### What Happens

1. Prompts for a wallet name (default: `wallet.jmdat`)
2. Asks for an encryption password
3. Generates a 12-word BIP39 recovery seed
4. Displays the seed words **IMPORTANT: Write this down!**
5. Creates the wallet file in `~/.joinmarket/wallets/`

### Security Warnings

!!! danger "Backup Your Seed"

    - Write down the 12-word seed on paper
    - Never store it digitally or online
    - The seed is only shown ONCE
    - Without the seed, funds cannot be recovered

### Example Session

```
Enter wallet file name (default: wallet.jmdat): mywallet.jmdat
Enter passphrase to encrypt wallet: ********
Re-enter passphrase: ********

Your 12-word recovery seed:
================================
word1 word2 word3 word4 word5 word6
word7 word8 word9 word10 word11 word12
================================

WRITE THIS DOWN! It will NOT be shown again.
```

### After Creation

1. Use **QR** or **DISPLAY** to get a deposit address
2. Send a small test amount first
3. Verify with **BALANCE** or **DISPLAY**

---

## RECOVER - Recover Wallet from Seed

Restores a wallet from a previously saved 12-word seed phrase.

### What Happens

1. Prompts for a wallet name
2. Asks for the 12-word seed phrase
3. Optionally sets a gap limit for address scanning
4. Creates the wallet file

### Example Session

```
Enter wallet file name: recovered.jmdat
Enter seed words (12 words): word1 word2 ... word12
Enter gap limit (default: 6): 6

Wallet recovered successfully!
```

### Gap Limit

The gap limit determines how many unused addresses to scan per mixdepth. Increase if:
- You used many addresses
- Not seeing all your funds
- Recovering an old wallet

---

## DISPLAY - Display Wallet Contents

Shows all addresses and balances across all 5 mixdepths.

### What Happens

1. Prompts to select a wallet
2. Displays addresses grouped by mixdepth
3. Shows balance per address
4. Indicates which addresses are "new" (unused)

### Example Output

```
Mixdepth 0:
  new     bc1qabc...  0.00000000 BTC
  used    bc1qdef...  0.05000000 BTC
  new     bc1qghi...  0.00000000 BTC

Mixdepth 1:
  new     bc1qjkl...  0.02500000 BTC
  used    bc1qmno...  0.00000000 BTC

Mixdepth 2:
  (empty)

Mixdepth 3:
  (empty)

Mixdepth 4:
  (empty)

Total balance: 0.07500000 BTC
```

### Address States

| State | Description |
|-------|-------------|
| `new` | Address has never received funds |
| `used` | Address has received funds before |

---

## SHOWSEED - Show Wallet Seed

Displays the 12-word recovery seed for the current wallet.

### What Happens

1. Prompts to select a wallet
2. Asks for wallet password
3. Displays the seed words

!!! warning "Security Notice"

    Only display the seed in a private environment. Anyone with the seed can access your funds.

---

## HISTORY - Show Transaction History

Displays recent transactions for the wallet.

### What Happens

1. Prompts to select a wallet
2. Shows list of recent transactions
3. Includes transaction type, amount, and confirmations

### Example Output

```
Recent transactions:
====================
Type: deposit
Amount: +0.05 BTC
Address: bc1qabc...
Confirmations: 42

Type: coinjoin
Amount: -0.001 BTC (fee)
Mixdepth: 0 → 1
Confirmations: 18

Type: payment
Amount: -0.025 BTC
Address: bc1qexternal...
Confirmations: 6
```

---

## BALANCE - Show Total Balance

Displays the total balance across all mixdepths.

### What Happens

1. Prompts to select a wallet
2. Shows balance per mixdepth
3. Shows total balance

### Example Output

```
Mixdepth 0: 0.05000000 BTC
Mixdepth 1: 0.02500000 BTC
Mixdepth 2: 0.00000000 BTC
Mixdepth 3: 0.00000000 BTC
Mixdepth 4: 0.00000000 BTC
-------------------------
Total:      0.07500000 BTC
```

---

## RESCAN - Rescan Blockchain

Rescans the blockchain for wallet transactions.

### What Happens

1. Prompts to select a wallet
2. Asks for rescan height (block height to start from)
3. Initiates blockchain rescan via Bitcoin Core

### When to Rescan

- After recovering a wallet
- Missing transactions
- After importing addresses
- Balance seems incorrect

### Example

```
Enter block height to start rescan (default: 0 for full rescan): 800000
Starting rescan from block 800000...
This may take a while.
```

---

## LOCK - Lock Wallet

Locks the wallet to prevent concurrent access.

### What Happens

1. Prompts to select a wallet
2. Creates a lockfile
3. Prevents other processes from using the wallet

### When to Lock

- Running multiple JoinMarket operations
- Preventing concurrent access
- Troubleshooting lock issues

---

## UNLOCK - Remove Wallet Lockfile

Removes the wallet lockfile if the wallet is stuck.

### What Happens

1. Lists all lockfiles
2. Prompts to remove selected lockfile

!!! warning "Caution"

    Only unlock if you are certain no other process is using the wallet. Unlocking during active operations can corrupt wallet data.

### When to Unlock

- Wallet appears locked but no process is running
- After a crash or unexpected shutdown
- "Wallet is locked" error persists

---

## FREEZE - Freeze/Unfreeze UTXOs

Freeze or unfreeze specific UTXOs to prevent them from being spent.

### What Happens

1. Prompts to select a wallet
2. Lists all UTXOs with freeze status
3. Allows toggling freeze status

### Use Cases

| Scenario | Action |
|----------|--------|
| Preserve specific coins | Freeze UTXO |
| Prevent small UTXOs from being used | Freeze dust |
| Privacy planning | Select which coins to use |
| Troubleshooting | Temporarily exclude coins |

!!! tip "See Also"

    For detailed coin control, see [Freeze UTXO](freeze.md).

---

## FIDELITY - Fidelity Bond Options

Create and manage fidelity bonds for improved Maker reputation.

### What Happens

Displays a submenu for fidelity bond operations:

```
┌─────────────────────────────────────────────────────────────────┐
│                   FIDELITY BOND OPTIONS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [CREATE]   Create a new fidelity bond                          │
│  [LIST]     List existing fidelity bonds                        │
│  [SPEND]    Spend/cancel a fidelity bond                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### What is a Fidelity Bond?

A fidelity bond is a timelocked Bitcoin output that:

- Proves you have committed funds for a period
- Increases your reputation as a Maker
- Can help earn higher fees
- Is burned (cannot be spent until timelock expires)

### CREATE - Create Fidelity Bond

1. Select wallet and mixdepth
2. Choose bond amount
3. Select timelock duration (months)
4. Confirm creation

### LIST - List Fidelity Bonds

Shows all existing fidelity bonds with:

- Amount
- Locktime
- Address
- Status

### SPEND - Spend Fidelity Bond

Spends a matured fidelity bond (after timelock expires).

---

## QR - Show Address as QR Code

Displays a wallet address as a QR code for easy scanning.

### What Happens

1. Prompts to select a wallet
2. Prompts to select a mixdepth
3. Shows the first "new" address
4. Displays address as QR code

### Example Output

```
Address: bc1qabc123def456...

████████████████████████████
████████████████████████████
████████████████████████████
... (QR code displayed)
```

### Use Cases

- Receiving payments
- Wallet deposits
- Transferring funds

---

## UTXO - List All UTXOs

Lists all unspent transaction outputs in the wallet.

### What Happens

1. Prompts to select a wallet
2. Lists each UTXO with details:
   - Transaction ID
   - Output index
   - Amount
   - Address
   - Mixdepth
   - Confirmations
   - Freeze status

### Example Output

```
UTXOs in wallet.jmdat:
=====================

TXID: abc123...:0
  Amount: 0.05000000 BTC
  Address: bc1qabc...
  Mixdepth: 0
  Confirmations: 42
  Frozen: no

TXID: def456...:1
  Amount: 0.02500000 BTC
  Address: bc1qdef...
  Mixdepth: 1
  Confirmations: 18
  Frozen: no

Total UTXOs: 2
Total value: 0.07500000 BTC
```

---

## Wallet File Locations

| File | Path | Description |
|------|------|-------------|
| Wallets | `~/.joinmarket/wallets/` | Wallet files (`.jmdat`) |
| Lockfiles | `~/.joinmarket/wallets/` | Wallet lockfiles (`.lock`) |
| Logs | `~/.joinmarket/logs/` | Wallet operation logs |
| Config | `~/.joinmarket/joinmarket.cfg` | JoinMarket configuration |

---

## Best Practices

| Practice | Description |
|----------|-------------|
| **Backup seed** | Write down the 12-word seed and store securely |
| **Test first** | Send a small test amount before large deposits |
| **Use mixdepth 0** | Always deposit to mixdepth 0 for new funds |
| **Wait for confirmations** | 5+ confirmations recommended for Maker |
| **Don't reuse addresses** | Use a new address for each deposit |
| **Regular backups** | Backup wallet files after important transactions |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Wallet not found" | Check wallet name in `~/.joinmarket/wallets/` |
| "Wallet is locked" | Use UNLOCK to remove lockfile |
| "Invalid password" | Check keyboard layout, Caps Lock |
| Missing balance | Use RESCAN to find transactions |
| Cannot spend | Check if UTXOs are frozen |

---

## Related Topics

| Topic | Description |
|-------|-------------|
| [Quickstart](quickstart.md) | Quick start guide |
| [Send Payment](send.md) | Send payments with CoinJoin |
| [Freeze UTXO](freeze.md) | Advanced coin control |
| [Configuration](config.md) | Wallet and network configuration |
