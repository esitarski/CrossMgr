from typing import Any

import wx, wx.adv
from wx.adv import DatePickerCtrl

import Utils

class SafeDatePickerCtrl(DatePickerCtrl):
	def __init__(self,
             *args: Any,
             **kw: Any) -> None:
		style = kw.pop('style', wx.adv.DP_DROPDOWN)
		dt = kw.pop('dt', Utils.GetDateTimeToday())
		super().__init__(style=style, dt=dt, *args, **kw)

		currentRange = self.GetRange()
		if not currentRange or not len(currentRange) == 2:
			minRange = wx.DateTime.FromDMY(1, 0, 1900)
			maxRange = wx.DateTime.FromDMY(1, 0, 2200)
		else:
			minRange = currentRange[1].Value
			maxRange = currentRange[2].Value

		if currentRange[2].Inv_Year < 1601:
			maxRange = wx.DateTime.FromDMY(1, 0, 2200)

		super().SetRange(
			dt1=minRange,
			dt2=maxRange
		)

