/*
if 0 != 4
{
  MsgBox incorrect number of arguments exiting
  ExitApp
}
*/
/*
SysGet, MonitorCount, MonitorCount
SysGet, MonitorPrimary, MonitorPrimary
MsgBox, Monitor Count:`t%MonitorCount%`nPrimary Monitor:`t%MonitorPrimary%
Loop, %MonitorCount%
{
    SysGet, MonitorName, MonitorName, %A_Index%
    SysGet, Monitor, Monitor, %A_Index%
    SysGet, MonitorWorkArea, MonitorWorkArea, %A_Index%
    MsgBox, Monitor:`t#%A_Index%`nName:`t%MonitorName%`nLeft:`t%MonitorLeft% (%MonitorWorkAreaLeft% work)`nTop:`t%MonitorTop% (%MonitorWorkAreaTop% work)`nRight:`t%MonitorRight% (%MonitorWorkAreaRight% work)`nBottom:`t%MonitorBottom% (%MonitorWorkAreaBottom% work)
}
*/
;setformat,float, 0.2
x:=(1033.0*0.66)
y:=(7.0*0.66)
w:=(867.0*0.66)
h:=(514*0.66)
CoordMode, Mouse, Screen
WinMove,SlingPlayer,,x,y,w,h 

Return