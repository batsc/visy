; N.B. The unformatted files dealt with in this program are big-endian.
; If this procedure is run on a little-endian platform (e.g. Linux),
; then this has to be accounted for explicitly.

; As this is an F77 unformatted file, there are 4 bytes at the start and 
; end of each chunk of data (one chunk in this case), giving the byte
; length of that chunk as a long integer.
   
; Check to see if we are on a little endian platform.
;little_end = LITTLE_ENDIAN() ; this only seems to work with PV-WAVE, not IDL...
little_end = 1 ; assume little-endian for now

; If it is little endian, then we don't want to use the f77 keyword because
; we need to handle the housekeeping bytes ourselves.
IF little_end THEN f77 = 0 ELSE f77 = 1

; get the lat/lon data for the EW area

Lat=fltarr(1180,1180)
Lon=fltarr(1180,1180)

openr,1,'/data/nwp1/frpf/MSG/Data/EW_lat.dat', F77=f77
IF little_end THEN BEGIN
   filestat = FSTAT(1)
   cur_ptr = filestat.cur_ptr
   POINT_LUN, 1, cur_ptr + 4
ENDIF
readu,1,Lat
close,1
openr,1,'/data/nwp1/frpf/MSG/Data/EW_lon.dat', F77=f77
IF little_end THEN BEGIN
   filestat = FSTAT(1)
   cur_ptr = filestat.cur_ptr
   POINT_LUN, 1, cur_ptr + 4
ENDIF
readu,1,Lon
close,1
IF little_end THEN BEGIN
   BYTEORDER, Lat, /ntohl
   BYTEORDER, Lon, /ntohl
ENDIF

; reverse the lat/lon values in the y direction, as read_png effectively does this to the image pixels
Lat=reverse(Lat,2)
Lon=reverse(Lon,2)

; now read in a sample EIEW51 image (10.8 micron IR)

EW31_filename='/data/nwp1/frpf/RDT/PGE11_20150824/RDT_Autosat_images/EIEW51_201508241400.png'

xs_all=1180 ; true image size
ys_all=1180 ; true image size
xs_image=1180 ; useful image size
ys_image=1180 ; useful image size

x=read_png(EW31_filename)

device, decomposed=0
tvlct,255,255,255,1 ; put white in 1
tvlct,189,253,229,2 ; put "coast" in 2
; reset to grey-scale (in case not done previously)
tvlct,  3,  3,  3,3 ; reset 3
tvlct,  4,  4,  4,4 ; reset 4
tvlct,  5,  5,  5,5 ; reset 5
tvlct,  6,  6,  6,6 ; reset 6
tvlct,  7,  7,  7,7 ; reset 7
tvlct,  8,  8,  8,8 ; reset 8
tvlct,  9,  9,  9,9 ; reset 9

window,1,xsize=800,ysize=1095,retain=2,title='From EIEW51_201508241400'

tv,x(0:799,0:1094) ; whole image doesn't quite fit my screen, so clip top! (and only print out to roughly the eastern edge of the processing domain...)

; so, we have lat and lon values for each of the 1180x1180 pixels

tvlct,255,  0,  0,3 ; put red in 3
tvlct,  0,255,  0,4 ; put green in 4
tvlct,  0,  0,255,5 ; put darkish blue in 5
tvlct,255,255,  0,6 ; put yellow in 6
tvlct,255,  0,255,7 ; put magenta in 7
tvlct,255,127,  0,8 ; put orange in 8
tvlct,  0,255,255,9 ; put cyan in 9

openr,1,'/data/nwp1/frpf/RDT/PGE11_20150824/PGE11/SAFNWC_MSG3_RDT__201508241345_ukamv_______.buf_section4'

dumstr=''

; read header info
for i=0,6 do begin
 readf,1,dumstr
endfor

; year
readf,1,dumstr
if (fix(strmid(dumstr,0,2)) eq 6) then begin
 yearimage=fix(strmid(dumstr,72,4))
 print,' yearimage: ',yearimage
