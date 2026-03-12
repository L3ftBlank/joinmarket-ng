# JoininBox Submenu MAKER

The MAKER menu provides options for running and managing the JoinMarket Yield Generator. Makers provide liquidity to the network and earn trading fees by accepting CoinJoin offers.

<div class="terminal-menu">
┌────────────Yield Generator options──────────────┐
│ ┌─────────────────────────────────────────────┐ │
│ │<a href="../maker/">MAKER</a>    Run the Yield Generator             │ │  
│ │<a href="../jmconf/">JMCONF</a>   YG settings in the joinmarket.cfg   │ │ 
│ │<a href="../yglist/">YGLIST</a>   List the past YG activity           │ │ 
│ │<a href="../stats/">STATS</a>    Show the sats earned as a Maker     │ │
│ │<a href="../nickname/">NICKNAME</a> Show the last used counterparty name│ │
│ │<a href="../service/">SERVICE</a>  Monitor the YG service (INFO)       │ │
│ │<a href="../logs/">LOGS</a>     View the last YG logfile (DEBUG)    │ │
│ │<a href="../stop/">STOP</a>     Stop the YG service                 │ │
│ │<a href="../timelock/">TIMELOCK</a> Create a Fidelity Bond address      │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│          <a href="../wallet/">< Select ></a>     <a href="../menu-main/">< Back ></a>                │
└─────────────────────────────────────────────────┘
</div>

**Note:** In the terminal, type the menu letter (e.g., `MAKER`) and press Enter. In this documentation, you can click on the menu items above.

---

## **Menu Options Description**

### **MAKER - Run the Yield Generator**

Starts the JoinMarket Yield Generator (YM) to provide liquidity to the network.

**Command:**
```bash
python yield-generator.py --config joinmarket.cfg start
```

**Prerequisites:**
- A funded wallet with multiple mixdepths
- Proper joinmarket.cfg configuration
- Tor running for anonymous connections

---

### **PAUSE - Pause the Yield Generator**

Temporarily pauses the Yield Generator without stopping it. Useful for maintenance or troubleshooting.

**Effect:**
- Offers are no longer placed
- Existing offers remain active
- Can be resumed with START

---

### **STOP - Stop the Yield Generator**

Completely stops the Yield Generator and removes all active offers.

**Warning:** All pending offers will be cancelled.

**Command:**
```bash
python yield-generator.py --config joinmarket.cfg stop
```

---

### **STATUS - View current generator status**

Shows the current status of the Yield Generator including:
- Active offers
- Earned fees
- Number of transactions
- Uptime

**Command:**
```bash
python yield-generator.py --config joinmarket.cfg status
```

---

### **OFFERS - View active offers**

Displays all current active offers placed by your Yield Generator on the order book.

**Information shown:**
- Offer size (amount)
- Mixdepth used
- Offer type (coinjoin rounds)
- Current status

---

### **EDIT - Edit maker offer configuration**

Modify the offer parameters including:
- Amount ranges (min/max)
- Number of mixes per transaction
- Coinjoin round count
- Fee settings

**Configuration file:** `~/.joinmarket/maker.conf`

---

### **FILTERS - Configure offer filters**

Set filters to control which orders you are willing to participate in:
- Minimum round count
- Maximum amount
- Maker availability windows
- Fee preferences

**Purpose:** Prevent participation in undesirable transactions

---

### **SETTINGS - Configure generator settings**

Access the full JoinMarket configuration including:
- Network settings (Tor)
- Wallet paths
- API endpoints
- Logging and output options

**Configuration file:** `~/.joinmarket/joinmarket.cfg`

---

## **Navigation**

| Option | Description |
|--------|-------------|
| `< Select >` | Executes the chosen option in the terminal |
| `< Back >` | Returns to the main menu (`menu-main.md`) |

---

## **Example: Starting a Yield Generator**

```bash
$ python yield-generator.py --config joinmarket.cfg start
Starting Yield Generator...
Wallet: wallet.jmdat
Active offers: 5
Mixdepths configured: 5
Minimum round: 2
Maximum round: 5

Generator running. Press Ctrl+C to stop.
```

---

## **Yield Generator Benefits**

| Benefit | Description |
|---------|-------------|
| **Passive Income** | Earn Bitcoin fees by providing liquidity |
| **Privacy Contribution** | Help make CoinJoin effective for all users |
| **No Active Management** | Runs in background after configuration |
| **Network Support** | Strengthens the privacy network |
| **Flexible** | Can start/stop/pause at any time |

---

## **Important Notes**

⚠️ **Funding Requirements:**
- Ensure your wallet has sufficient funds across multiple mixdepths
- Avoid using your main spending wallet for Yield Generation

⚠️ **Privacy Best Practices:**
- Run the YM behind Tor for anonymity
- Use multiple mixdepths to avoid pattern analysis
- Avoid making offers from the same address repeatedly

⚠️ **System Requirements:**
- Bitcoin Core wallet loaded (non-descriptor)
- Tor service running
- Stable internet connection

