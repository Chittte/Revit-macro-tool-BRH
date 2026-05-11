#Requires AutoHotkey v1.1
#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%

; === REVIT MACRO TOOL - DEBUT ===
_rmt_idx   := 1
_rmt_count := 3

#IfWinActive Autodesk Revit
PgUp::
    _rmt_idx := (_rmt_idx > 1) ? _rmt_idx - 1 : _rmt_count
    FileDelete, C:\Users\brheaume\Projects\revit-macro-tool\data_local\_rmt_profile.txt
    FileAppend, %_rmt_idx%, C:\Users\brheaume\Projects\revit-macro-tool\data_local\_rmt_profile.txt
    return

PgDn::
    _rmt_idx := (_rmt_idx < _rmt_count) ? _rmt_idx + 1 : 1
    FileDelete, C:\Users\brheaume\Projects\revit-macro-tool\data_local\_rmt_profile.txt
    FileAppend, %_rmt_idx%, C:\Users\brheaume\Projects\revit-macro-tool\data_local\_rmt_profile.txt
    return
#IfWinActive

XButton1::
    if (_rmt_idx == 1)  ; Create Similar
    {
        Send, CS
        Sleep, 100
    }
    else if (_rmt_idx == 2)  ; armature et dalle
    {
        oldClip := ClipboardAll
        Clipboard := "__M@__'' c/c"
        ClipWait, 1
        Send, ^v
        Sleep, 50
        Clipboard := oldClip
        Sleep, 100
    }
    return

XButton2::
    if (_rmt_idx == 1)  ; Create Similar
    {
        Send, CS
        Sleep, 100
    }
    else if (_rmt_idx == 2)  ; armature et dalle
    {
        oldClip := ClipboardAll
        Clipboard := "DALLE SUR SOL"
        ClipWait, 1
        Send, ^v
        Sleep, 50
        Clipboard := oldClip
        Sleep, 100
    }
    else if (_rmt_idx == 3)  ; Copie et TR
    {
        Send, ()
        Sleep, 100
    }
    return

; === REVIT MACRO TOOL - FIN ===
