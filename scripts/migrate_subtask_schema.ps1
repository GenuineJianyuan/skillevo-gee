param(
    [string]$Root = (Join-Path $PSScriptRoot '..\knowledge\published\subtasks')
)

$canonicalFiles = @(
    'SUBTASK-AOI-DEFINE-001.md',
    'SUBTASK-COLLECTION-FILTER-001.md',
    'SUBTASK-MAP-PRESENTATION-001.md',
    'SUBTASK-DRIVE-EXPORT-001.md'
)

Get-ChildItem -File -LiteralPath $Root -Filter '*.md' | ForEach-Object {
    if ($_.Name -in $canonicalFiles) { return }

    $text = Get-Content -Raw -LiteralPath $_.FullName
    $operation = if ($_.Name -eq 'SUBTASK-THEMATIC-LEGEND-001.md') { 'optional' } else { 'required' }
    if ($text -notmatch '(?m)^operation:') {
        $text = [regex]::Replace(
            $text,
            '(?s)\A---\r?\n(.*?)\r?\n---',
            { param($match) "---`r`n$($match.Groups[1].Value)`r`noperation: $operation`r`n---" },
            1
        )
    }

    $text = $text -replace '(?m)^# (简述|Summary)\r?$', '# Purpose'
    $text = $text -replace '(?m)^## (算法描述|Algorithm)\r?$', '## Procedure'
    $text = $text -replace '(?m)^## (软约束|Soft constraints)\r?$', '## Constraints'
    $text = $text -replace '(?m)^# 代码骨架\r?$', '### Implementation'
    $text = $text -replace '(?m)^## Implementation\r?$', '### Implementation'
    $text = $text -replace '(?m)^# Scenario\r?$', '### Scenario'
    $text = $text -replace '(?m)^# 验证\r?$', '### Validation'
    $text = $text -replace '(?m)^## Validation evidence\r?$', '### Validation'
    $text = $text -replace '(?m)^# 限制\r?$', '### Limitations'
    $text = $text -replace '(?m)^## Limitations\r?$', '### Limitations'

    if ($text -notmatch '(?m)^## Operation classification$') {
        $classification = if ($operation -eq 'optional') {
            "``optional``。该操作只影响展示或交付，不改变核心分析结果。"
        } else {
            "``required``。该操作是其所属 Task 核心分析链的一部分。"
        }
        $text = $text -replace '(?m)^## Procedure\r?$', "## Operation classification`r`n`r`n$classification`r`n`r`n## Procedure"
    }

    $text = [regex]::Replace(
        $text,
        '(?m)^## Example\r?\n\r?\n### ([^\r\n]+)',
        "## Example`r`n`r`n### Scenario`r`n`r`n`$1",
        1
    )
    $text = $text -replace '(?m)^- Source: ', 'Source: '
    $text = $text -replace '(?m)^- Status: .+\r?\n?', ''

    if ($text -notmatch '(?m)^### Validation$') {
        $text = $text -replace '(?m)^### Limitations\r?$', "### Validation`r`n`r`nStatus: ``$operation`` operation; knowledge status follows frontmatter and requires Task-level execution evidence.`r`n`r`n### Limitations"
    }

    Set-Content -LiteralPath $_.FullName -Value $text -Encoding utf8
}
