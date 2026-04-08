Add-Type -AssemblyName Microsoft.VisualBasic

# Change the folder directories for where you have Medal saved
$folders = @(
    "D:\Medal\.Thumbnails",
    "D:\Medal\Clips",
    "D:\Medal\Edits",
    "D:\Medal\editor\render"
)

foreach ($folder in $folders) {
    if (Test-Path $folder) {

        Write-Host "Cleaning $folder"

        # Delete all files (to Recycle Bin)
        Get-ChildItem $folder -Recurse -Force -File | ForEach-Object {
            [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile(
                $_.FullName,
                'OnlyErrorDialogs',
                'SendToRecycleBin'
            )
        }

        # Delete all subfolders (to Recycle Bin)
        Get-ChildItem $folder -Recurse -Force -Directory | ForEach-Object {
            [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory(
                $_.FullName,
                'OnlyErrorDialogs',
                'SendToRecycleBin'
            )
        }
    }
}

Write-Host "Clearing Recycle Bin..."

# Empty the Recycle Bin (no prompt)
# "0x0007" means: no confirmation, no progress UI, no sound
# This permanently deletes everything currently in the Recycle Bin
(New-Object -ComObject Shell.Application).NameSpace(0xA).Items() |
    ForEach-Object { Remove-Item $_.Path -Recurse -Force -ErrorAction SilentlyContinue }

Write-Host "All Medal folders cleaned and Recycle Bin emptied."
Start-Sleep -Seconds 2
