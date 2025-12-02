import csv
import uuid

class timesheets():
  def __init__(self, 
               period_start, 
               period_end,
               hours,
               exception,
               wps,
               wps_weights,
               month,
               year
    ) -> None:

      self.period_start = period_start
      self.period_end = period_end + 1
      self.hours = hours
      self.exception = exception
      self.wps = wps
      self.wps_weights = wps_weights
      self.month = month
      self.year = year
      
      self.filepath = ""
      self.error = ""

      self.prepare_timetable()
      self.r = self.calculate_hours_per_day()
      if self.r == 0:
        self.calculate_hours_per_wps()
        self.add_wps_to_timetable()
        self.create_csv()
      

  def available_slots(self):
    for i in range(len(self.timetable)):
      if self.timetable[i]["active"] and self.timetable[i]["value"] < 8:
        return True
    return False


  def spread_residual(self, residual):
    i = 0
    while (residual > 0 and self.available_slots()):
      if self.timetable[i]["active"] and self.timetable[i]["value"] <= 8:
        self.timetable[i]["value"] += 1
        residual -= 1
      i += 1
      if i == len(self.timetable):
        i = 0

    if residual > 0:
      self.error = f"The given hours do not fit in the given days. {residual} hours exeed the limit"
      return 1
      # raise ValueError(f"The given hours do not fit in the given days. {residual} hours exeed the limit")
    
    return 0


  def calculate_hours_per_day(self):
    if self.period_start > self.period_end:
      raise ValueError(f"Expected period_end > period_start. \
                                              Got period_start > period_end")
      
    count = 0
    for i in range(len(self.exception)):
      if (self.exception[i] >= self.period_start and self.exception[i] <= self.period_end-1):
        count += 1
    
    days = self.period_end - self.period_start - count
    hours_per_day = self.hours // days
    
    residual = self.hours % days
    
    if hours_per_day > 8:
      res = days * (hours_per_day - 8)
      self.error = f"The given hours do not fit in the given days. {res} hours exceed the limit."
      return 1
      # raise ValueError(f"The given hours do not fit in the given days.")
    
    
    for i in range(len(self.timetable)):
      if self.timetable[i]["active"]:
        self.timetable[i]['value'] = hours_per_day
      else:
        self.timetable[i]["value"] = 0

    if residual > 0:
      r = self.spread_residual(residual)
      return r
    
    return 0


  def prepare_timetable(self):
    self.timetable = [{"day": i, "active": True, "value": 0} for i in \
                                range(self.period_start, self.period_end)]
    for i in range(len(self.timetable)):
      if self.timetable[i]["day"] in self.exception:
        self.timetable[i]["active"] = False


  def calculate_hours_per_wps(self):

    self.wps_info = [{"name": self.wps[i], 
                      "hours": int(self.hours*self.wps_weights[i])} 
                                      for i in range(len(self.wps))]

    res = self.hours - sum(self.wps_info[i]["hours"] 
                        for i in range(len(self.wps_info)))
    i = 0
    while res > 0:
      self.wps_info[i]["hours"] += 1
      res -= 1
      i += 1
  

  def add_wps_to_timetable(self):
    
    self.timesheet = []
    for i in range(len(self.timetable)):
      flag = False
      for j in range(len(self.wps_info)):
        self.timesheet.append(self.timetable[i] | 
            {"wp": self.wps_info[j]["name"], "wp_done": False})
        if self.wps_info[j]["hours"] > 0 and not flag:
          self.wps_info[j]["hours"] -= self.timetable[i]["value"]
          self.timesheet[len(self.timesheet)-1]["wp_done"] = True
          flag = True
        else:
          self.timesheet[len(self.timesheet)-1]["value"] = 0

  def create_csv(self):
    filepath = f"timesheet_{uuid.uuid4()}.csv"
    with open(filepath, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
      writer.writerow(['day', 'wp', 'hours'])
      
      for i in range(1, self.period_start):
        for j in range(len(self.wps_info)):
          writer.writerow([f'{i}-{self.month}-{self.year}', \
                                self.wps_info[j]["name"], '0'])
          
      for i in range(len(self.timesheet)):
        writer.writerow([f'{self.timesheet[i]["day"]}-{self.month}-{self.year}', \
                                self.timesheet[i]["wp"], \
                         self.timesheet[i]["value"]])
      
      for i in range(self.period_end, 31):
        for j in range(len(self.wps_info)):
          writer.writerow([f'{i}-{self.month}-{self.year}', \
                                self.wps_info[j]["name"], '0'])
    
    self.filepath = filepath