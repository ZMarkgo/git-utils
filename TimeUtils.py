import time

class Timer:
    def __init__(self) -> None:
        self.time_start = time.time()
        self.time_end = None
    
    def end(self):
        self.time_end = time.time()
    
    def get_time_cost_in_seconds(self):
        return self.time_end - self.time_start
    
    def get_time_cost_in_minutes(self):
        return (self.time_end - self.time_start) / 60
    
    def get_time_cost_in_hours(self):
        return (self.time_end - self.time_start) / 3600

    def show_time_cost(self):
        print(f'Time cost: {self.get_time_cost_in_seconds():.2f}s or {self.get_time_cost_in_minutes():.2f}m or {self.get_time_cost_in_hours():.2f}h')
        