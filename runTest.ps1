[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$firstPlayerType = "bot.py"
$secondPlayerType = "bot.py"
$iterationCount = 1
$white_id_interval = 1,3
$black_id_interval = 1,3
$name = "tester1"


for ($w = $white_id_interval[0]; $w -le $white_id_interval[1]; $w++) {
    for ($b = $black_id_interval[0]; $b -le $black_id_interval[1]; $b++) {
        if ($w -eq $b) {
            continue  # Skip the iteration if both IDs are the same
        }
        for ($i = $0; $i -le $iterationCount; $i++) {
            python main_abalone.py -t local $firstPlayerType $secondPlayerType -g -w $w -b $b -name $name
            Write-Host "Game complete for White ID $w and Black ID $b."
        }
    }
}


Write-Host "Script completed."

