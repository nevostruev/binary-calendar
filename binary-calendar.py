#!/usr/bin/env python

import argparse
import datetime

class SVGOutput:
	def __init__(self, colors):
		self.colors = colors

	def draw_calendar(self, calendar):
		box_size = 15
		between_months = 20
		border_size = 20
		width = calendar.get_month_count() * calendar.get_bit_count() * box_size + (calendar.get_month_count() - 1) * between_months + border_size * 2
		height = calendar.get_day_count() * box_size + border_size * 2
		print '<svg width="%dpx" height="%dpx" xmlns="http://www.w3.org/2000/svg" version="1.1">' % (width, height)
		for month in range(calendar.get_month_count()):
			for bit in reversed(range(calendar.get_bit_count())):
				x = border_size + (month * calendar.get_bit_count() + calendar.get_bit_count() - bit - 1) * box_size + month * between_months
				for day in range(calendar.get_day_count()):
					y = border_size + day * box_size
					if calendar.get_bit(month, day, bit):
						day_type = calendar.get_day_type(month, day)
						style = ""
						if day_type == DayType.WORKDAY:
							style = "fill:%s" % self.colors['workday']
						elif day_type == DayType.HOLIDAY:
							style = "fill:%s" % self.colors['holiday']
						else:
							style = "fill:%s" % self.colors['weekend']
						style += ";stroke:%s;stroke-width:0.1" % self.colors['line']
						print '<rect x="%d" y="%d" width="%d" height="%d" style="%s" />' % (x, y, box_size, box_size, style)
		print '</svg>'

class ConsoleOutput:
	def draw_calendar(self, calendar):
		for day in range(calendar.get_day_count()):
			for month in range(calendar.get_month_count()):
				for bit in reversed(range(calendar.get_bit_count() + 2)): ## make some space between months
					if calendar.get_bit(month, day, bit):
						day_type = calendar.get_day_type(month, day)
						if day_type == DayType.WORKDAY:
							print "#",
						elif day_type == DayType.HOLIDAY:
							print "!",
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
	def render_calendar(self, year, holidays, renderer):
		calendar = self.make_calender(year, self.parse_holidays(holidays))
		renderer.draw_calendar(calendar)
	def parse_holidays(self, holidays):
		holiday_map = {}
		for holiday_str in holidays:
			(month, ignore, day) = holiday_str.partition('-')
			holiday_map[(int(month),int(day))] = 1
		return holiday_map
	def make_calender(self, year, holidays):
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
			if (current_date.month, current_date.day) in holidays:
				day_type = DayType.HOLIDAY
			elif current_date.weekday() in [5, 6]: ## Saturday, Sunday
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
	arg_parser.add_argument('--output', choices = ['text', 'svg', 'svg-bw'], default = 'text', nargs = '?')
	arg_parser.add_argument('--holiday', nargs = '*', help = 'holiday date in mm-dd format', default = [])
	args = arg_parser.parse_args()
	binary_calendar = BinaryCalendar()
	output = ConsoleOutput()
	if args.output == 'svg':
		output = SVGOutput({'workday': 'green', 'holiday': 'yellow', 'weekend': 'red', 'line': 'black'})
	if args.output == 'svg-bw':
		output = SVGOutput({'workday': '#ddd', 'holiday': '#333', 'weekend': '#aaa', 'line': 'black'})
	binary_calendar.render_calendar(args.year, args.holiday, output)
