if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")) {
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

$odtUrl = "https://download.microsoft.com/download/2/7/A/27AF1BE6-DD20-4CB4-B154-EBAB8A7D4A7E/officedeploymenttool_18129-20158.exe"
$odtPath = "$env:TEMP\odt.exe"
$configPath = "$env:TEMP\config.xml"

Invoke-WebRequest -Uri $odtUrl -OutFile $odtPath

@"
<Configuration>
  <Add OfficeClientEdition="64" Channel="Current">
    <Product ID="O365BusinessRetail">
      <Language ID="en-us"/>
      <ExcludeApp ID="Access"/>
      <ExcludeApp ID="Groove"/>
      <ExcludeApp ID="InfoPath"/>
      <ExcludeApp ID="Lync"/>
      <ExcludeApp ID="OneDrive"/>
      <ExcludeApp ID="OneNote"/>
      <ExcludeApp ID="Outlook"/>
      <ExcludeApp ID="Publisher"/>
      <ExcludeApp ID="Teams"/>
    </Product>
  </Add>
</Configuration>
"@ | Out-File -FilePath $configPath -Encoding UTF8

Start-Process -FilePath $odtPath -ArgumentList "/quiet /extract:$env:TEMP\odt" -Wait
Start-Process -FilePath "$env:TEMP\odt\setup.exe" -ArgumentList "/configure $configPath" -Wait