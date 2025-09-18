# File: test_tts.ps1
# Base URL of your backend
$BASE_URL = "https://saathi-backend-1cny.onrender.com"

# Fetch all posts
Write-Host "Fetching all posts..."
$posts = Invoke-RestMethod -Uri "$BASE_URL/posts"

if ($posts.Count -eq 0) {
    Write-Host "No posts found."
    exit
}

# List posts with index
Write-Host "Available posts:"
for ($i=0; $i -lt $posts.Count; $i++) {
    Write-Host "[$i] $($posts[$i].description_brief) (ID: $($posts[$i].id))"
}

# Ask user to choose a post
$choice = Read-Host "Enter the index of the post to play TTS"

if (-not ($choice -as [int]) -or $choice -lt 0 -or $choice -ge $posts.Count) {
    Write-Host "Invalid choice."
    exit
}

$postID = $posts[$choice].id
$brief = $posts[$choice].description_brief
Write-Host "Playing TTS for: $brief"

# Download the audio to a temporary file
$tempFile = "$env:TEMP\tts_audio.mp3"
Invoke-WebRequest -Uri "$BASE_URL/tts/post/$postID" -OutFile $tempFile

# Play audio using Windows Media Player COM object
$player = New-Object -ComObject WMPlayer.OCX
$media = $player.newMedia($tempFile)
$player.currentPlaylist.appendItem($media)
$player.controls.play()

# Wait until playback finishes
while ($player.playState -ne 1) { Start-Sleep -Milliseconds 500 }

# Cleanup
Remove-Item $tempFile
