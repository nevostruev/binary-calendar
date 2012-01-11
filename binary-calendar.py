#!/usr/bin/env python

import argparse
import datetime

class ConsoleOutput:
	def __init__(self):
		self.boxes = {}
	def draw_calendar(self, calendar):
		for day in range(calendar.get_day_count()):
			for month in range(calendar.get_month_count()):
				for bit in reversed(range(calendar.get_bit_count() + 2)): ## make some space between months
					if calendar.get_bit(month, day, bit):
						day_type = calendar.get_day_type(month, day)
						if day_type == DayType.WORKDAY:
							print "#",
						else:
							print ".",
					else:
						print " ",
			print

class Calendar:
	def __init__(self, months):
		self.months = months
		self.max_month_index = len(months)
		self.max_day_index = max(len(month.days) + month.offset for month in months)
		self.max_bit_index = max(len(day.as_bin()) for month in months for day in month.days)
	def get_month_count(self):
		return self.max_month_index
	def get_day_count(self):
		return self.max_day_index
	def get_bit_count(self):
		return self.max_bit_index
	def get_bit(self, month, day, bit):
		if month < len(self.months):
			selected_month = self.months[month]
			if day < len(selected_month.days) + selected_month.offset and day >= selected_month.offset:
				bit_str = selected_month.days[day - selected_month.offset].as_bin()
				if bit < len(bit_str):
					return bit_str[len(bit_str) - bit - 1] == '1'
		return 0
	def get_day_type(self, month, day):
		if month < len(self.months):
			selected_month = self.months[month]
			if day < len(selected_month.days) + selected_month.offset and day >= selected_month.offset:
				return selected_month.days[day - selected_month.offset].day_type
		return None

class Month:
	def __init__(self, number, days, offset):
		self.number = number
		self.days = days
		self.offset = offset
	def __str__(self):
		return "%d month (%d)" % (self.number, self.offset)

class DayType:
	WORKDAY = "workday"
	WEEKEND = "weekend"
	HOLIDAY = "holiday"

class Day:
	def __init__(self, number, day_type):
		self.number = number
		self.day_type = day_type
	def __str__(self):
		return "%s %s" % (self.number, self.day_type)
	def as_bin(self):
		return bin(self.number)[2:]

class BinaryCalendar:
	def render_calendar(self, year):
		calendar = self.make_calender(year)
		renderer = ConsoleOutput()
		renderer.draw_calendar(calendar)
	def make_calender(self, year):
		current_date = datetime.date(year, 1, 1)
		delta = datetime.timedelta(1)
		months = []
		current_month = []
		current_month_offset = current_date.weekday()
		#first_day_offset = 7 - current_date.weekday() ## make January 1st always on top
		first_day_offset = 0 ## make calendar start from Monday
		prev_month = 1
		while current_date.year == year:
			#print current_date
			if prev_month != current_date.month:
				months.append(Month(prev_month, current_month, self._shift_weekday(current_month_offset, first_day_offset)))
				current_month = []
				current_month_offset = current_date.weekday()
			if current_date.weekday() in [5, 6]: ## Saturday, Sunday
				day_type = DayType.WEEKEND
			else:
				day_type = DayType.WORKDAY
			current_month.append(Day(current_date.day, day_type))
			prev_month = current_date.month
			current_date += delta
		months.append(Month(prev_month, current_month, self._shift_weekday(current_month_offset, first_day_offset)))
		return Calendar(months)
	def _shift_weekday(self, weekday, offset):
		return (weekday + offset) % 7


if __name__ == "__main__":
	arg_parser = argparse.ArgumentParser(description = 'Generate banary calandar in SVG format')
	arg_parser.add_argument('year', type=int)
	args = arg_parser.parse_args()
	binary_calendar = BinaryCalendar()
	binary_calendar.render_calendar(args.year)
