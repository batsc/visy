program test_time

implicit none

integer :: t(5)
character (len=200) :: yr, mo, da, ho, mi

call get_command_argument(1, yr)
call get_command_argument(2, mo)
call get_command_argument(3, da)
call get_command_argument(4, ho)
call get_command_argument(5, mi)

read(yr,'(i4)') t(1)
read(mo,'(i2)') t(2)
read(da,'(i2)') t(3)
read(ho,'(i2)') t(4)
read(mi,'(i2)') t(5)

print*, hours_since(t)

contains
  real function hours_since(time_array)
    integer, dimension(:), intent( in) :: time_array(5) ! Year, Month, Day, Hour, Minute

    integer, dimension(:) :: time_since(5)
    integer :: yr, mon
    integer :: num_days
    integer, dimension(12) :: months = &
      (/ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 /)

    ! Default since 1970-01-01T00:00
    time_since(1) = 1970
    time_since(2) = 1
    time_since(3) = 1
    time_since(4) = 0
    time_since(5) = 0

    num_days = 0
    do yr = time_since(1), time_array(1) - 1
      num_days = num_days + 365
      if (is_leap_year(yr)) num_days = num_days + 1
    end do

    do mon = time_since(2), time_array(2) - 1
      num_days = num_days + months(mon)
    end do
    if (is_leap_year(time_array(1)) .and. time_array(2) > 2) then
      num_days = num_days + 1
    end if

    num_days = num_days + time_array(3) - 1

    hours_since = num_days * 24 + time_array(4) + time_array(5) / 60.0
  end function hours_since

  logical function is_leap_year(yr)
    integer, intent( in) :: yr
    if ( (mod(yr, 100) /= 0 .and. mod(yr, 4) == 0) .or. (mod(yr, 400) == 0) ) then
      is_leap_year = .true.
    else
      is_leap_year = .false.
    end if
  end function is_leap_year
end program test_time