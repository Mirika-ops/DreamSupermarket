#!/usr/bin/env pwsh
<#
.SYNOPSIS
Monitor PNG to MP4 conversion progress
#>

$videosPath = 'f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\videos'
$targetCount = 20
$checkInterval = 10  # seconds

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🎬 PNG转MP4转换监控 - Conversion Monitor" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "目标: 完成 $targetCount 个MP4视频" -ForegroundColor Yellow
Write-Host "检查间隔: $checkInterval 秒" -ForegroundColor Yellow
Write-Host "开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host ""

$startTime = Get-Date
$isComplete = $false

while (-not $isComplete) {
    $mp4Files = @(Get-ChildItem -Path $videosPath -Filter '*.mp4' -File -ErrorAction SilentlyContinue)
    $mp4Count = @($mp4Files).Count
    
    # Calculate elapsed time
    $elapsed = (Get-Date) - $startTime
    $elapsedStr = "{0:D2}:{1:D2}:{2:D2}" -f [int]$elapsed.TotalHours, [int]$elapsed.Minutes, [int]$elapsed.Seconds
    
    # Calculate estimated time remaining
    if ($mp4Count -gt 0) {
        $timePerVideo = $elapsed.TotalSeconds / $mp4Count
        $remainingVideos = $targetCount - $mp4Count
        $estimatedSecondsRemaining = $timePerVideo * $remainingVideos
        $estimatedTimeRemaining = New-TimeSpan -Seconds $estimatedSecondsRemaining
        $estimatedStr = "{0:D2}:{1:D2}:{2:D2}" -f [int]$estimatedTimeRemaining.TotalHours, [int]$estimatedTimeRemaining.Minutes, [int]$estimatedTimeRemaining.Seconds
    } else {
        $estimatedStr = "处理中..."
    }
    
    # Display progress bar
    $progressBar = ""
    $filledBlocks = [int]($mp4Count / $targetCount * 20)
    $emptyBlocks = 20 - $filledBlocks
    $progressBar = "█" * $filledBlocks + "░" * $emptyBlocks
    
    Write-Host "`r[$progressBar] $mp4Count/$targetCount 已转换 | 耗时: $elapsedStr | 预计剩余: $estimatedStr" -NoNewline
    
    if ($mp4Count -ge $targetCount) {
        $isComplete = $true
    } else {
        Start-Sleep -Seconds $checkInterval
    }
}

Write-Host ""
Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "✅ MP4转换完成! CONVERSION COMPLETE!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Show converted videos
$mp4Files = Get-ChildItem -Path $videosPath -Filter '*.mp4' -File | Sort-Object Name
Write-Host ""
Write-Host "🎬 已转换的MP4视频 ($($mp4Files.Count) 个):" -ForegroundColor Cyan
Write-Host ""

$mp4Files | ForEach-Object {
    $sizeMB = [Math]::Round($_.Length / 1MB, 2)
    Write-Host "   ✓ $($_.Name)" -ForegroundColor Green
    Write-Host "     └─ 大小: $sizeMB MB" -ForegroundColor Gray
}

# Final stats
$totalSize = 0
$mp4Files | ForEach-Object {
    $totalSize += $_.Length
}

$totalElapsed = (Get-Date) - $startTime
$totalElapsedStr = "{0:D2}:{1:D2}:{2:D2}" -f [int]$totalElapsed.TotalHours, [int]$totalElapsed.Minutes, [int]$totalElapsed.Seconds
$totalSizeMB = [Math]::Round($totalSize / 1MB, 2)

Write-Host ""
Write-Host "📊 统计信息:" -ForegroundColor Cyan
Write-Host "   总MP4数: $($mp4Files.Count) 个" -ForegroundColor White
Write-Host "   总大小: $totalSizeMB MB" -ForegroundColor White
Write-Host "   转换耗时: $totalElapsedStr" -ForegroundColor White
Write-Host "   平均每视频: $('{0:F1}' -f ($totalElapsed.TotalSeconds / $mp4Files.Count)) 秒" -ForegroundColor White
Write-Host "   平均每视频大小: $('{0:F2}' -f ($totalSizeMB / $mp4Files.Count)) MB" -ForegroundColor White

Write-Host ""
Write-Host "📁 输出目录:" -ForegroundColor Cyan
Write-Host "   $videosPath" -ForegroundColor Gray

Write-Host ""
Write-Host "⏰ 完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host ""

# Play completion sound
try {
    $beep = New-Object System.Media.SoundPlayer
    $soundFile = "C:\Windows\Media\tada.wav"
    if (Test-Path $soundFile) {
        $beep.SoundLocation = $soundFile
        $beep.PlaySync()
    }
} catch {
    [console]::beep(1000, 500)
}

Write-Host "===============================================" -ForegroundColor Green
Write-Host "所有视频已成功转换为MP4格式！" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
