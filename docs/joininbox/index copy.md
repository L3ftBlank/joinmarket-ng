---
title: JoininBox
---
# JoininBox

## Overview

JoininBox is a menu-driven interface for JoinMarket that simplifies common operations through an interactive dialog-based GUI. It provides easy access to all JoinMarket functions without requiring command-line knowledge.

## Main Menu

<div class="joininbox-menu" markdown>

| Getting Started | |
|:----------------|:--|
| [**START**](quickstart.md) | Quickstart with JoinMarket |

| Core Functions | |
|:---------------|:--|
| [**WALLET**](wallet.md) | Wallet management options |
| [**MAKER**](maker.md) | Yield Generator options |
| [**SEND**](send.md) | Pay to an address with/without a coinjoin |
| [**FREEZE**](freeze.md) | Exercise coin control within a mixdepth |
| [**PAYJOIN**](payjoin.md) | Send/Receive between JoinMarket wallets |
| [**OFFERS**](orderbook.md) | Watch the Order Book locally |

| Settings & Tools | |
|:-----------------|:--|
| [**CONFIG**](config.md) | Connection and joinmarket.cfg settings |
| [**TOOLS**](tools.md) | Extra helper functions and services |
| [**UPDATE**](update.md) | Update JoininBox or JoinMarket |

| System | |
|:-------|:--|
| **JAM** | JoinMarket Web UI options (RaspiBlitz only) |
| **BLITZ** | Switch to the RaspiBlitz menu (RaspiBlitz only) |
| **REBOOT** | Restart the computer |
| **SHUTDOWN** | Switch off the computer |

</div>

## Menu Preview

The JoininBox main menu displayed in a terminal:

```
┌─────────────────────────────────────────────────────────────┐
│         JoininBox GUI [VERSION] network:[NET] IP:[IP]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Choose from the options:                                   │
│                                                             │
│  [START](quickstart.md)    Quickstart with JoinMarket       │
│  [JAM]                     JoinMarket Web UI (RaspiBlitz)   │
│                                                             │
│  [WALLET](wallet.md)       Wallet management options        │
│  [MAKER](maker.md)         Yield Generator options          │
│                                                             │
│  [SEND](send.md)           Pay with/without coinjoin        │
│  [FREEZE](freeze.md)       Coin control                     │
│  [PAYJOIN](payjoin.md)     Send/Receive PayJoin             │
│                                                             │
│  [OFFERS](orderbook.md)    Watch the Order Book locally     │
│                                                             │
│  [CONFIG](config.md)       Connection settings              │
│  [TOOLS](tools.md)         Helper functions                 │
│  [UPDATE](update.md)       Update JoininBox/JoinMarket      │
│                                                             │
│  [BLITZ]                   RaspiBlitz menu (RaspiBlitz)     │
│  [REBOOT]                  Restart the computer             │
│  [SHUTDOWN]                Switch off the computer          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Starting the Menu

To start the JoininBox menu, run:

```bash
menu
```

Or directly:

```bash
/home/joinmarket/menu.sh
```

## Documentation Sections

### Getting Started

| Section | Description |
|---------|-------------|
| [Installation](installation.md) | Install JoininBox on your system |
| [Quickstart](quickstart.md) | Quick start options for new users |

### Core Functions

| Section | Description |
|---------|-------------|
| [Wallet](wallet.md) | Wallet creation, recovery, and management |
| [Yield Generator](maker.md) | Run as a liquidity provider to earn fees |
| [Send Payment](send.md) | Send payments with or without CoinJoin |
| [Freeze UTXO](freeze.md) | Coin control - freeze and unfreeze UTXOs |
| [PayJoin](payjoin.md) | Direct PayJoin transactions between JoinMarket wallets |
| [Order Book](orderbook.md) | Monitor the JoinMarket order book locally |

### Configuration & Maintenance

| Section | Description |
|---------|-------------|
| [Configuration](config.md) | Connection settings and joinmarket.cfg |
| [Tools](tools.md) | Helper functions and additional services |
| [Update](update.md) | Update JoininBox and JoinMarket |
| [CLI Commands](commands.md) | Command-line shortcuts and aliases |

## Key Features

| Feature | Description |
|---------|-------------|
| **Wallet Management** | Create, recover, display, and manage JoinMarket wallets |
| **CoinJoin** | Send payments with privacy-enhancing CoinJoin |
| **Yield Generator** | Earn sats by providing liquidity as a Maker |
| **PayJoin** | Direct collaborative transactions between JoinMarket users |
| **Fidelity Bonds** | Create timelocked addresses for improved Maker reputation |
| **Order Book** | Local monitoring of available offers via Tor hidden service |
| **Coin Control** | Freeze and unfreeze specific UTXOs |
| **QR Codes** | Display addresses and information as QR codes |

## Mixdepths

JoinMarket wallets use 5 mixdepths (0-4) for coin segregation:

```
Mixdepth 0 ←→ Mixdepth 1 ←→ Mixdepth 2 ←→ Mixdepth 3 ←→ Mixdepth 4
```

- Each mixdepth acts as a separate account within the wallet
- Coins automatically move between mixdepths during CoinJoins
- Use mixdepth 0 for incoming funds
- Higher mixdepths indicate more privacy rounds

## Configuration Files

| File | Path | Description |
|------|------|-------------|
| `joinmarket.cfg` | `~/.joinmarket/joinmarket.cfg` | Main JoinMarket configuration |
| `joinin.conf` | `~/joinin.conf` | JoininBox settings |
| Wallets | `~/.joinmarket/wallets/` | Wallet files (`.jmdat`) |
| Logs | `~/.joinmarket/logs/` | Log files |
| YG Statement | `~/.joinmarket/logs/yigen-statement.csv` | Yield Generator earnings |

## Related Resources

- [JoininBox GitHub Repository](https://github.com/openoms/joininbox)
- [JoinMarket Usage Documentation](https://github.com/JoinMarket-Org/joinmarket-clientserver/blob/master/docs/USAGE.md)
- [JoinMarket NG Orderbook](https://joinmarket-ng.sgn.space/)
