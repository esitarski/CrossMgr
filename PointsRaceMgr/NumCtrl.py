import wx
import string

class NumCtrl(wx.TextCtrl):
  '''
  https://stackoverflow.com/questions/1369086/is-it-possible-to-limit-textctrl-to-accept-numbers-only-in-wxpython
  '''
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.Bind(wx.EVT_CHAR, self.onChar)

  def onChar(self, event):
    keycode = event.GetKeyCode()
    obj = event.GetEventObject()
    val = super().GetValue()
    # filter unicode characters
    if keycode == wx.WXK_NONE:
      pass
    # allow digits
    elif chr(keycode) in string.digits:
      event.Skip()
    # allow special, non-printable keycodes
    elif chr(keycode) not in string.printable:
      event.Skip()  # allow all other special keycode
    # allow '-' for negative numbers
    elif chr(keycode) == '-':
      if '-' not in val:
        obj.SetValue('-' + val)
        obj.SetInsertionPointEnd()
      else:
        obj.SetValue(val[1:])
        obj.SetInsertionPointEnd()
    # allow '.' for float numbers
    elif chr(keycode) == '.' and '.' not in val:
      event.Skip()
    return

  def SetValue(self, value):
    try:
      value = float(value)
    except Exception:
      value = 0.0
    super().SetValue( '{:.2f}'.format(value) )

  def GetValue(self):
    try:
      return float(super().GetValue())
    except ValueError as e:
      return 0.0

class PosNumCtrl(wx.TextCtrl):
  '''
  https://stackoverflow.com/questions/1369086/is-it-possible-to-limit-textctrl-to-accept-numbers-only-in-wxpython
  '''
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.Bind(wx.EVT_CHAR, self.onChar)

  def onChar(self, event):
    keycode = event.GetKeyCode()
    obj = event.GetEventObject()
    val = super().GetValue()
    # filter unicode characters
    if keycode == wx.WXK_NONE:
      pass
    # allow digits
    elif chr(keycode) in string.digits:
      event.Skip()
    # allow special, non-printable keycodes
    elif chr(keycode) not in string.printable:
      event.Skip()  # allow all other special keycode
    # allow '.' for float numbers
    elif chr(keycode) == '.' and '.' not in val:
      event.Skip()
    return

  def SetValue(self, value):
    try:
      value = abs(float(value))
    except Exception as e:
      print( e )
      value = 0.0
    super().SetValue( '{:.2f}'.format(value) )

  def GetValue(self):
    try:
      return float(super().GetValue())
    except ValueError as e:
      return 0.0
