from abc import abstractmethod

import wx


class TimeEntryController:
	@abstractmethod
	def refreshLaps(self) -> None:
		pass

class ManualTimeEntryPanel( wx.Panel, TimeEntryController ):
	_disableReason: str | None = None
	_infoBar: wx.InfoBar
	_infoBarSizer: wx.BoxSizer

	def __init__(self, parent: wx.Window, controller: TimeEntryController | None = None, id = wx.ID_ANY):
		super().__init__(parent, id)
		self._disableReason = None
		self._controller = controller

		self.SetBackgroundColour( wx.WHITE )

		self._infoBarSizer = wx.BoxSizer(wx.VERTICAL)
		self._infoBar = wx.InfoBar(self)
		self._infoBarSizer.Add(self._infoBar, 0, wx.EXPAND | wx.ALL, 5)

		self._contentSizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self._contentSizer, False)

		super().SetSizer(self._infoBarSizer)

		self.Layout()


	def SetSizer(self, sizer: wx.Sizer, deleteOld=True) -> None:
		if deleteOld:
			self._infoBarSizer.Remove(self._contentSizer)

		self._infoBarSizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)
		self._contentSizer = sizer
		self.Layout()

	def SetSizerAndFit(self, sizer, deleteOld=True):
		self.SetSizer(sizer, deleteOld)
		self.Fit()

	def GetSizer(self) -> wx.Sizer:
		return self._contentSizer

	def refreshLaps(self) -> None:
		if self._controller:
			self._controller.refreshLaps()

	@abstractmethod
	def _DisableControls(self) -> None:
		pass

	@abstractmethod
	def _EnableControls(self) -> None:
		pass

	def Disable(self, disable: bool=True, reason:str | None = None) -> None:
		assert isinstance(disable, bool)
		if disable is True:
			if reason is None:
				self._disableReason = None
				message = 'Control is disabled.'
			else:
				self._disableReason = reason
				message = f'Control is disabled: {self._disableReason}'

			self._infoBar.ShowMessage(message, wx.ICON_WARNING)
			self._DisableControls()
		else:
			self.Enable()

	def Enable( self, enable=True ) -> None:
		if enable is True:
			self._disableReason = None
			self._infoBar.Dismiss()
			self._EnableControls()
		else:
			self.Disable()