# Installation

## Platform Support

JoininBox runs on:

| Platform | Description |
|----------|-------------|
| **RaspiBlitz** | Pre-installed, ready to use |
| **Standalone** | Manual installation on any Linux system |

## RaspiBlitz

JoininBox comes pre-installed on RaspiBlitz. Access it by switching to the joinmarket user:

```bash
sudo su - joinmarket
```

Or via SSH:

```bash
ssh joinmarket@<LAN_IP>
```

Password: Use the password set during RaspiBlitz setup (typically stored in the RaspiBlitz settings).

## Standalone Installation

### Requirements

| Requirement | Description |
|-------------|-------------|
| Operating System | Linux (Debian/Ubuntu recommended) |
| Bitcoin Core | Local or remote node with RPC access |
| Python | Version 3.8 or higher |
| Tor | Optional but recommended for privacy |

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/openoms/joininbox.git
cd joininbox

# Run the installation script
./install.sh
```

The installation script will:

1. Install required dependencies
2. Set up the joinmarket user
3. Clone and build JoinMarket
4. Configure Tor hidden services (optional)
5. Create the joinin.conf configuration file

### Post-Installation

After installation completes:

1. **Connect to Bitcoin Core**

   ```bash
   menu
   # Navigate to: CONFIG → CONNECT (for remote node)
   # or CONFIG → LOCAL (for local node)
   ```

2. **Generate Configuration**

   The `joinmarket.cfg` is generated automatically with default settings.

3. **Create Your First Wallet**

   ```bash
   # Navigate to: WALLET → GEN
   ```

## Network Configuration

### Mainnet (Default)

Production use with real Bitcoin. Requires a fully synced Bitcoin Core node.

### Signet

Testing network with play money. Useful for learning without risk.

```
# Navigate to: CONFIG → SIGNET
```

### Testnet

Development and testing network.

## Tor Configuration

JoininBox can route all traffic through Tor for enhanced privacy.

### Enable Tor

Edit `~/joinin.conf`:

```bash
runBehindTor=on
RPCoverTor=on
```

### Hidden Services

JoininBox can create Tor hidden services for:

| Service | Port | Description |
|---------|------|-------------|
| Order Book | 62601 | Local order book monitoring |
| jmwalletd API | 28183 | Wallet API access |

## First Steps After Installation

| Step | Menu Path | Description |
|------|-----------|-------------|
| 1 | START → GEN | Create a new wallet |
| 2 | START → m0 | Display deposit address with QR code |
| 3 | Fund wallet | Send Bitcoin to the displayed address |
| 4 | WALLET → DISPLAY | Verify funds arrived |
| 5 | MAKER → MAKER | Start earning as liquidity provider |

## Configuration Files

| File | Path | Description |
|------|------|-------------|
| `joinmarket.cfg` | `~/.joinmarket/joinmarket.cfg` | Main JoinMarket configuration |
| `joinin.conf` | `~/joinin.conf` | JoininBox settings |
| Wallets | `~/.joinmarket/wallets/` | Wallet files (`.jmdat`) |
| Logs | `~/.joinmarket/logs/` | Log files |

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Wallet lockfile exists | WALLET → UNLOCK to remove lockfiles |
| RPC connection failed | Check Bitcoin Core RPC settings in CONFIG |
| Tor not working | `sudo systemctl status tor` |
| Yield Generator not starting | Check logs in `~/.joinmarket/logs/` |
| Permission denied | Ensure you are running as `joinmarket` user |

### Reset Configuration

To reset `joinmarket.cfg` to defaults:

```
CONFIG → RESET
```

### View Logs

```bash
# JoinMarket logs
ls -la ~/.joinmarket/logs/

# Yield Generator logs (newest first)
ls -t ~/.joinmarket/logs/ | grep J5 | head -n 1

# Bitcoin Core logs
menu → TOOLS → LOGS
```

## Security Recommendations

1. **Backup your seed** - Store the wallet recovery seed securely offline
2. **Use Tor** - Route all traffic through Tor for privacy
3. **Strong passwords** - Use unique, strong passwords for SSH and wallet
4. **Regular updates** - Keep JoininBox and JoinMarket updated
5. **Limited access** - Restrict SSH access to trusted IPs if possible

## Related Resources

- [JoininBox GitHub Repository](https://github.com/openoms/joininbox)
- [RaspiBlitz Documentation](https://github.com/rootzoll/raspiblitz)
- [JoinMarket Documentation](https://github.com/JoinMarket-Org/joinmarket-clientserver/blob/master/docs/USAGE.md)
