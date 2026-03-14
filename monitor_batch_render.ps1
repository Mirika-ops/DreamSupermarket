#!/usr/bin/env pwsh
<#
.SYNOPSIS
Monitor batch render progress and notify when complete
.DESCRIPTION
Checks every 30 seconds for completed video directories
Alerts when all 20 videos are complete
#>

$videosPath = 'f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\videos'
$targetCount = 20
$checkInterval = 30  # seconds
$startTime = Get-Date

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 批渲染监控 - Batch Render Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "目标: 完成 $targetCount 个视频" -ForegroundColor Yellow
Write-Host "检查间隔: $checkInterval 秒" -ForegroundColor Yellow
Write-Host "开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host ""

$isComplete = $false

while (-not $isComplete) {
    $videoDirs = @(Get-ChildItem -Path $videosPath -Filter '*_frames' -Directory -ErrorAction SilentlyContinue)
    $completedCount = @($videoDirs).Count
    
    # Calculate elapsed time
    $elapsed = (Get-Date) - $startTime
    $elapsedStr = "{0:D2}:{1:D2}:{2:D2}" -f [int]$elapsed.TotalHours, [int]$elapsed.Minutes, [int]$elapsed.Seconds
    
    # Calculate estimated time remaining (rough estimate based on linear progression)
    if ($completedCount -gt 0) {
        $timePerVideo = $elapsed.TotalSeconds / $completedCount
        $remainingVideos = $targetCount - $completedCount
        $estimatedSecondsRemaining = $timePerVideo * $remainingVideos
        $estimatedTimeRemaining = New-TimeSpan -Seconds $estimatedSecondsRemaining
        $estimatedStr = "{0:D2}:{1:D2}:{2:D2}" -f [int]$estimatedTimeRemaining.TotalHours, [int]$estimatedTimeRemaining.Minutes, [int]$estimatedTimeRemaining.Seconds
    } else {
        $estimatedStr = "计算中..."
    }
    
    # Display progress
    $progressBar = ""
    $filledBlocks = [int]($completedCount / $targetCount * 20)
    $emptyBlocks = 20 - $filledBlocks
    $progressBar = "█" * $filledBlocks + "░" * $emptyBlocks
    
    Write-Host "`r[$progressBar] $completedCount/$targetCount 已完成 | 耗时: $elapsedStr | 预计剩余: $estimatedStr" -NoNewline
    
    if ($completedCount -ge $targetCount) {
        $isComplete = $true
    } else {
        Start-Sleep -Seconds $checkInterval
    }
}

Write-Host ""
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 渲染完成! ALL RENDER COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Show completed videos
$videoDirs = Get-ChildItem -Path $videosPath -Filter '*_frames' -Directory | Sort-Object Name
Write-Host ""
Write-Host "📹 已完成的视频 ($($videoDirs.Count) 个):" -ForegroundColor Cyan

$videoDirs | ForEach-Object {
    $frameCount = @(Get-ChildItem "$($_.FullName)\frame_*.png" -ErrorAction SilentlyContinue).Count
    Write-Host "   ✓ $($_.Name)" -ForegroundColor Green
    Write-Host "     └─ $frameCount 帧" -ForegroundColor Gray
}

# Final stats
$totalFrames = 0
$videoDirs | ForEach-Object {
    $frameCount = @(Get-ChildItem "$($_.FullName)\frame_*.png" -ErrorAction SilentlyContinue).Count
    $totalFrames += $frameCount
}

$totalElapsed = (Get-Date) - $startTime
$totalElapsedStr = "{0:D2}:{1:D2}:{2:D2}" -f [int]$totalElapsed.TotalHours, [int]$totalElapsed.Minutes, [int]$totalElapsed.Seconds

Write-Host ""
Write-Host "📊 统计信息:" -ForegroundColor Cyan
Write-Host "   总视频数: $($videoDirs.Count) 个" -ForegroundColor White
Write-Host "   总帧数: $totalFrames 帧" -ForegroundColor White
Write-Host "   总耗时: $totalElapsedStr" -ForegroundColor White
Write-Host "   平均每视频耗时: $('{0:F1}' -f ($totalElapsed.TotalSeconds / $videoDirs.Count)) 秒" -ForegroundColor White

Write-Host ""
Write-Host "📁 输出目录:" -ForegroundColor Cyan
Write-Host "   $videosPath" -ForegroundColor Gray

Write-Host ""
Write-Host "⏰ 完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host ""

# Optional: Play sound notification
try {
    $beep = New-Object System.Media.SoundPlayer
    # Windows system notification sound
    $soundFile = "C:\Windows\Media\tada.wav"
    if (Test-Path $soundFile) {
        $beep.SoundLocation = $soundFile
        $beep.PlaySync()
    }
} catch {
    # Fallback: beep
    [console]::beep(1000, 500)
    [console]::beep(1000, 500)
}

Write-Host "==========================================" -ForegroundColor Green
Write-Host "所有视频已渲染完成！现在可以转换为MP4格式。" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