endif else begin
 print,' Error: not expected ref #6'
 stop
endelse

; month
readf,1,dumstr
if (fix(strmid(dumstr,0,2)) eq 7) then begin
 monthimage=fix(strmid(dumstr,72,2))
 print,' monthimage: ',monthimage
endif else begin
 print,' Error: not expected ref #7'
 stop
endelse

; day
readf,1,dumstr
if (fix(strmid(dumstr,0,2)) eq 8) then begin
 dayimage=fix(strmid(dumstr,72,2))
 print,' dayimage: ',dayimage
endif else begin
 print,' Error: not expected ref #8'
 stop
endelse

; hour
readf,1,dumstr
if (fix(strmid(dumstr,0,2)) eq 9) then begin
 hourimage=fix(strmid(dumstr,72,2))
 print,' hourimage: ',hourimage
endif else begin
 print,' Error: not expected ref #9'
 stop
endelse

; minute
readf,1,dumstr
if (fix(strmid(dumstr,0,2)) eq 10) then begin
 minuteimage=fix(strmid(dumstr,72,2))
 print,' minuteimage: ',minuteimage
endif else begin
 print,' Error: not expected ref #10'
 stop
endelse

; read header info
for i=0,15 do begin
 readf,1,dumstr
endfor

; next line should give number of detected systems
readf,1,dumstr
if (fix(strmid(dumstr,0,2)) eq 23) then begin
 numsys=fix(strmid(dumstr,72,10)) ; number of detected systems
 print,' numsys: ',numsys
endif else begin
 print,' Error: not expected ref #23'
 stop
endelse

latsys=fltarr(numsys)
lonsys=fltarr(numsys)
btthreshsys=fltarr(numsys)
dirnsys=fltarr(numsys)
speedsys=fltarr(numsys)
ctpsys=fltarr(numsys)
btminsys=fltarr(numsys)
btavsys=fltarr(numsys)
arearatesys=fltarr(numsys)
coolratesys=fltarr(numsys)
phasesys=intarr(numsys)
areasys=fltarr(numsys)
naturesys=intarr(numsys)
methodsys=strarr(numsys)
durationsys=intarr(numsys)
lflashpossys=intarr(numsys)
idsys=intarr(numsys)
idbirthsys=intarr(numsys)
plot_lightning=intarr(numsys) ; 0 for "plot as if no lightning", >0 for "plot as if there is lightning"
nested=intarr(numsys) ; 0 for not nested, >0 for nested

for inumsys=0,numsys-1 do begin ; loop over detected systems

 ; read next line to get number of points in system contour
 readf,1,dumstr
 readf,1,dumstr
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 27) then begin
  numcpts=fix(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' numcpts: ',numcpts
 endif else begin
  print,' Error: not expected ref #27'
  stop
 endelse

 contlat=fltarr(numcpts)
 contlon=fltarr(numcpts)
 for icpts=0,numcpts-1 do begin ; loop over points in contour, to read lat/lons
  readf,1,dumstr ; read lat
  if (float(strmid(dumstr,0,2)) eq 28) then begin
   contlat(icpts)=float(strmid(dumstr,72,20))
  endif else begin
   print,' Error: not expected ref #28'
   stop
  endelse  
  readf,1,dumstr ; read lon
  if (float(strmid(dumstr,0,2)) eq 29) then begin
   contlon(icpts)=float(strmid(dumstr,72,20))
  endif else begin
   print,' Error: not expected ref #29'
   stop
  endelse  
 endfor

 ; sys nature
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 30) then begin
  if (strmid(dumstr,72,7) eq 'UNKNOWN') then begin
   naturesys(inumsys)=999
  endif else begin
   naturesys(inumsys)=fix(strmid(dumstr,72,10))
