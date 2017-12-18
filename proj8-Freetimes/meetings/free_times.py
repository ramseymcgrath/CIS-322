import arrow # Replacement for datetime, based on moment.js
import busy_times
import general_time_helpers

def convertBusyToAvailable(merged_busy_times, begin_datetime, available_times):
  for busy_time in merged_busy_times:
      converted = convertJunkDTVals(busy_time, begin_datetime)
      if begin_datetime < converted:
          available_times.append({'start': begin_datetime.format("ddd MM/DD/YYYY HH:mm"), 'end': converted.datetime})
          begin_datetime = converted
  return begin_datetime

def find_free_times(service, calendars, range):
    range_split = range.split()
    beginDT = range_split[0]
    begin_datetime = arrow.get(beginDT).isoformat()
    
    endDT = range_split[2]
    end_datetime = arrow.get(endDT).isoformat()

    merged_busy_times = []
    available_times = []

    busy_blocks = busy_times.find_times_busy(service,begin_datetime,end_datetime)
    if len(busy_blocks)>0:
        appendMergedBusyTimes(busy_blocks, merged_busy_times)

        begin_datetime = convertBusyToAvailable(merged_busy_times, begin_datetime, available_times)

        if begin_datetime < end_datetime:
            available_times.append({'start': begin_datetime.format("ddd MM/DD/YYYY HH:mm"), 'end': end_datetime.format("ddd MM/DD/YYYY HH:mm")})
        return available_times
    else:
        return {'start': begin_datetime.format("ddd MM/DD/YYYY HH:mm"), 'end': end_datetime.format("ddd MM/DD/YYYY HH:mm")}

def appendMergedBusyTimes(busy_times, merged_busy_times):
  elem = None
  for x in busy_times[0]:
    dateArray_start = arrow.get(x['start'])
    dateArray_end = arrow.get(x['end'])
    if elem is not None:
        if dateArray_start <= elem['end'] and dateArray_end >= elem['end']:
            elem['end'] = dateArray_end
            continue # Go to next iteration of loop
        else:
            merged_busy_times.append({'start': elem['start'].datetime, 'end': elem['end'].datetime})

    elem = {'start': dateArray_start, 'end': dateArray_end}

  merged_busy_times.append({'start': dateArray_start.datetime, 'end': dateArray_end.datetime})