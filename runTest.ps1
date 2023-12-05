[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$firstPlayerType = "random_player_abalone.py"
$secondPlayerType = "random_player_abalone.py"
$iterationCount = 10

for ($i=0; $i -lt $iterationCount; $i++) {
    python main_abalone.py -t local $firstPlayerType $secondPlayerType
    Write-Host "Iteration $i complete."
}

Write-Host "Script completed."