;   if (inumsys eq 16) then print,' naturesys: ',naturesys(inumsys)
  endelse
 endif else begin
  print,' Error: not expected ref #30'
  stop
 endelse

 ; sys method
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 31) then begin
  methodsys(inumsys)=strmid(dumstr,72,3)
 endif else begin
  print,' Error: not expected ref #31'
  stop
 endelse

 ; 1 dummy line
 readf,1,dumstr

 ; sys id
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 33) then begin
  idsys(inumsys)=fix(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' idsys: ',idsys(inumsys)
 endif else begin
  print,' Error: not expected ref #33'
  stop
 endelse

 ; sys id at birth
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 34) then begin
  idbirthsys(inumsys)=fix(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' idbirthsys: ',idbirthsys(inumsys)
  ; if the birth id of current system is the same as the main id of the previous system, then mark as nested
  if (inumsys gt 0 and idbirthsys(inumsys) eq idsys(inumsys-1)) then nested(inumsys) = 1
 endif else begin
  print,' Error: not expected ref #34'
  stop
 endelse

 ; 3 dummy lines
 for i=0,2  do begin
  readf,1,dumstr
 endfor

 ; bt threshold
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 38) then begin
  btthreshsys(inumsys)=float(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' btthreshsys: ',btthreshsys(inumsys)
 endif else begin
  print,' Error: not expected ref #38'
  stop
 endelse

 ; sys lat
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 39) then begin
  latsys(inumsys)=float(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' latsys: ',latsys(inumsys)
 endif else begin
  print,' Error: not expected ref #39'
  stop
 endelse

 ; sys lon
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 40) then begin
  lonsys(inumsys)=float(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' lonsys: ',lonsys(inumsys)
 endif else begin
  print,' Error: not expected ref #40'
  stop
 endelse

 ; 10 dummy lines
 for i=0,9  do begin
  readf,1,dumstr
 endfor

 ; sys duration
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 51) then begin
  yearfirstsys=float(strmid(dumstr,72,4))
 endif else begin
  print,' Error: not expected ref #51'
  stop
 endelse
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 52) then begin
  monthfirstsys=float(strmid(dumstr,72,2))
 endif else begin
  print,' Error: not expected ref #52'
  stop
 endelse
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 53) then begin
  dayfirstsys=float(strmid(dumstr,72,2))
 endif else begin
  print,' Error: not expected ref #53'
  stop
 endelse
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 54) then begin
  hourfirstsys=float(strmid(dumstr,72,2))
 endif else begin
  print,' Error: not expected ref #54'
  stop
 endelse
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 55) then begin
  minutefirstsys=float(strmid(dumstr,72,2))
 endif else begin
  print,' Error: not expected ref #55'
  stop
 endelse
 durationsys(inumsys)=15+nint((julday(monthimage,dayimage,yearimage,hourimage,minuteimage)-$
                            julday(monthfirstsys,dayfirstsys,yearfirstsys,hourfirstsys,minutefirstsys))*24.*60.)

 ; sys speed
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 56) then begin
  speedsys(inumsys)=float(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' speedsys: ',speedsys(inumsys)
 endif else begin
  print,' Error: not expected ref #56'
  stop
 endelse

 ; sys direction
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 57) then begin
  dirnsys(inumsys)=float(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' dirnsys: ',dirnsys(inumsys)
 endif else begin
  print,' Error: not expected ref #57'
  stop
 endelse

 ; 2 dummy lines
 for i=0,1  do begin
  readf,1,dumstr
 endfor

 ; sys btmin
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 60) then begin
  btminsys(inumsys)=float(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' btminsys: ',btminsys(inumsys)
 endif else begin
  print,' Error: not expected ref #60'
  stop
 endelse

 ; 1 dummy line
 readf,1,dumstr

 ; sys btav
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 62) then begin
  btavsys(inumsys)=float(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' btavsys: ',btavsys(inumsys)
 endif else begin
  print,' Error: not expected ref #62'
  stop
 endelse

 ; read next line to get number of areas in system contour
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 64) then begin
  numareas=fix(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' numareas: ',numareas
 endif else begin
  print,' Error: not expected ref #64'
  stop
 endelse

 for iareas=0,numareas-1 do begin ; loop over points in areas, to read thresholds and area sizes
  readf,1,dumstr ; threshold
  if (fix(strmid(dumstr,0,2)) eq 65) then begin
   areathresh=float(strmid(dumstr,72,10))
  endif else begin
   print,' Error: not expected ref #65'
   stop
  endelse  
  readf,1,dumstr ; read area size
  if (fix(strmid(dumstr,0,2)) eq 66) then begin
   areacloud=float(strmid(dumstr,72,20))
  endif else begin
   print,' Error: not expected ref #66'
   stop
  endelse
  if (abs(areathresh-btthreshsys(inumsys)) lt 0.0001) then begin
;   if (inumsys eq 16) then print,' areacloud: ',areacloud
   areasys(inumsys)=areacloud/1000000.0 ; km^2
;   if (inumsys eq 16) then print,' areasys: ',areasys(inumsys)
  endif
 endfor

 ; sys area expansion rate
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 67) then begin
  if (strmid(dumstr,72,7) eq 'UNKNOWN') then begin
   timeint=-999.999
  endif else begin
   timeint=float(strmid(dumstr,72,10))
