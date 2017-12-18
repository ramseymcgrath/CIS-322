from acp_times import open_time, close_time
import arrow
import nose

def test_control_open():
    #testing open_time function
    begintime = arrow.utcnow()
    assert open_time(100, 400, begintime) == begintime.shift(hours=(100/34)).isoformat() 

def test_control_close():
    #testing close_time function
    closetime = arrow.utcnow()
    assert close_time(100, 800, closetime) == closetime.shift(hours=100/15).isoformat()

def test_first_control():
    #test if control time is 0
    closetime = arrow.utcnow()
    assert close_time(0, 1000, closetime) == closetime.shift(hours=1).isoformat()

def test_200brev_endtime():
    #to test the endtime of 200km brevet
    closetime = arrow.utcnow()
    addedminutes = closetime.shift(minutes=10)
    assert close_time(200, 200, closetime) == addedminutes.shift(hours=200/15).isoformat()

def test_400brev_endtime():
    #to test endtime of 400km brevet
    closetime = arrow.utcnow()
    addedminutes = closetime.shift(minutes=20)
    assert close_time(400, 400, closetime) == addedminutes.shift(hours=400/15).isoformat()

def test_20perc_open():
    #Test to see if we're within 20%, including false cases
    begintime = arrow.utcnow()
    assert open_time(240, 200, begintime) == begintime.shift(hours=200/34).isoformat()
    assert open_time(241, 200, begintime) == False
    assert open_time(360, 300, begintime) == begintime.shift(hours=200/34 + 100/32).isoformat()
    assert open_time(361, 300, begintime) == False