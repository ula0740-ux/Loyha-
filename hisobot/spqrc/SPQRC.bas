Attribute VB_Name = "SPQRC"
' SPQRC haftalik belgilash shabloni uchun makroslar (SPQRC_haftalik_shablon.pptx).
' Ulash: Alt+F11 -> File -> Import File -> SPQRC.bas, keyin faylni .pptm sifatida saqlang.
'   ToggleMark  - slayd-shouda katakni bosganda: bo'sh -> (bajarildi) -> (bajarilmadi) -> bo'sh, foizlar yangilanadi
'   Yangilash   - barcha foiz, son, chiziq va jadval ranglarini qayta hisoblaydi (tahrirlash rejimida + / - yozilgandan keyin)
'   OyniOrnatish - yangi oy: hafta sanalarini qo'yadi, belgilarni tozalaydi, oyda yo'q haftani "-" (chiziqcha) qiladi
'   Tozalash    - barcha belgilarni tozalaydi
' Shakl nomlari: CELL|s|d|r|w  HDR|s|d|w  TXT|metric|s|d|r|w  BAR|pct|s|d|r|w  TRK|pct|s|d|r|w  MAT|s|d   (0 = yig'indi)
Option Explicit

Private Const MS As Long = 4   ' sexlar
Private Const MD As Long = 5   ' yo'nalishlar (Du..Ju)
Private Const MR As Long = 12  ' ko'rsatkichlar
Private Const MW As Long = 5   ' haftalar

Private nDone(0 To MS, 0 To MD, 0 To MR, 0 To MW) As Long
Private nMiss(0 To MS, 0 To MD, 0 To MR, 0 To MW) As Long
Private nPlan(0 To MS, 0 To MD, 0 To MR, 0 To MW) As Long

Private Function SOk() As String: SOk = ChrW(&H2713): End Function
Private Function SNo() As String: SNo = ChrW(&H2717): End Function
Private Function SOff() As String: SOff = ChrW(&H2014): End Function

Private Function cTeal() As Long: cTeal = RGB(60, 198, 184): End Function
Private Function cLTeal() As Long: cLTeal = RGB(127, 217, 207): End Function
Private Function cAmber() As Long: cAmber = RGB(232, 184, 110): End Function
Private Function cCoral() As Long: cCoral = RGB(232, 130, 110): End Function
Private Function cGrey() As Long: cGrey = RGB(90, 98, 108): End Function

' Katak qiymatini me'yorlash: + / v -> belgi OK ;  - / x -> belgi NO ; chiziqcha saqlanadi ; qolgani bo'sh
Private Function Norm(ByVal t As String) As String
    t = Trim$(Replace(Replace(t, vbCr, ""), vbLf, ""))
    Select Case t
        Case "": Norm = ""
        Case "+", "v", "V", SOk(), ChrW(&H2714): Norm = SOk()
        Case "-", ChrW(&H2212), ChrW(&H2013), "x", "X", ChrW(&H445), ChrW(&H425), SNo(), ChrW(&H2718): Norm = SNo()
        Case SOff(): Norm = SOff()
        Case Else: Norm = ""
    End Select
End Function