;   if (inumsys eq 16) then print,' timeint: ',timeint
  endelse
 endif else begin
  print,' Error: not expected ref #67'
  stop
 endelse
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 68) then begin
  if (timeint gt -999.) then begin
   arearatesys(inumsys)=float(strmid(dumstr,72,10)) ; fractional area expansion rate per second
;   if (inumsys eq 16) then print,' arearatesys: ',arearatesys(inumsys)
   arearatesys(inumsys)=float(strmid(dumstr,72,10))*100.*60.*timeint ; area expansion rate in percent per timeint
;   if (inumsys eq 16) then print,' arearatesys: ',arearatesys(inumsys)
  endif else begin
    arearatesys(inumsys)=-999.999
  endelse
 endif else begin
  print,' Error: not expected ref #68'
  stop
 endelse

 ; 1 dummy line
 readf,1,dumstr

 ; sys cooling rate
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 70) then begin
  if (strmid(dumstr,72,7) eq 'UNKNOWN') then begin
   timeint=-999.999
  endif else begin
   timeint=float(strmid(dumstr,72,10))
;   if (inumsys eq 16) then print,' timeint: ',timeint
  endelse
 endif else begin
  print,' Error: not expected ref #70'
  stop
 endelse
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 71) then begin
  if (timeint gt -999.) then begin
   coolratesys(inumsys)=float(strmid(dumstr,72,10))
;   if (inumsys eq 16) then print,' coolratesys: ',coolratesys(inumsys)
   coolratesys(inumsys)=float(strmid(dumstr,72,10))*3600. ; per hour
;   if (inumsys eq 16) then print,' coolratesys: ',coolratesys(inumsys)
  endif else begin
    coolratesys(inumsys)=999.999
  endelse
 endif else begin
  print,' Error: not expected ref #71'
  stop
 endelse

 ; 1 dummy line
 readf,1,dumstr

 ; sys phase
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 73) then begin
  phasesys(inumsys)=fix(strmid(dumstr,72,10))
  ; but, if the birth id of current system is the same as the main id of the previous system, then give it the same phase (i.e. colour) as the ancestor
  if (inumsys gt 0 and idbirthsys(inumsys) eq idsys(inumsys-1)) then phasesys(inumsys) = phasesys(inumsys-1)
;  if (inumsys eq 16) then print,' phasesys: ',phasesys(inumsys)
 endif else begin
  print,' Error: not expected ref #73'
  stop
 endelse

 ; sys ctp
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 74) then begin
  if (strmid(dumstr,72,7) eq 'UNKNOWN') then begin
   ctpsys(inumsys)=-999.999
  endif else begin
   ctpsys(inumsys)=float(strmid(dumstr,72,10))
