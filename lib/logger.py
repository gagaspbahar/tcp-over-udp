class Logger:
  WARNING = "\033[91m"
  ASK = "\033[93m"
  OK = "\033[92m"
  ENDC = "\033[0m"

  def __init__(self, name):
    self.name = name
  
  def warning_log(self, msg):
    print(f"{self.WARNING}[{self.name}]{self.ENDC} {msg}")
  
  def ask_log(self, msg):
    print(f"{self.ASK}[{self.name}]{self.ENDC} {msg}")
  
  def ok_log(self, msg):
    print(f"{self.OK}[{self.name}]{self.ENDC} {msg}")
