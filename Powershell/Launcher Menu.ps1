# LauncherMenu.ps1

$shortcutDir = "PATH/TO/FILE"

# ─────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────

function Open-Shortcut($name) {
    $path = Join-Path $shortcutDir "$name.lnk"
    if (Test-Path $path) {
        Start-Process -FilePath $path
        Write-Host "$name launched." -ForegroundColor Green
        Start-Sleep -Seconds 1
        exit
    } else {
        Write-Host "Could not find: $path" -ForegroundColor Red
        Write-Host ""
        Write-Host "Press any key to return to the menu..." -ForegroundColor DarkGray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

function Show-GameLaunchers {
    do {
        Clear-Host
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host "       GAME LAUNCHERS          " -ForegroundColor White
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host " 1. Playnite"
        Write-Host " 2. Itch.io"
        Write-Host " 3. Minecraft"
        Write-Host " 4. Rockstar Games Launcher"
        Write-Host " 5. Ubisoft Connect"
        Write-Host " 6. RohanKar Launcher"
        Write-Host " 7. Back"
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host ""
        $choice = Read-Host "Select an option (1-7)"

        switch ($choice) {
            "1" { Open-Shortcut "Playnite" }
            "2" { Open-Shortcut "Itch.io" }
            "3" { Open-Shortcut "Minecraft" }
            "4" { Open-Shortcut "Rockstar Games Launcher" }
            "5" { Open-Shortcut "Ubisoft Connect" }
            "6" { Open-Shortcut "RohanKar Launcher" }
            "7" { return }
            default { Write-Host "Invalid option. Please enter 1-7." -ForegroundColor Red }
        }

        if ($choice -ne "7") {
            Write-Host ""
            Write-Host "Press any key to return to the menu..." -ForegroundColor DarkGray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }

    } while ($true)
}

function Show-ModLaunchers {
    do {
        Clear-Host
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host "        MOD LAUNCHERS          " -ForegroundColor White
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host " 1. CurseForge"
        Write-Host " 2. Modrinth"
        Write-Host " 3. Thunderstore Mod Manager"
        Write-Host " 4. r2modman"
        Write-Host " 5. Vortex"
        Write-Host " 6. SKlauncher (Minecraft)"
        Write-Host " 7. BG3 Mod Manager"
        Write-Host " 8. RedModManager"
        Write-Host " 9. Back"
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host ""
        $choice = Read-Host "Select an option (1-9)"

        switch ($choice) {
            "1" { Open-Shortcut "CurseForge" }
            "2" { Open-Shortcut "Modrinth App" }
            "3" { Open-Shortcut "Thunderstore Mod Manager" }
            "4" { Open-Shortcut "r2modman" }
            "5" { Open-Shortcut "Vortex" }
            "6" { Open-Shortcut "SKlauncher" }
            "7" { Open-Shortcut "BG3ModManager" }
            "8" { Open-Shortcut "RedModManager" }
            "9" { return }
            default { Write-Host "Invalid option. Please enter 1-9." -ForegroundColor Red }
        }

        if ($choice -ne "9") {
            Write-Host ""
            Write-Host "Press any key to return to the menu..." -ForegroundColor DarkGray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }

    } while ($true)
}

function Show-Emulators {
    do {
        Clear-Host
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host "          EMULATORS            " -ForegroundColor White
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host " (No emulators added yet)"
        Write-Host ""
        Write-Host " 1. Back"
        Write-Host "===============================" -ForegroundColor DarkCyan
        Write-Host ""
        $choice = Read-Host "Select an option (1)"

        switch ($choice) {
            "1" { return }
            default { Write-Host "Invalid option." -ForegroundColor Red }
        }

        if ($choice -ne "1") {
            Write-Host ""
            Write-Host "Press any key to return to the menu..." -ForegroundColor DarkGray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }

    } while ($true)
}

# ─────────────────────────────────────────────
# MAIN MENU LOOP
# ─────────────────────────────────────────────

do {
    Clear-Host
    Write-Host "===============================" -ForegroundColor DarkCyan
    Write-Host "       LAUNCHER MENU           " -ForegroundColor White
    Write-Host "===============================" -ForegroundColor DarkCyan
    Write-Host " 1. Game Launchers"
    Write-Host " 2. Mod Launchers"
    Write-Host " 3. Emulators"
    Write-Host " 4. Exit"
    Write-Host "===============================" -ForegroundColor DarkCyan
    Write-Host ""
    $choice = Read-Host "Select an option (1-4)"

    switch ($choice) {
        "1" { Show-GameLaunchers }
        "2" { Show-ModLaunchers }
        "3" { Show-Emulators }
        "4" { Write-Host "Goodbye." -ForegroundColor DarkGray; exit }
        default { Write-Host "Invalid option. Please enter 1-4." -ForegroundColor Red }
    }

} while ($true)
