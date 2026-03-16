# Bazzite App Installer

Vibecoded with Claude. Built for my personal Bazzite setup. Not intended for anyone else — if you run it and something breaks, that's on you.

---

## What It Does

A Bash script that automates app installation on Bazzite via Flatpak/Flathub. It handles dependencies, sets up permissions, installs alternatives for Windows-only apps, and prints a full remediation report at the end showing what failed and what still needs manual action.

---

## Dependencies

Layered via `rpm-ostree` (reboot required after):

- `cabextract` — Wine/Bottles needs this for Windows `.cab` installers
- `p7zip` + `p7zip-plugins` — archive extraction for Windows app installers
- `usbutils` — USB capture support for Wireshark
- `v4l-utils` — video device detection for GPU Screen Recorder

Flatpak runtimes installed for Wine/Bottles:

- `org.freedesktop.Platform//23.08`
- `org.freedesktop.Platform.Compat.i386//23.08`
- `org.freedesktop.Platform.GL32.default//23.08`
- `org.freedesktop.Platform.VAAPI.Intel//23.08`
- `org.winehq.Wine.DLLs.dxvk//stable-23.08`

---

## Apps Installed

| App | Flatpak ID |
|-----|-----------|
| Floorp Browser | `one.ablaze.floorp` |
| Waterfox | `net.waterfox.waterfox` |
| Google Chrome | `com.google.Chrome` |
| Steam | `com.valvesoftware.Steam` |
| Bottles | `com.usebottles.bottles` |
| Flatseal | `com.github.tchx84.Flatseal` |
| Surfshark VPN | `com.surfshark.Surfshark` |
| Discord | `com.discordapp.Discord` |
| Vesktop | `dev.vencord.Vesktop` |
| Spotify | `com.spotify.Client` |
| VSCodium | `com.vscodium.codium` |
| Wireshark | `org.wireshark.Wireshark` |
| itch.io | `io.itch.itch` |
| ATLauncher | `com.atlauncher.ATLauncher` |
| Modrinth App | `com.modrinth.ModrinthApp` |
| r2modman | `com.github.ebkr.r2modman` |
| Limo | `io.github.limo_app.limo` |
| MangoHud Vulkan Layer | `org.freedesktop.Platform.VulkanLayer.MangoHud` |
| GOverlay | `page.codeberg.Heldek.GOverlay` |
| Flameshot | `org.flameshot.Flameshot` |
| GPU Screen Recorder | `com.dec05eba.gpu_screen_recorder` |

---

## Apps That Can't Auto-Install

| App | Reason | What Happens Instead |
|-----|--------|---------------------|
| Playnite | Windows-only | Run via Bottles — guide printed at end |
| Rockstar Games Launcher | Windows-only | Run via Bottles — guide printed at end |
| BG3 Mod Manager | Windows .NET app | Run via Bottles — guide printed at end |
| VeraCrypt | Not on Flathub, FUSE issues on Bazzite | Manual install — guide printed at end |
| Cisco Packet Tracer | Requires NetAcad account | Manual install — guide printed at end |
| Surfshark Kill Switch | Flatpak sandbox limitation | Native .rpm guide printed at end |
| CurseForge | No Linux client | ATLauncher installed instead |
| Vortex | Windows-only | Limo installed instead |
| Thunderstore App | Windows-only (Overwolf) | r2modman installed instead |
| REDmod | Windows-only | r2modman handles Cyberpunk mods via Proton |
| Medal.tv | No Linux support | GPU Screen Recorder installed instead |
| ShareX | Windows-only | Flameshot installed instead |
| Borderless Gaming | Windows-only | Gamescope handles this natively on Bazzite |
| Core Temp / HWiNFO64 | Windows-only | MangoHud + GOverlay installed instead |

---

## Usage

```bash
chmod +x Installer.sh
./Installer.sh
```

Requires `sudo` for `rpm-ostree` steps. A reboot is needed after the script runs for system-level changes to take effect.

---

## Warning

This is for **my** Bazzite install. Running it on anything else is unsupported and untested. You've been warned.