;   if (inumsys eq 16) then print,' ctpsys: ',ctpsys(inumsys)
  endelse
 endif else begin
  print,' Error: not expected ref #74'
  stop
 endelse

 ; 13 dummy lines
 for i=0,12  do begin
  readf,1,dumstr
 endfor

 ; sys lightning
 readf,1,dumstr
 if (fix(strmid(dumstr,0,2)) eq 88) then begin
  lflashpossys(inumsys)=fix(strmid(dumstr,72,10))
;  if (inumsys eq 16) then print,' lflashpossys: ',lflashpossys(inumsys)
 endif else begin
  print,' Error: not expected ref #88'
  stop
 endelse
 if (lflashpossys(inumsys) gt 0) then plot_lightning(inumsys) = 1
 ; but, if the birth id of current system is the same as the main id of the previous system, then plot "with lightning" if the ancestor has lightning - think about whether this is good to do?
 if (inumsys gt 0 and idbirthsys(inumsys) eq idsys(inumsys-1) and plot_lightning(inumsys-1) gt 0) then plot_lightning(inumsys) = plot_lightning(inumsys-1)

 ; 4 dummy lines
 for i=0,3  do begin
  readf,1,dumstr
 endfor

 cont_icol=intarr(numcpts)
 cont_irow=intarr(numcpts)
 if (latsys(inumsys) lt 65.) then begin
;  if (naturesys(inumsys) eq 0 or naturesys(inumsys) eq 1) then begin
;  if (naturesys(inumsys) eq 0 or naturesys(inumsys) eq 1 or naturesys(inumsys) eq 2) then begin
;  if (naturesys(inumsys) eq 0 or naturesys(inumsys) eq 1 or (naturesys(inumsys) eq 2 and coolratesys(inumsys) lt -30.)) then begin
;  if (naturesys(inumsys) eq 0 or naturesys(inumsys) eq 1 or ((naturesys(inumsys) gt 1 and coolratesys(inumsys) lt -30.))) then begin
  if (naturesys(inumsys) eq 0 or $
      naturesys(inumsys) eq 1) then begin
;      naturesys(inumsys) eq 1 or $
;      naturesys(inumsys) eq 2) then begin
;      ((naturesys(inumsys) eq 2 and phasesys(inumsys) eq 0)) or $
;      ((naturesys(inumsys) eq 2 and phasesys(inumsys) eq 1 and coolratesys(inumsys) lt -25.))) then begin
   print,' '
   print,' inumsys: ',inumsys
   print,' latsys: ',latsys(inumsys)
   print,' lonsys: ',lonsys(inumsys)
   print,' phasesys: ',phasesys(inumsys)
   print,' naturesys: ',naturesys(inumsys)
   print,' idsys: ',idsys(inumsys)
   print,' idbirthsys: ',idbirthsys(inumsys)
   print,' coolratesys: ',coolratesys(inumsys)
   print,' btthreshsys: ',btthreshsys(inumsys)
   print,' ctpsys: ',ctpsys(inumsys)
   print,' dirnsys: ',dirnsys(inumsys)
   print,' speedsys: ',speedsys(inumsys)
   print,' btminsys: ',btminsys(inumsys)
   print,' arearatesys: ',arearatesys(inumsys)
   print,' areasys: ',areasys(inumsys)
   print,' methodsys: ',methodsys(inumsys)
   print,' durationsys: ',durationsys(inumsys)
   print,' lflashpossys: ',lflashpossys(inumsys)
   print,' plot_lightning: ',plot_lightning(inumsys)
   ; this next bit is REALLY SLOW (if there are lots of convective objects), as currently coded!!!! (must be much more efficient ways of doing this...)
   for icpts=0,numcpts-1 do begin ; loop over points in contour for plotting
    c2min=999999.
    ; loop through image
    ; 0.15 is larger than the largest lat spacing and 0.25 is larger than the largest lon spacing
    for icol=0,1179 do begin
     for irow=0,1179 do begin
      if (abs(contlat(icpts)-lat(icol,irow)) lt 0.15 and abs(contlon(icpts)-lon(icol,irow)) lt 0.25) then begin ; feasible pixel
       c2=((contlat(icpts)-lat(icol,irow))*(contlat(icpts)-lat(icol,irow)) + (contlon(icpts)-lon(icol,irow))*(contlon(icpts)-lon(icol,irow)))
       if (c2 lt c2min) then begin
        cont_icol(icpts)=icol
        cont_irow(icpts)=irow
        c2min=c2
       endif
      endif
     endfor
    endfor
   endfor
