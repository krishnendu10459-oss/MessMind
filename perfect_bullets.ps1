$ppt = New-Object -ComObject PowerPoint.Application
$presPath = "C:\Users\LOQ\Desktop\IDT 3rd sem\AI_Powered_Food_Waste_Prediction_System_Presentation.pptx"
$p = $ppt.Presentations.Open($presPath, $false, $false, $false)

# Slide 1: Title
$s1 = $p.Slides.Item(1)
$tf1 = $s1.Shapes.Item("Subtitle 2").TextFrame
for ($i = 1; $i -le $tf1.TextRange.Paragraphs().Count; $i++) {
    $tf1.TextRange.Paragraphs($i).ParagraphFormat.Bullet.Type = 0
}

# Slide 2: Abstract
$s2 = $p.Slides.Item(2)
$tf2 = $s2.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf2.TextRange.Paragraphs().Count; $i++) {
    $tf2.TextRange.Paragraphs($i).ParagraphFormat.Bullet.Type = 0
}

# Slide 3: Contents (Clean numbering, no bullet symbol)
$s3 = $p.Slides.Item(3)
$tf3 = $s3.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf3.TextRange.Paragraphs().Count; $i++) {
    $tf3.TextRange.Paragraphs($i).ParagraphFormat.Bullet.Type = 0
    $tf3.TextRange.Paragraphs($i).ParagraphFormat.LeftIndent = 0
    $tf3.TextRange.Paragraphs($i).ParagraphFormat.FirstLineIndent = 0
}

# Slide 4: Introduction
$s4 = $p.Slides.Item(4)
$tf4 = $s4.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf4.TextRange.Paragraphs().Count; $i++) {
    $para = $tf4.TextRange.Paragraphs($i)
    $para.ParagraphFormat.Bullet.Type = 1 # ppBulletUnnumbered
    $para.ParagraphFormat.Bullet.Character = 8226 # •
}

# Slide 5: Problem Statement (No bullets)
$s5 = $p.Slides.Item(5)
$tf5 = $s5.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf5.TextRange.Paragraphs().Count; $i++) {
    $tf5.TextRange.Paragraphs($i).ParagraphFormat.Bullet.Type = 0
    $tf5.TextRange.Paragraphs($i).ParagraphFormat.LeftIndent = 0
    $tf5.TextRange.Paragraphs($i).ParagraphFormat.FirstLineIndent = 0
}

# Slide 6: Literature Survey
$s6 = $p.Slides.Item(6)
$tf6 = $s6.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf6.TextRange.Paragraphs().Count; $i++) {
    $para = $tf6.TextRange.Paragraphs($i)
    if ($i % 2 -eq 1) {
        $para.ParagraphFormat.Bullet.Type = 1
        $para.ParagraphFormat.Bullet.Character = 8226 # •
    } else {
        $para.ParagraphFormat.Bullet.Type = 1
        $para.ParagraphFormat.Bullet.Character = 8211 # –
        $para.ParagraphFormat.LeftIndent = 36 # indent for sub-item
        $para.ParagraphFormat.FirstLineIndent = -18
    }
}

# Slide 7: System Design & Methodology
$s7 = $p.Slides.Item(7)
$tf7 = $s7.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf7.TextRange.Paragraphs().Count; $i++) {
    $para = $tf7.TextRange.Paragraphs($i)
    if ($i -eq 1 -or $i -eq 6) {
        $para.ParagraphFormat.Bullet.Type = 0
        $para.ParagraphFormat.LeftIndent = 0
        $para.ParagraphFormat.FirstLineIndent = 0
    } else {
        $para.ParagraphFormat.Bullet.Type = 1
        $para.ParagraphFormat.Bullet.Character = 8226
    }
}

# Slide 8: Hardware & Software Requirements
$s8 = $p.Slides.Item(8)
$tf8 = $s8.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf8.TextRange.Paragraphs().Count; $i++) {
    $para = $tf8.TextRange.Paragraphs($i)
    if ($i -eq 1 -or $i -eq 7) {
        $para.ParagraphFormat.Bullet.Type = 0
        $para.ParagraphFormat.LeftIndent = 0
        $para.ParagraphFormat.FirstLineIndent = 0
    } else {
        $para.ParagraphFormat.Bullet.Type = 1
        $para.ParagraphFormat.Bullet.Character = 8226
    }
}

# Slide 9: Expected Outcomes
$s9 = $p.Slides.Item(9)
$tf9 = $s9.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf9.TextRange.Paragraphs().Count; $i++) {
    $para = $tf9.TextRange.Paragraphs($i)
    $para.ParagraphFormat.Bullet.Type = 1
    $para.ParagraphFormat.Bullet.Character = 8226
}

# Slide 10: References (No bullets)
$s10 = $p.Slides.Item(10)
$rect10 = $s10.Shapes.Item("Rectangle 1")
$tf10 = $rect10.TextFrame
for ($i = 1; $i -le $tf10.TextRange.Paragraphs().Count; $i++) {
    $tf10.TextRange.Paragraphs($i).ParagraphFormat.Bullet.Type = 0
}

# Slide 11: Thank You (No bullets)
$s11 = $p.Slides.Item(11)
$tf11 = $s11.Shapes.Item("Content Placeholder 2").TextFrame
for ($i = 1; $i -le $tf11.TextRange.Paragraphs().Count; $i++) {
    $tf11.TextRange.Paragraphs($i).ParagraphFormat.Bullet.Type = 0
}

$p.Save()
Write-Host "Formatting polished and saved successfully!"

# Re-export all slides to PNG for final verification
$imgFolder = "C:\Users\LOQ\Desktop\IDT 3rd sem\slide_images"
for ($i = 1; $i -le $p.Slides.Count; $i++) {
    $s = $p.Slides.Item($i)
    $outImg = "$imgFolder\slide_$i.png"
    $s.Export($outImg, "PNG", 1280, 720)
}
$p.Close()
$ppt.Quit()
Write-Host "All 11 slides re-exported to slide_images"
