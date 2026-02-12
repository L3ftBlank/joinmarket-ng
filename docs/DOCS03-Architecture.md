## Architecture

### System Overview






```
                    ┌──────────────────────┐
                    │   Directory Server   │
                    │  (Message Routing)   │
                    └──────────┬───────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
      ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
      │  Maker 1  │      │  Maker 2  │      │   Taker   │
      │           │      │           │      │           │
      │  Wallet   │      │  Wallet   │      │  Wallet   │
      │           │      │           │      │           │
      └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
            │                  │                  │
            └──────────────────┴──────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Bitcoin Core / SPV  │
                    │  (Neutrino Option)   │
                    └──────────────────────┘
```



``` mermaid
flowchart TD
    DS["Directory Server<br/>(Message Routing)"]
    
    DS --> M1["Maker 1<br/>Wallet"]
    DS --> M2["Maker 2<br/>Wallet"]
    DS --> TK["Taker<br/>Wallet"]
    
    M1 --> BC["Bitcoin Core / SPV<br/>(Neutrino Option)"]
    M2 --> BC
    TK --> BC
    
    style DS fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style M1 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style M2 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style TK fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style BC fill:#fff3e0,stroke:#e65100,stroke-width:2px
```

### Components

The implementation separates concerns into distinct packages:

| Package | Purpose |
|---------|---------|
| `jmcore` | Core library: crypto, protocol definitions, models |
| `jmwallet` | Wallet: BIP32/39/84, UTXO management, signing |
| `directory_server` | Directory node: message routing, peer registry |
| `maker` | Maker bot: offer management, CoinJoin participation |
| `taker` | Taker bot: CoinJoin orchestration, maker selection |
| `orderbook_watcher` | Monitoring: orderbook visualization |
| `neutrino_server` (external) | Lightweight SPV server (BIP157/158) - [github.com/m0wer/neutrino-api](https://github.com/m0wer/neutrino-api) |

### Data Directory

JoinMarket NG uses a dedicated data directory for persistent files shared across sessions.

**Location:**
- Default: `~/.joinmarket-ng`
- Override: `--data-dir` CLI flag or `$JOINMARKET_DATA_DIR` environment variable
- Docker: `/home/jm/.joinmarket-ng` (mounted as volume)

**Structure:**

```
~/.joinmarket-ng/
├── config.toml            # Configuration file
├── cmtdata/
│   ├── commitmentlist     # PoDLE commitment blacklist (makers)
│   └── commitments.json   # PoDLE used commitments (takers)
├── state/
│   ├── maker.nick         # Current maker nick
│   ├── taker.nick         # Current taker nick
│   ├── directory.nick     # Current directory server nick
│   └── orderbook.nick     # Current orderbook watcher nick
├── coinjoin_history.csv   # Transaction history log
└── fidelity_bonds.json    # Bond registry
```

**Shared Files:**

| File | Used By | Purpose |
|------|---------|---------|
| `cmtdata/commitmentlist` | Makers | Network-wide blacklisted PoDLE commitments |
| `cmtdata/commitments.json` | Takers | Locally used commitments (prevents reuse) |
| `coinjoin_history.csv` | Both | Transaction history with confirmation tracking |
| `state/*.nick` | All | Component nick files for self-CoinJoin protection |

**Nick State Files:**

Written at startup, deleted on shutdown. Used for:
- External monitoring of running bots
- Startup notifications with nick identification
- **Self-CoinJoin Protection**: Taker reads `state/maker.nick` to exclude own maker; maker reads `state/taker.nick` to reject own taker

**CoinJoin History:**

Records all CoinJoin transactions with:
- Pending transaction tracking (initially `success=False`, updated on confirmation)
- Automatic txid discovery for makers who didn't receive the final transaction
- Address blacklisting for privacy (addresses recorded before being shared with peers)
- CSV format for analysis: `jm-wallet history --stats`
