
# JoininBox - Complete Menu Documentation

**Version:** v0.8.5 Mainnet  
**Project:** JoinMarket NG Documentation  
**Last Updated:** 2026-03-13

---

## Table of Contents

- [START](#start)
- [WALLET](#wallet)
- [MAKER](#maker)
- [SEND](#send)
- [FREEZE](#freeze)
- [PAYJOIN](#payjoin)
- [OFFERS](#offers)
- [CONFIG](#config)
- [TOOLS](#tools)
- [UPDATE](#update)
  - [Advanced Update Options](#advanced-update-options)
- [BLITZ](#blitz)

## Hauptmenü {#m000}
---
<div class="terminal-menu">
┌────────────────JoininBox v0.8.5 mainnet─────────────────┐
│                                                         │
│   Choose from the options:                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │<a href="#m100">START</a>     Quickstart with JoinMarket               │  │
│  │                                                   │  │
│  │<a href="#m120">WALLET</a>    Wallet management options                │  │
│  │<a href="../maker/">MAKER</a>     Yield Generator options                  │  │
│  │                                                   │  │
│  │<a href="../send/">SEND</a>      Pay to an address with/without a coinjoin│  │
│  │<a href="../freeze/">FREEZE</a>    Exercise coin control within a mixdepth  │  │
│  │<a href="../payjoin/">PAYJOIN</a>   Send/Receive between JoinMarket wallets  │  │
│  │                                                   │  │
│  │<a href="../offers/">OFFERS</a>    Watch the Order Book locally             │  │
│  │                                                   │  │
│  │<a href="../config/">CONFIG</a>    Connection and joinmarket.cfg settings   │  │
│  │<a href="../tools/">TOOLS</a>     Extra helper functions and services      │  │
│  │<a href="../update/">UPDATE</a>    Update JoininBox or JoinMarket           │  │
│  │                                                   │  │
│  │BLITZ     Switch to the RaspiBlitz menu            │  │
│  │REBOOT    Restart the computer                     │  │
│  │SHUTDOWN  Switch off the computer                  │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│               <a href="../menu-main/">< Select ></a>        <a href="../menu-main/">< Exit ></a>                │
└─────────────────────────────────────────────────────────┘
</div>
---

## START {#m100}

Quickstart with JoinMarket

<details>
<summary>General Explanation</summary>

This section provides a quick entry point into using JoinMarket. It allows you to set up a new wallet, view deposit addresses, start earning fees as a maker, and access the documentation via QR code. All commands here are designed for rapid setup and basic wallet operations.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| GEN | **Generate Wallet** - Creates a new wallet from scratch. Choose a secure password and store the recovery seed safely offline. This generates a fresh wallet ready for receiving Bitcoin. |
| M0 | **First Deposit Address** - Displays the first receiving address (mixdepth 0) for new funds. Use this address for your first Bitcoin deposits. Check this address periodically for incoming payments. |
| DISPLAY | **Show All Addresses** - Displays all receiving addresses across all mix depths (0-4). Mix depths are different privacy levels. This helps you see all your deposit addresses at once. |
| MAKER | **Start Yield Generator** - Launches the Yield Generator service to provide liquidity for coinjoins. In exchange, you earn fees in Satoshis. Keep your computer connected and online to earn passive income. |
| DOCS | **Documentation QR Code** - Opens a QR code that links to the JoinMarket NG documentation website. Scan with your phone to read setup guides, troubleshooting tips, and advanced features. |

---

## WALLET {#m120}

Wallet management options

<details>
<summary>General Explanation</summary>

This section contains all tools to manage your Bitcoin wallet securely. View balances, transaction history, and public keys. Generate new wallets, restore from seed, or import from another node. Use coin control features to freeze specific coins and manage UTXOs efficiently.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| DISPLAY | **Show Wallet Contents** - Displays all mix depths with their balances and addresses. See how much Bitcoin you have in each privacy level. Mix depth 0 contains your most recently generated addresses. |
| LABEL | **Add/Edit Label** - Assigns a custom name or note to a specific address. Useful for tracking who sent Bitcoin or what the funds are for. Labels help organize your wallet when addresses become unrecognizable. |
| UTXOS | **Show All Coins** - Lists all unspent transaction outputs (UTXOs) in your wallet. Each coin has a unique identifier. This helps understand wallet structure and is useful for coin control and fee optimization. |
| HISTORY | **Show Transaction History** - Displays all past transactions with incoming and outgoing Bitcoin. Shows dates, amounts, and transaction IDs. Filter to see recent or historical transfers on the blockchain. |
| XPUBS | **Show Master Public Keys** - Displays extended public keys (xpub) for all mix depths. These keys can generate receiving addresses without exposing private keys. Safe to share publicly or with backup services. |
| PSBT | **Sign PSBT** - Signs a Partially Signed Bitcoin Transaction (PSBT) file. Use this to sign transactions offline on a cold wallet or air-gapped computer for maximum security. Base64 format is used for easy copy/paste. |
| GEN | **Generate New Wallet** - Creates a brand new wallet with a fresh seed phrase. This gives you complete privacy separation from existing wallets. Use for new accounts or to reset wallet state. |
| IMPORT | **Import from Remote Node** - Copies wallet files from a remote Bitcoin node (e.g., another computer or server). Use when moving your wallet to new hardware or backing up across systems. |
| SHOWSEED | **Show Recovery Seed** - Displays your 12-24 word seed phrase. **NEVER share this with anyone!** This seed allows you to restore your wallet if you lose access. Write it down and store it safely. |
| RECOVER | **Restore from Seed** - Recreates a wallet using a 12-24 word recovery seed. Use this if you lose your wallet files or need to access funds on a new device. Double-check the seed entry is correct. |
| INCREASEGAP | **Increase Gap Limit** - Raises the number of unused addresses to scan for transactions. Default gap limit is 20 addresses. Increase this if you haven't received Bitcoin to some of your addresses yet. |
| RESCAN | **Rescan Blockchain** - Forces Bitcoin Core to re-scan the blockchain from a specific block height for wallet transactions. Use if your wallet shows missing transactions that you know are confirmed on-chain. |
| UNLOCK | **Remove Lock Files** - Deletes wallet lock files (`.lock` files) that may be stuck from a previous crash. **Only do this when Bitcoin Core is not running!** This may cause data corruption if wallet is open. |

---

## MAKER

Yield Generator options

<details>
<summary>General Explanation</summary>

The Yield Generator (YM) is JoinMarket's automated trading service that provides liquidity to the network in exchange for fees. It matches your orders with takers for coinjoins and earns Satoshis as compensation. Configure settings, monitor earnings, and control the service here.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| MAKER | **Start Yield Generator** - Launches the Yield Generator service to make offers for coinjoins. Your wallet will automatically match with takers and earn fees. Run as a system service for continuous operation. |
| JMCONF | **YM Settings in Config** - Opens the JoinMarket configuration file to adjust Yield Generator settings. Modify offer amounts, fee rates, and schedule times. Changes here affect how you participate in the network. |
| YGLIST | **Yield Generator History** - Shows a CSV log of past Yield Generator activity. Includes timestamps, counterparty names, and earnings. Review this to track your income history and network activity over time. |
| STATS | **Show Earnings in Satoshis** - Displays total Satoshis earned as a Maker from coinjoin participation. Shows lifetime earnings broken down by transaction count. Great for tracking passive income accumulation. |
| NICKNAME | **Show Last Counterparty** - Displays the username or nickname of the last person you did a coinjoin with. Helps identify regular trading partners or suspicious activity on the network. |
| SERVICE | **Service Status Monitor** - Checks if the Yield Generator service is running as a systemd service. Shows active/inactive status and uptime. Useful for troubleshooting why the service isn't working. |
| LOGS | **View Debug Logs** - Shows the latest log file from the Yield Generator service. Contains errors, warnings, and debug messages for troubleshooting. Use this when the service fails or behaves unexpectedly. |
| STOP | **Stop Yield Generator** - Gracefully stops the Yield Generator service. Use when you want to pause earning or troubleshoot issues. Can be restarted later without losing configuration settings. |
| TIMELOCK | **Create Fidelity Bond** - Generates a timelocked address for a Fidelity Bond. This commits a certain amount of Bitcoin for a set period to earn higher coinjoin fee rates. Requires locking funds temporarily. |

---

## SEND

Pay to an address with or without a coinjoin

<details>
<summary>General Explanation</summary>

Send Bitcoin from your wallet to any recipient. Configure privacy settings by adjusting maker count, transaction fees, and mix depths. Send with coinjoins for enhanced privacy or without for faster confirmation. All parameters are set interactively before sending.
</details>

| Parameter | User-Friendly Explanation |
|-----------|---------------------------|
| mixdepth | **Choose Send From** - Select which mix depth (0-4) to send coins from. Lower numbers contain newer addresses with higher privacy. Use different mix depths for different transaction types. |
| amount | **Enter Amount in Satoshis** - Specify how much Bitcoin to send in satoshis (1 BTC = 100,000,000 sats). Enter 0 to send entire mix depth balance. Double-check the amount before confirming. |
| makercount | **Coinjoin Participation** - Choose how many makers to include in the coinjoin. Higher numbers mean more privacy but slower confirmation. 0 sends without coinjoin (faster but less private). Recommended: 5-9 for balance. |
| txfee | **Miner Fee in Sat/Byte** - Set the transaction fee paid to miners for confirmation. Higher fees = faster confirmation. Typical range: 1-10 sat/byte depending on network congestion. |
| address | **Recipient Bitcoin Address** - Enter the destination Bitcoin address for the transaction. Verify the address carefully before sending to avoid lost funds. Supports mainnet addresses (bc1, 1, or 3 prefix). |
| changeAddress | **Optional Change Address** - Provide a custom address for any leftover change (if sending partial amount). If empty, change goes back to wallet automatically. Useful for batch processing to multiple addresses. |

---

## FREEZE

Exercise coin control within a mixdepth

<details>
<summary>General Explanation</summary>

Coin control allows you to freeze specific UTXOs (coins) so they won't be automatically selected for future transactions. This gives you full control over which coins are spent and when, useful for privacy planning and fee management.
</details>

| Parameter | User-Friendly Explanation |
|-----------|---------------------------|
| mixdepth | **Choose Mix Depth** - Select which mix depth (0-4) to freeze coins in. Each mix depth has its own set of coins. Freeze only coins in specific privacy levels while leaving others available for sending. |

---

## PAYJOIN

Send/Receive between JoinMarket wallets

<details>
<summary>General Explanation</summary>

PayJoin is a privacy technology where the receiver contributes coins to the transaction, making it look like a regular payment rather than a coinjoin. Send payments or receive funds with enhanced privacy through this protocol. Both parties need JoinMarket wallets.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| SEND | **Send with PayJoin** - Send Bitcoin to another JoinMarket wallet using PayJoin protocol. The receiver's coins are combined, improving privacy for both parties. Requires recipient wallet to support PayJoin. |
| RECEIVE | **Receive with PayJoin** - Accept incoming Bitcoin payments via PayJoin. When someone sends to you, your wallet contributes coins to make the transaction look like a regular payment. Enhances incoming transaction privacy. |

---

## OFFERS

Watch the Order Book locally

<details>
<summary>General Explanation</summary>

The Order Book shows all active coinjoin offers from other users on the network. Watch locally to see what offers are available, who is participating, and current fee rates. Run as a background service to monitor the network in real-time.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| START | **Start Order Book Watch** - Launches a local process to watch the JoinMarket Order Book. Connects to network peers and displays active coinjoin offers in real-time. Runs as a background service. |
| SHOW | **Show Order Book Address** - Displays your local Order Book .onion address for the Tor network. Others can connect to your node to see what you're offering or trading with. Share carefully as it exposes your node. |
| STOP | **Stop Background Process** - Terminates the Order Book watcher service. Use when you no longer need to monitor offers or to free up system resources. Can be restarted anytime without configuration loss. |

---

## CONFIG

Connection and joinmarket.cfg settings

<details>
<summary>General Explanation</summary>

Configure all connection settings for Bitcoin Core and JoinMarket. Connect to local or remote Bitcoin nodes, edit configuration files, or switch network modes. These settings determine how your wallet communicates with the blockchain and network.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| JMCONF | **Edit JoinMarket Config** - Opens the main JoinMarket configuration file for manual editing. Customize wallet paths, network settings, and protocol options. Changes require restarting services to take effect. |
| CONNECT | **Connect Remote Node** - Configure connection to a remote Bitcoin Core node on mainnet. Enter RPC credentials, IP or .onion address, and port. Required if your Bitcoin node runs on a different computer or server. |
| SIGNET | **Switch to Signet Network** - Configures JoinMarket to use the Bitcoin Signet test network instead of mainnet. Use for testing without risking real Bitcoin. Switches back to mainnet for real transactions. |
| LOCAL | **Connect Local Bitcoin Core** - Connects to the Bitcoin Core node running on the same computer. Uses local file paths and default ports (8332). Fastest connection with lowest latency. |
| BTCCONF | **Edit Bitcoin Config** - Opens the Bitcoin Core configuration file for manual editing. Adjust mining settings, RPC credentials, pruning options, and network parameters. Affects how Bitcoin Core operates. |
| RESET | **Reset JoinMarket Config** - Deletes and recreates the joinmarket.cfg file with default values. Use this if your configuration is broken or corrupted. You'll need to re-enter all custom settings afterward. |

---

## TOOLS

Extra helper functions and services

<details>
<summary>General Explanation</summary>

This section contains utility tools and services that support the main JoinMarket functionality. Generate QR codes, run custom RPC commands, scan for coinjoins, or manage system services. Use these tools for maintenance, debugging, and advanced operations.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| QR | **Generate QR Code** - Converts any text or data into a scannable QR code. Use to create wallet addresses, payment requests, or documentation links. Great for sharing sensitive information securely. |
| CUSTOMRPC | **Run Custom RPC Command** - Execute any Bitcoin Core RPC command using curl. Advanced users can query blockchain data directly. Useful for debugging and advanced blockchain analysis. |
| CJFINDER | **Find Coinjoin Transactions** - Scans recent blocks for JoinMarket coinjoin transactions. Lists detected coinjoins with addresses and amounts. Useful for research and network analysis. |
| CHECKTXN | **Transaction Explorer** - CLI tool to explore any Bitcoin transaction on the blockchain. Enter a transaction ID to see inputs, outputs, and confirmation details. No web browser required for transaction lookup. |
| PASSWORD | **Change SSH Password** - Changes your system SSH login password. Use this to improve account security on the RaspiBlitz system. Choose a strong, memorable password for account protection. |
| SSH | **Enable SSH Access** - Turns SSH access on or off for the joinmarket user. Enable this to access the system remotely via SSH client. Disable for improved security if remote access is not needed. |
| LOGS | **View Bitcoin Core Logs** - Displays the latest bitcoind log files on mainnet. Shows blockchain sync status, peer connections, and any errors. Essential for troubleshooting node issues. |
| API | **Start Wallet API Service** - Launches jmwalletd.py as a systemd service for API access. Required for third-party wallet integrations and external tools. Runs automatically with system startup. |
| FULLYNODED | **Connect Fully Noded** - Provides a QR code to connect Fully Noded hardware wallet. Scan with your Noded device to establish secure connection. Used for high-security cold wallet integration. |

---

## UPDATE

Update JoininBox or JoinMarket

<details>
<summary>General Explanation</summary>

Keep your JoinMarket installation up to date with the latest security patches and features. Update the JoininBox scripts themselves, the JoinMarket software, or access advanced options like testing pull requests and custom versions.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| JOININBOX | **Update JoininBox Scripts** - Updates all JoininBox menu scripts and interface to the latest version. Ensures you have the newest features and bug fixes. Recommended to run regularly. |
| JOINMARKET | **Update JoinMarket Software** - Reinstalls JoinMarket to the latest official commit from GitHub. Gets the newest JoinMarket features and security updates. Run after major releases for optimal performance. |
| ADVANCED | **Advanced Update Options** - Opens menu with deeper update controls. Test new features, install custom versions, or update Tor. Use with caution and only if you understand the implications. |

### Advanced Update Options

| Option | User-Friendly Explanation |
|--------|---------------------------|
| JBCOMMIT | **Update JoininBox Commit** - Updates JoininBox to the latest git commit hash. Includes pre-release features that haven't been officially released yet. May contain bugs. |
| JBPR | **Test JoininBox Pull Request** - Tests a specific Pull Request on JoininBox. Use this to preview upcoming features before official release. Not recommended for production use. |
| JBRESET | **Reset JoininBox Installation** - Completely reinstalls JoininBox scripts from scratch. Use if the installation is corrupted or you want a fresh start. All settings will be reset to defaults. |
| JMCUSTOM | **Update JoinMarket Custom Version** - Install a custom or modified version of JoinMarket. Use this for development, testing, or specialized builds. Not the official release version. |
| JMPR | **Test JoinMarket Pull Request** - Tests a specific Pull Request on JoinMarket software. Preview upcoming JoinMarket features and improvements. Use for development or evaluation purposes only. |
| JMCOMMIT | **Update JoinMarket Commit** - Updates JoinMarket to the latest git commit hash. Contains the newest code from the repository. May be unstable if features are not fully tested. |
| TOR | **Update Tor to Alpha** - Updates the Tor proxy to the latest alpha version. Latest Tor versions offer better privacy and censorship resistance. Alpha versions may have bugs. |

---

## BLITZ

Switch to the RaspiBlitz menu

<details>
<summary>General Explanation</summary>

Switches from JoinMarket to the RaspiBlitz administration menu. This is only available when using JoininBox on a RaspiBlitz Bitcoin node. Provides full control over your RaspiBlitz system and services.
</details>

| Option | User-Friendly Explanation |
|--------|---------------------------|
| BLITZ | **Switch to RaspiBlitz Menu** - Exits JoininBox and switches to the RaspiBlitz administration interface. Use this to configure your RaspiBlitz node, check system status, or access advanced features. |

---

## Summary

| Menu | Number of Options |
|------|-------------------|
| START | 5 |
| WALLET | 13 |
| MAKER | 9 |
| SEND | 1 (Parameter Dialog) |
| FREEZE | 1 (Parameter Dialog) |
| PAYJOIN | 2 |
| OFFERS | 3 |
| CONFIG | 6 |
| TOOLS | 9 |
| UPDATE | 3 + 7 (Advanced) |
| BLITZ | 1 |
| TOTAL | 53+ Items |

---

## Notes

- **Privacy**: Always use coinjoins for maximum privacy when sending Bitcoin
- **Backup**: Store your seed phrase offline and never share with anyone
- **Updates**: Regularly update JoininBox and JoinMarket for security
- **Testing**: Use Signet network for testing before mainnet transactions

