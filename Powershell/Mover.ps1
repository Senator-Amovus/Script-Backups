# =============================================================================
# CONFIGURATION SECTION
# Define your source and destination folder pairs below.
# Source: where to read files FROM
# Destination: where to put files TO
# =============================================================================

$FolderMappings = @(
    @{
        Source      = "C:\Path\To\Folder1"
        Destination = "C:\Path\To\Output1"
    },
    @{
        Source      = "C:\Path\To\Folder2"
        Destination = "C:\Path\To\Output2"
    },
    @{
        Source      = "C:\Path\To\Folder3"
        Destination = "C:\Path\To\Output3"
    },
    @{
        Source      = "C:\Path\To\Folder4"
        Destination = "C:\Path\To\Output4"
    }
)

# =============================================================================
# OPTIONS
# =============================================================================

# If $true, mirror subfolders in the destination. If $false, flatten everything.
$PreserveSubfolders = $true

# If $true, print what would happen without actually doing anything.
$DryRun = $false

# =============================================================================
# SCRIPT - Do not edit below unless you know what you're doing
# =============================================================================

Add-Type -AssemblyName System.Drawing

function Convert-JpgToPng {
    param (
        [string]$SourceFile,
        [string]$DestFile
    )

    try {
        $img = [System.Drawing.Image]::FromFile($SourceFile)
        $img.Save($DestFile, [System.Drawing.Imaging.ImageFormat]::Png)
        $img.Dispose()
        return $true
    } catch {
        Write-Warning "  Failed to convert: $SourceFile`n  Error: $_"
        return $false
    }
}

function Get-DestinationPath {
    param (
        [string]$SourceFile,
        [string]$SourceRoot,
        [string]$DestRoot,
        [string]$NewExtension = $null
    )

    if ($PreserveSubfolders) {
        $relative = [System.IO.Path]::GetRelativePath($SourceRoot, $SourceFile)
    } else {
        $relative = [System.IO.Path]::GetFileName($SourceFile)
    }

    if ($NewExtension) {
        $relative = [System.IO.Path]::ChangeExtension($relative, $NewExtension)
    }

    return [System.IO.Path]::Combine($DestRoot, $relative)
}

# ------- Main Loop -------

$totalConverted = 0
$totalMoved     = 0
$totalSkipped   = 0
$totalErrors    = 0

foreach ($mapping in $FolderMappings) {
    $src  = $mapping.Source
    $dest = $mapping.Destination

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Source      : $src" -ForegroundColor Cyan
    Write-Host "Destination : $dest" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    if (-not (Test-Path $src)) {
        Write-Warning "Source folder not found, skipping: $src"
        continue
    }

    if (-not $DryRun -and -not (Test-Path $dest)) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
        Write-Host "  Created destination folder: $dest"
    }

    $files = Get-ChildItem -Path $src -File -Recurse

    foreach ($file in $files) {
        $ext = $file.Extension.ToLower()

        $destPath = Get-DestinationPath `
            -SourceFile $file.FullName `
            -SourceRoot $src `
            -DestRoot   $dest `
            -NewExtension ($ext -eq ".jpg" -or $ext -eq ".jpeg" ? ".png" : $null)

        # Ensure destination subfolder exists
        $destDir = [System.IO.Path]::GetDirectoryName($destPath)
        if (-not $DryRun -and -not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        # --- JPG / JPEG: Convert to PNG ---
        if ($ext -eq ".jpg" -or $ext -eq ".jpeg") {
            Write-Host "  [CONVERT] $($file.Name) -> $([System.IO.Path]::GetFileName($destPath))"

            if (-not $DryRun) {
                $ok = Convert-JpgToPng -SourceFile $file.FullName -DestFile $destPath
                if ($ok) { $totalConverted++ } else { $totalErrors++ }
            } else {
                $totalConverted++
            }

        # --- Everything else: Move as-is ---
        } else {
            $label = if ($ext -eq ".png") { "[PNG→MOVE]" } else { "[MOVE]    " }
            Write-Host "  $label $($file.Name)"

            if (-not $DryRun) {
                try {
                    Copy-Item -Path $file.FullName -Destination $destPath -Force
                    $totalMoved++
                } catch {
                    Write-Warning "  Failed to move: $($file.FullName)`n  Error: $_"
                    $totalErrors++
                }
            } else {
                $totalMoved++
            }
        }
    }
}

# ------- Summary -------
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  DONE$(if ($DryRun) { ' (DRY RUN - no changes made)' })" -ForegroundColor Green
Write-Host "  Converted (JPG→PNG) : $totalConverted" -ForegroundColor Green
Write-Host "  Moved (as-is)       : $totalMoved" -ForegroundColor Green
Write-Host "  Errors              : $totalErrors" -ForegroundColor $(if ($totalErrors -gt 0) { "Red" } else { "Green" })
Write-Host "========================================" -ForegroundColor Green
