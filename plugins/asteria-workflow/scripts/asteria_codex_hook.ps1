param(
    [string]$Event = "Unknown"
)

$repoRoot = "H:\Asteria"
$python = "H:\Asteria\.venv\Scripts\python.exe"
$script = Join-Path $repoRoot "scripts\governance\check_asteria_workflow.py"

if (-not (Test-Path -LiteralPath $python)) {
    Write-Output "Asteria workflow hook: repo virtualenv not found; use A1 Align before edits."
    exit 0
}

if (-not (Test-Path -LiteralPath $script)) {
    Write-Output "Asteria workflow hook: workflow checker missing; use A1-A6 manually."
    exit 0
}

& $python $script --repo-root $repoRoot --hook-event $Event
exit 0