Private Function Pct(ByVal a As Long, ByVal b As Long) As String
    Dim s As String
    If b = 0 Then Pct = SOff(): Exit Function
    s = Replace(Format(a * 100# / b, "0.0"), ".", ",")
    If Right$(s, 2) = ",0" Then s = Left$(s, Len(s) - 2)
    Pct = s & "%"
End Function

Private Function ExeColor(ByVal dn As Long, ByVal ms As Long) As Long
    Dim v As Double
    If dn + ms = 0 Then ExeColor = cGrey(): Exit Function
    v = dn / (dn + ms)
    If v >= 0.999 Then
        ExeColor = cTeal()
    ElseIf v >= 0.75 Then
        ExeColor = cLTeal()
    ElseIf v >= 0.5 Then
        ExeColor = cAmber()
    Else
        ExeColor = cCoral()
    End If
End Function

Private Sub StyleCell(shp As Shape, ByVal v As String)
    With shp.TextFrame.TextRange
        .Text = v
        .ParagraphFormat.Alignment = ppAlignCenter
        .Font.Name = "Segoe UI Semibold"
        .Font.Size = 13
        If v = SOk() Then
            .Font.Color.RGB = cTeal()
        ElseIf v = SNo() Then
            .Font.Color.RGB = cCoral()
        Else
            .Font.Color.RGB = cGrey()
        End If
    End With
End Sub

Private Function HasText(shp As Shape) As Boolean
    HasText = False
    On Error Resume Next
    HasText = shp.HasTextFrame
End Function

' ---------- hisoblash va yangilash ----------
Public Sub Yangilash()
    Dim sld As Slide, shp As Shape, p() As String, v As String
    Dim s As Long, d As Long, r As Long, w As Long
    Dim a As Long, b As Long, c As Long, e As Long

    Erase nDone: Erase nMiss: Erase nPlan

    ' 1) katakchalarni yig'ish
    For Each sld In ActivePresentation.Slides
        For Each shp In sld.Shapes
            If Left$(shp.Name, 5) = "CELL|" Then
                p = Split(shp.Name, "|")
                s = CLng(p(1)): d = CLng(p(2)): r = CLng(p(3)): w = CLng(p(4))
                v = Norm(shp.TextFrame.TextRange.Text)
                If v <> shp.TextFrame.TextRange.Text Then StyleCell shp, v
                If v <> SOff() Then
                    For a = 0 To 1: For b = 0 To 1: For c = 0 To 1: For e = 0 To 1
                        nPlan(s * a, d * b, r * c, w * e) = nPlan(s * a, d * b, r * c, w * e) + 1
                        If v = SOk() Then nDone(s * a, d * b, r * c, w * e) = nDone(s * a, d * b, r * c, w * e) + 1
                        If v = SNo() Then nMiss(s * a, d * b, r * c, w * e) = nMiss(s * a, d * b, r * c, w * e) + 1
                    Next e: Next c: Next b: Next a
                End If
            End If
        Next shp
    Next sld

    ' 2) matn, chiziq, jadval
    Dim m As String, dn As Long, mi As Long, pl As Long, trk As Shape, ratio As Double
    For Each sld In ActivePresentation.Slides
        For Each shp In sld.Shapes
            If Left$(shp.Name, 4) = "TXT|" Then
                p = Split(shp.Name, "|")
                m = p(1): s = CLng(p(2)): d = CLng(p(3)): r = CLng(p(4)): w = CLng(p(5))
                dn = nDone(s, d, r, w): mi = nMiss(s, d, r, w): pl = nPlan(s, d, r, w)
                With shp.TextFrame.TextRange
                    Select Case m
                        Case "pct": .Text = Pct(dn, pl)
                        Case "exe": .Text = Pct(dn, dn + mi)
                        Case "miss": .Text = CStr(mi)
                        Case "plan": .Text = CStr(pl)
                        Case "done"
                            If .Runs.Count >= 2 Then
                                .Runs(1).Text = CStr(dn)
                                .Runs(2).Text = " / " & CStr(pl)
                            Else
                                .Text = CStr(dn)
                            End If
                    End Select
                End With
            ElseIf Left$(shp.Name, 4) = "BAR|" Then
                p = Split(shp.Name, "|")
                s = CLng(p(2)): d = CLng(p(3)): r = CLng(p(4)): w = CLng(p(5))
                Set trk = Nothing
                On Error Resume Next
                Set trk = sld.Shapes("TRK" & Mid$(shp.Name, 4))
                On Error GoTo 0
                If Not trk Is Nothing Then
                    dn = nDone(s, d, r, w): pl = nPlan(s, d, r, w)
                    If pl > 0 Then ratio = dn / pl Else ratio = 0
                    shp.Left = trk.Left
                    shp.Width = IIf(trk.Width * ratio < 1.5, 1.5, trk.Width * ratio)
                    shp.Visible = (ratio > 0)
                    shp.Fill.ForeColor.RGB = ExeColor(dn, nMiss(s, d, r, w))
                End If
            ElseIf Left$(shp.Name, 4) = "MAT|" Then
                p = Split(shp.Name, "|")
                s = CLng(p(1)): d = CLng(p(2))
                shp.TextFrame.TextRange.Text = Pct(nDone(s, d, 0, 0), nPlan(s, d, 0, 0))
                shp.Fill.ForeColor.RGB = ExeColor(nDone(s, d, 0, 0), nMiss(s, d, 0, 0))
            End If
        Next shp
    Next sld
End Sub

' ---------- slayd-shouda katakni bosish ----------
Public Sub ToggleMark(oShp As Shape)
    Dim shp As Shape, v As String
    On Error Resume Next
    Set shp = ActivePresentation.Slides(oShp.Parent.SlideIndex).Shapes(oShp.Name)
    On Error GoTo 0
    If shp Is Nothing Then Set shp = oShp
    v = Norm(shp.TextFrame.TextRange.Text)
    If v = SOff() Then Exit Sub
    If v = "" Then
        v = SOk()
    ElseIf v = SOk() Then
        v = SNo()
    Else
        v = ""
    End If
    StyleCell shp, v
    Yangilash
    On Error Resume Next
    With SlideShowWindows(1).View
        .GotoSlide .CurrentShowPosition
    End With
End Sub

' ---------- yangi oy ----------
Public Sub OyniOrnatish()
    Dim inp As String, y As Long, mo As Long, nd As Long
    Dim sld As Slide, shp As Shape, p() As String, d As Long, w As Long, dt As Long

    inp = InputBox("Yil-oy (masalan 2026-12):", "SPQRC - yangi oy", Format(DateAdd("m", 1, Date), "yyyy-mm"))
    If inp = "" Then Exit Sub
    On Error GoTo Xato
    y = CLng(Left$(inp, 4)): mo = CLng(Mid$(inp, 6, 2))
    If mo < 1 Or mo > 12 Then GoTo Xato
    On Error GoTo 0
    nd = Day(DateSerial(y, mo + 1, 0))

    For Each sld In ActivePresentation.Slides
        For Each shp In sld.Shapes
            If Left$(shp.Name, 4) = "HDR|" Then
                p = Split(shp.Name, "|"): d = CLng(p(2)): w = CLng(p(3))
                dt = NthDay(y, mo, d, w)
                With shp.TextFrame.TextRange
                    If .Paragraphs.Count >= 2 Then
                        If dt <= nd Then .Paragraphs(2).Text = Format(dt, "00") & "." & Format(mo, "00") Else .Paragraphs(2).Text = SOff()
                    End If
                End With
            ElseIf Left$(shp.Name, 5) = "CELL|" Then
                p = Split(shp.Name, "|"): d = CLng(p(2)): w = CLng(p(4))
                dt = NthDay(y, mo, d, w)
                If dt <= nd Then
                    StyleCell shp, ""
                    With shp.ActionSettings(ppMouseClick)
                        .Action = ppActionRunMacro
                        .Run = "ToggleMark"
                    End With
                Else
                    StyleCell shp, SOff()
                    shp.ActionSettings(ppMouseClick).Action = ppActionNone
                End If
            End If
        Next shp
    Next sld
    Yangilash
    MsgBox "Tayyor: " & inp & ". Sarlavhadagi oy nomini Ctrl+H (Replace) bilan almashtiring.", vbInformation, "SPQRC"
    Exit Sub
Xato:
    MsgBox "Format: YYYY-MM (masalan 2026-12)", vbExclamation, "SPQRC"
End Sub

' oyning w-chi d-hafta kuni (d: 1=Dushanba .. 5=Juma) -> kun raqami (oydan oshsa > oy kunlari)
Private Function NthDay(ByVal y As Long, ByVal mo As Long, ByVal d As Long, ByVal w As Long) As Long
    Dim wd1 As Long
    wd1 = Weekday(DateSerial(y, mo, 1), vbMonday)
    NthDay = 1 + ((d - wd1 + 7) Mod 7) + 7 * (w - 1)
End Function

Public Sub Tozalash()
    Dim sld As Slide, shp As Shape
    If MsgBox("Barcha belgilar o'chirilsinmi?", vbYesNo + vbQuestion, "SPQRC") <> vbYes Then Exit Sub
    For Each sld In ActivePresentation.Slides
        For Each shp In sld.Shapes
            If Left$(shp.Name, 5) = "CELL|" Then
                If Norm(shp.TextFrame.TextRange.Text) <> SOff() Then StyleCell shp, ""
            End If
        Next shp
    Next sld
    Yangilash
End Sub