;hak,mesg=' Hit any key to continue...'
  endif
  if (naturesys(inumsys) eq 0 or naturesys(inumsys) eq 1) then cont_icol=[cont_icol,cont_icol(0)] ; add first point on end to complete contour
  if (naturesys(inumsys) eq 0 or naturesys(inumsys) eq 1) then cont_irow=[cont_irow,cont_irow(0)] ; add first point on end to complete contour

  if (phasesys(inumsys) eq 0 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60.) then plots,cont_icol,cont_irow,color=6,thick=3,/device ; triggering
  if (phasesys(inumsys) eq 0 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and nested(inumsys) lt 1) then xyouts,max(cont_icol)+1,min(cont_irow)+1,string(coolratesys(inumsys),format='(i4)')+'!Uo!NC hr!U-1!N',color=6,/device ; don't annotate if nested, as gets too messy
  if (phasesys(inumsys) eq 0 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=3,line=1,/device ; triggering
  if (phasesys(inumsys) eq 1 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60.) then plots,cont_icol,cont_irow,color=3,thick=3,/device ; growing
  if (phasesys(inumsys) eq 1 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and nested(inumsys) lt 1) then xyouts,max(cont_icol)+1,min(cont_irow)+1,string(coolratesys(inumsys),format='(i4)')+'!Uo!NC hr!U-1!N',color=3,/device ; don't annotate if nested, as gets too messy
  if (phasesys(inumsys) eq 1 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=3,line=1,/device ; growing
  if (phasesys(inumsys) eq 2 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60.) then plots,cont_icol,cont_irow,color=7,thick=3,/device ; mature
  if (phasesys(inumsys) eq 2 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and nested(inumsys) lt 1) then xyouts,max(cont_icol)+1,min(cont_irow)+1,string(coolratesys(inumsys),format='(i4)')+'!Uo!NC hr!U-1!N',color=7,/device ; don't annotate if nested, as gets too messy
  if (phasesys(inumsys) eq 2 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=3,line=1,/device ; mature
  if (phasesys(inumsys) eq 3 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60.) then plots,cont_icol,cont_irow,color=5,thick=3,/device ; decaying
  if (phasesys(inumsys) eq 3 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and nested(inumsys) lt 1) then xyouts,max(cont_icol)+1,min(cont_irow)+1,string(coolratesys(inumsys),format='(i4)')+'!Uo!NC hr!U-1!N',color=5,/device ; don't annotate if nested, as gets too messy
  if (phasesys(inumsys) eq 3 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=3,line=1,/device ; decaying
  if (phasesys(inumsys) eq 4 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60.) then plots,cont_icol,cont_irow,color=8,thick=3,/device ; seem to be triggering from a split (so why "unused"?)
  if (phasesys(inumsys) eq 4 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and nested(inumsys) lt 1) then xyouts,max(cont_icol)+1,min(cont_irow)+1,string(coolratesys(inumsys),format='(i4)')+'!Uo!NC hr!U-1!N',color=8,/device ; don't annotate if nested, as gets too messy
  if (phasesys(inumsys) eq 4 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=3,line=1,/device ; seem to be triggering from a split (so why "unused"?)

  if (phasesys(inumsys) eq 0 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60.) then plots,cont_icol,cont_irow,color=6,thick=2,/device ; triggering
  if (phasesys(inumsys) eq 0 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=2,line=1,/device ; triggering
  if (phasesys(inumsys) eq 1 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60.) then plots,cont_icol,cont_irow,color=3,thick=2,/device ; growing
  if (phasesys(inumsys) eq 1 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=2,line=1,/device ; growing
  if (phasesys(inumsys) eq 2 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60.) then plots,cont_icol,cont_irow,color=7,thick=2,/device ; mature
  if (phasesys(inumsys) eq 2 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=2,line=1,/device ; mature
  if (phasesys(inumsys) eq 3 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60.) then plots,cont_icol,cont_irow,color=5,thick=2,/device ; decaying
  if (phasesys(inumsys) eq 3 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=2,line=1,/device ; decaying
  if (phasesys(inumsys) eq 4 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60.) then plots,cont_icol,cont_irow,color=8,thick=2,/device ; seem to be triggering from a split (so why "unused"?)
  if (phasesys(inumsys) eq 4 and naturesys(inumsys) eq 0 and coolratesys(inumsys) lt -30. and coolratesys(inumsys) ge -60. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,thick=2,line=1,/device ; seem to be triggering from a split (so why "unused"?)

  ; don't plot if not a valid cooling rate
  if (phasesys(inumsys) eq 0 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999.) then plots,cont_icol,cont_irow,color=6,/device ; triggering
  if (phasesys(inumsys) eq 0 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,line=1,/device ; triggering
  if (phasesys(inumsys) eq 1 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999.) then plots,cont_icol,cont_irow,color=3,/device ; growing
  if (phasesys(inumsys) eq 1 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,line=1,/device ; growing
  if (phasesys(inumsys) eq 2 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999.) then plots,cont_icol,cont_irow,color=7,/device ; mature
  if (phasesys(inumsys) eq 2 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,line=1,/device ; mature
  if (phasesys(inumsys) eq 3 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999.) then plots,cont_icol,cont_irow,color=5,/device ; decaying
  if (phasesys(inumsys) eq 3 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,line=1,/device ; decaying
  if (phasesys(inumsys) eq 4 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999.) then plots,cont_icol,cont_irow,color=8,/device ; seem to be triggering from a split (so why "unused"?)
  if (phasesys(inumsys) eq 4 and naturesys(inumsys) eq 0 and coolratesys(inumsys) ge -30. and coolratesys(inumsys) lt 999. and plot_lightning(inumsys) le 0) then plots,cont_icol,cont_irow,color=0,line=1,/device ; seem to be triggering from a split (so why "unused"?)

  if (phasesys(inumsys) eq 0 and naturesys(inumsys) gt 0 and naturesys(inumsys) le 1) then plots,cont_icol,cont_irow,color=4,/device ; ?
  if (phasesys(inumsys) eq 1 and naturesys(inumsys) gt 0 and naturesys(inumsys) le 1) then plots,cont_icol,cont_irow,color=4,/device ; ?
  if (phasesys(inumsys) eq 2 and naturesys(inumsys) gt 0 and naturesys(inumsys) le 1) then plots,cont_icol,cont_irow,color=4,/device ; ?
  if (phasesys(inumsys) eq 3 and naturesys(inumsys) gt 0 and naturesys(inumsys) le 1) then plots,cont_icol,cont_irow,color=4,/device ; ?
  if (phasesys(inumsys) eq 4 and naturesys(inumsys) gt 0 and naturesys(inumsys) le 1) then plots,cont_icol,cont_irow,color=4,/device ; ?

 endif

endfor

close,1

tvlct,  3,  3,  3,3 ; reset 3
tvlct,  4,  4,  4,4 ; reset 4
tvlct,  5,  5,  5,5 ; reset 5
tvlct,  6,  6,  6,6 ; reset 6
tvlct,  7,  7,  7,7 ; reset 7
tvlct,  8,  8,  8,8 ; reset 8
tvlct,  9,  9,  9,9 ; reset 9

end
