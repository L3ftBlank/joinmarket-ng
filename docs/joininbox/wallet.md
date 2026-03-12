# JoininBox Submenu WALLET

The WALLET menu provides comprehensive options for managing JoinMarket wallets.

<div class="terminal-menu">
┌────────────Wallet management options─────────────┐
│ ┌──────────────────────────────────────────────┐ │
│ │<a href="../display/">DISPLAY</a>     Show the contents of all mixdepths│ │
│ │<a href="../labels/">LABEL</a>       Add or edit a label to an address │ │
│ │<a href="../utxos/">UTXOS</a>       Show all the coins in the wallet  │ │
│ │<a href="../history/">HISTORY</a>     Show all past transactions        │ │
│ │<a href="../xpubs/">XPUBS</a>       Show the master public keys       │ │
│ │<a href="../psbt/">PSBT</a>        Sign a Base64 format PSBT         │ │
│ │<a href="../create-wallet/">GEN</a>         Generate a new wallet             │ │
│ │<a href="../import-wallet/">IMPORT</a>      Copy wallet(s) from a remote node │ │
│ │<a href="../showseed/">SHOWSEED</a>    Shows the wallet recovery seed    │ │
│ │<a href="../recover/">RECOVER</a>     Restore a wallet from the seed    │ │
│ │<a href="../increase-gap/">INCREASEGAP</a> Increase the gap limit            │ │
│ │<a href="../rescan/">RESCAN</a>      Rescan the Bitcoin Core wallet    │ │
│ │<a href="../unlock/">UNLOCK</a>      Remove the lockfiles              │ │
│ └──────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────┤     
│            <a href="../wallet/">< Select ></a>      <a href="../menu-main/">< Back ></a>              │
└──────────────────────────────────────────────────┘
</div>

**Note:** In the terminal, type the menu letter (e.g., `GEN`) and press Enter. In this documentation, you can click on the menu items above.

---

## **Menu Options Description**

### **DISPLAY - Show all mixdepths**

Displays the balance and UTXOs of all mixdepths in your wallet.

**Command:**
```bash
python wallet-tool.py display
```

---

### **LABEL - Label addresses**

Adds or edits a label for a specific address in the wallet.

**Command:**
```bash
python wallet-tool.py setlabel [address] [label]
```

---

### **UTXOS - Show unspent transaction outputs**

Lists all unspent coins (UTXOs) in the wallet.

**Command:**
```bash
python wallet-tool.py showutxos
```

---

### **HISTORY - Show all past transactions**

Shows transaction history with verbose output.

**Command:**
```bash
python wallet-tool.py history -v 4
```

---

### **XPUBS - Show master public keys**

Displays the 5 master public keys (one for each mixdepth).

**Usage:**
- Import these keys to Specter Desktop or Electrum for watch-only wallets
- Required for hardware wallet integration

---

### **PSBT - Sign PSBT**

Signs a Partially Signed Bitcoin Transaction (Base64 format).

**Command:**
```bash
python wallet-tool.py signpsbt
```

---

### **GEN - Generate a new wallet**

Creates a new JoinMarket wallet using the `wallet-tool.py` script.

**Command:**
```bash
python wallet-tool.py generate
```

---

### **IMPORT - Copy wallet(s) from a remote node**

Copies wallet(s) from a remote node.

---

### **SHOWSEED - Show recovery seed**

Displays the wallet recovery seed phrase.

⚠️ **Security Warning:** Never share your seed phrase with anyone!

---

### **RECOVER - Restore from seed**

Restores a wallet from a backup seed phrase.

**Command:**
```bash
python wallet-tool.py recover
```

---

### **INCREASEGAP - Increase gap limit**

The gap limit is the number of empty addresses after which the wallet stops looking for funds. Default is 6.

**Command:**
```bash
python wallet-tool.py --recoversync -g [new-gap-limit] [wallet.jmdat]
```

---

### **RESCAN - Rescan blockchain**

Rescans the Bitcoin Core wallet from a specified block height.

**First SegWit block:** 481824

**Command:**
```bash
bitcoin-cli -conf=/mnt/hdd/app-data/bitcoin/bitcoin.conf rescanblockchain [blockheight]
```

---

### **UNLOCK - Remove lockfiles**

Removes wallet lockfiles if the wallet is stuck in a locked state.

**Commands:**
```bash
rm ~/.joinmarket/wallets/.*.lock
rm ~/.joinmarket/wallets/*.lock
```

---

## **Navigation**

| Option | Description |
|--------|-------------|
| `< Select >` | Executes the chosen option in the terminal |
| `< Back >` | Returns to the main menu (`menu-main.md`) |

---

## **Example: Displaying Mixdepths**

```bash
$ python wallet-tool.py display
wallet: wallet.jmdat
mixdepth 0: 0.00123456 BTC (10000 sats)
mixdepth 1: 0.00234567 BTC (234567 sats)
mixdepth 2: 0.00345678 BTC (345678 sats)
mixdepth 3: 0.00456789 BTC (456789 sats)
mixdepth 4: 0.00567890 BTC (567890 sats)
```

