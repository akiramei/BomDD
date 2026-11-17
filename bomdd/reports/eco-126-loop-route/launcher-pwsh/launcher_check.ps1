# Confirms the repaired launcher from the shell that runs it. usage: pwsh -File launcher_check.ps1 <path to handover-stamp.py> <scratch root>
param([string]$Tool, [string]$Root)
$env:PYTHONIOENCODING = 'utf-8'
$env:HANDOVER_NO_START = '1'
"shell: PowerShell $($PSVersionTable.PSVersion)"
"tool sha256: $((Get-FileHash -Algorithm SHA256 -LiteralPath $Tool).Hash.ToLower())"

"--- 1. selftest"
python $Tool --selftest
"selftest exit=$LASTEXITCODE"

"--- 2. a folder with a space and non-ASCII characters in its path; launcher started through cmd"
$d = Join-Path $Root ('hs fix 確認-' + [guid]::NewGuid().ToString('N').Substring(0, 6))
New-Item -ItemType Directory $d | Out-Null
[IO.File]::WriteAllBytes("$d\main.bin", [Text.Encoding]::ASCII.GetBytes('build one'))
[IO.File]::WriteAllText("$d\prog.cmd", "@exit /b 0`r`n", [Text.Encoding]::ASCII)
python $Tool stamp --dir $d --program prog.cmd --file main.bin --label check | Out-Null
"stamp exit=$LASTEXITCODE"
$err = cmd /c "`"$d\launch.cmd`"" 2>&1
"launcher exit=$LASTEXITCODE; launcher output lines: $(@($err).Count)"
$want = (Get-Content "$d\handover.json" -Raw -Encoding utf8 | ConvertFrom-Json).files.'main.bin'
$line = @(Get-Content "$d\launch-log.tsv")[-1]
$got = ($line -split "`t")[3]
"log hash == stamped hash: $($got -eq $want) ($($got.Substring(0, [Math]::Min(16, $got.Length)))…)"
python $Tool check --dir $d | Select-Object -Last 1
"check exit=$LASTEXITCODE"

"--- 3. the main file is gone at launch: nothing printed, the line says unreadable"
Remove-Item "$d\main.bin"
$err = cmd /c "`"$d\launch.cmd`"" 2>&1
"launcher exit=$LASTEXITCODE; launcher output lines: $(@($err).Count)"
$line = @(Get-Content "$d\launch-log.tsv")[-1]
"last field: $(($line -split "`t")[3])"
python $Tool check --dir $d | Select-Object -Last 1
"check exit=$LASTEXITCODE"

"--- 4. the same expression under a constrained language mode (Windows PowerShell 5.1 through cmd)"
[IO.File]::WriteAllBytes("$d\main.bin", [Text.Encoding]::ASCII.GetBytes('build one'))
$env:D = "$d\"
$expr = '$ExecutionContext.SessionState.LanguageMode=''ConstrainedLanguage'';try{$s=[IO.File]::OpenRead($env:D+''main.bin'');try{[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($s)).Replace(''-'','''').ToLower()}finally{$s.Dispose()}}catch{}'
$out = cmd /c "powershell -NoProfile -Command `"$expr`"" 2>&1
"constrained: output lines: $(@($out).Count); text: $(@($out) -join ' | ')"
"folder: $d"
