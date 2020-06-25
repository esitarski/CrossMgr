import wx
import wx.richtext as rt
from wx.lib.embeddedimage import PyEmbeddedImage
from io import StringIO

#----------------------------------------------------------------------
_rt_alignleft = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAEJJ"
    "REFUOI1jZGRiZqAEMFGkm4GBgYWBgYHBx9vrPzmat2zdxshIqRdIcsGWrdsY0cXo6wJsLhoN"
    "g2ERBhRnJooNAACQdhhQZbXeGAAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_alignright = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAADxJ"
    "REFUOI1jZGRiZqAEMFGkm4GBgYWBgYHBx9vrPzmat2zdxshIqRdYsAkS6yLquWA0DEZ8GFCc"
    "mSg2AADQZxhQFG0xxgAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_bold = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAEtJ"
    "REFUOI3NUkEKACAMyq3//7jWNQwWY0HzKNOJCIi2DCSlfmHQmbA5zBNAFG4CPoAodo4fFOyA"
    "wZGvHTDqdwCecnQHh0EU/ztIGyy1dBRJuH/9MwAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_centre = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAEJJ"
    "REFUOI1jZGRiZqAEMFGkm4GBgYWBgYHBx9vrPzmat2zdxshIqRdYkDnEumTL1m2MMDZ1XDAa"
    "BiM+DCjOTBQbAAAwdhhQDziCqAAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_colour = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAPZJ"
    "REFUOI1jZGRiZqAEsOCS+Mcu9h+bONPPV4wofEKa37Lz4zWYEd0LuGzG5RKsLiAFDEIDllTz"
    "MWxtyGJ4yiWKofgfCyTSkGMCJRDd/hr/Z2BgYGCZ5cAg8v0jg++C9wy6zx8ysP37zfCYXYFh"
    "g1gww+VfUSiGwg2AaRZ/JcPw6v0fhv/qLxg4vv1jCOv5zPBvZgrDSukghp8/ZRkY/rFiGgDT"
    "jBV84mX4572WgekzL8O/v5hBxoRXMwMDw/+3QgwM/3CHNeFY+MvMwMDyE6vtRBnAKPqWgUH2"
    "OQUu4P/IwGh8HrcFBAORgYFhF/NZRhetP1jVAACsCFJPHjA77wAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_copy = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAATlJ"
    "REFUKJGFk71OwzAURo/tpE2AdihiAAmQWNiKWICpDIhnQEi8A0+ASsXAzDsgIcTEA3QANsZu"
    "XTMQBiqkUkFF04aB2sRJSO90bV+f+33+EUIqzq7bMam471UA6JzuiPRaMqROltc2KS9tMFhY"
    "JVArAJw31qlfPWfguYCqp6j5Lou+S81XpmAWRGgLe1t13r8i+sMxYdAtasrFyYGx5eik4v11"
    "DYHW8T6dl0/6w4i3wYjXjxFh0KV51ADasYYYQNUzKXlQDQYsiNnluzLJA6CsBKQgrdtHa2x2"
    "zJdkeoq5koLvsYEc7m5bdqxqRwk8V5C4GFwlDCRKKdR2Egq01IkpUhJgCsmKtkdKJiHTOSFA"
    "xoWQ7NFbgF8F+ZAU4PLuKbMopYBJXAhxwH5ZgPW5ZkH+tdC8eShyZ+IHUNNZHhrzal0AAAAA"
    "SUVORK5CYII=")

#----------------------------------------------------------------------
_rt_cut = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAAbBJ"
    "REFUKJGdk0FLG1EQx3/vpRdv7sG49CKYxvSmVDwkpd78ALbSShQkbU81guAH8BN4EE0KGlCQ"
    "5iAIoiaIwWAP3bi0WXZLW1q2WfGmJ8mhV19Pu+xqWsSBx/Bm/vObmQcPIWP4Jz83r96vb6pw"
    "LJxzXfdWThKyuJR8/2rjOI4Kxz8ZDQUwkHosuGERwOLKsohLydpaKSIqfyjfrOsM8C2VSlKr"
    "1RRAtVJRAK8mJ+8GWFxZFldui93dPTzvTFWqhwCMPnt6a3yAB52CWjLBSCLBwcH+P0f/7wpX"
    "bouLywvys+/uB9CSCfRendVCkezMm/tN8PnwiKHBQX59axKXHWUACCFjAHyp15VX2gIgbdg0"
    "MkO8LG+I7WxO+XeARwt5ngwPBw8q/eLe1wtI75y25QTCsG9bDtI7p+fFW6xmU0UAXmkLU9eY"
    "OK0LNf0cIOji+4ezOSZO68LUNX4vrUbfIG3YXPf3AdD9o4Wpa5E9TV3jT8MC4Lq/j7RhRwGm"
    "rtG2HPx9u6bGI4CuqXHShs12NqfalhNtIGSMn8cnaiczpnYyY6paKHb8jdVCMdA0Tz4Gmr9P"
    "zKg0oZ3GfwAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_font = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAIpJ"
    "REFUOI21k8ENgCAMRSmMpwzAgenUsgDMhweCgUpRJDYhJG362v8DAFKJmZBT3W8A67LFz4Bj"
    "T835HgY4V99DADqV24IF5Kk+WOht0QTkabm5twW03kHPeQoVIFV1EDFqjZHmtU55xLp2k8Bp"
    "NaZdrwCcdhqlF5cHVHcJ4TzxwULTxJH4/zM9xQmi7UCACkKFWgAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_idea = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAVtJ"
    "REFUWIXtl2FOwkAQhd8u3gAJp1EXuQEBrmOU24DxBtoWjmA8BAlXsOsPXNjadjtvRImJ708T"
    "pnS+fTudnRpjezinLjR/Wq5K//W3+cwazbMM40BIPJ3c1GKPT4UKRASQShxruyuwWYMC6QRY"
    "rkpfTZwBGCUhAGCzlkFYCeUxcTW5Ma521/Ay7RIFcFx9VouF5E0QAHB13VysFEBd7dbHYlxo"
    "BUitXgohcYFwQLZ6VoJGpE+834oieQ9ZA5zCK3kWAEnyJMB8Zk1or1pJmpHaAe/zylUrRSvu"
    "VjgTJK1YdRwD1Q4YuyDd+6DOLWBqgT2IAGIekGwFY30QVYQpJ+JZgJEYILUqzSASRBXh2+sd"
    "Bn3XGBv0gTzPASyYR/JvwT7J6UQDOOdaYxq4fwcogPuHhQHQOuF8xilRHyaxspfnA8jodqz6"
    "KvoWgC/fDwDG9n4f4FT60ZHsTwB8AA6FjDfFEDh8AAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
_rt_indentless = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAHRJ"
    "REFUOI3Nkm8KgCAMxfe2TlftCJ0u6ATa9eyTIqZiKdEDYfj25+eQwEKlo6qu5oOFABbq0eSD"
    "dZldbBh7Ir3LaSTB7ozdEJstBOyL3xJA9bgVpyTVBmAJBK1PMPYMefx0YpagR7/6B2WCeGnD"
    "CbhmfrKDC/GuLg9MR0atAAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
_rt_indentmore = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAHlJ"
    "REFUOI3NkmEKgCAMhbfZ6aododMJncB5PftlTE2TkuiBID7f9jkEJAO1xcyh5SMZQCQDbzTF"
    "zbrMQRtOPOZnVxpJYIOTDbXZQ0BpwN4GciHzXoRykmaBOIPYXYdrT3DizzuUGv2dC4Kn+tU/"
    "qBPooQ0noJb5yQwOwa4uD/KzgEcAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
_rt_italic = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAGdJ"
    "REFUOI3Vk1EOgDAIQwt4/2P0lopfS6YOgsEfl+xntK8kMBE1dI623F8Atqzox+73N1GTcgez"
    "mOTDPEThJekAHIBHmhQwzCTfAyrpKaCSHgKq6SGgmi5qkHmVV3Nfzf5S+/9faANOrocplI0e"
    "xSoAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
_rt_open = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAAbpJ"
    "REFUKJGlkz1IW1EUx39X3zNRgwFBMaCoQ0sFJwfpICgBccgkQQlOIUWE0lJCVTS0KWhU0KhY"
    "LeigoIMaQXCwgx9YR3XoIC2lpYMu4uLg0/jy8gLPQfLwGePimc79n3t+5+NyhcjJ5TkmPSbW"
    "BwaM++ejhbDICqjy9hoPxaOFsKgPDBirUQ8APjCyQSSAd54mi7hVUWZE/B583TGmwy9YjXqy"
    "QkR1W7/xEKBoOopyxXXihuPTc758dFDjasTdGTPvnKyPCoCcx9oqssmUlxTzqqI8Izb9oSNz"
    "BICZ7/uWQKnTYfqq8QdoBOD91DIAVd5eo7bSZX2Fr2992GUZm02mZ26NN8M/AbgAdpKD9H+D"
    "5rzPuDtj/F0Zwts3czeCoqoAxFWNhK6jaTpjXe3Mh+osXaWTfy2G2T74jbmDpb1DAi0NXN0k"
    "LJCIv9WEpJMPZ0Noeoq5jR9sTgSFOUKBJKFpuqWiXZaJ+Fv5FIKRyxg740GSqSSQZ13i65fV"
    "KKpKEfkZW09DnMWFxNW7Av9Oz6wAhz0XXUuhkB2SiCehEFBhcm2LzYmgAJCcBXZ2j/9nJD1l"
    "tZUu0xfP/Y230rSdugX3RssAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
_rt_paste = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAAXNJ"
    "REFUKJGFkzsvREEYhp/vzDnWWHuxdnsJjd+wRKPYgkIUKqHVKtYlQoi4FX6BiGQTolEpFBIU"
    "/gUJtbXWdSMuo1jGHueceJvJN5nvmff9JiPiKH6UL5YMITrfGJWwfQARR5EvlsxY8pqr6gvL"
    "60u+A3NT8wCcOd2hICdfLJmT/k+AQPPPXke6hcP241CHbmOxtboW5TRS0jO9a06HM5j7MgAf"
    "lRsAzE2N15cLBm77A02NURxLSmUBUJlcvc5pYi1dAGxODDI7WgDgaHHEF8UBkERbJAQgrV2y"
    "rZ510AixM5BEG+bxDkllMfdlVCZn46T071MXFvZ9cVwAiScxzw+hEIAm5ZDSsD05RLX2Tvnp"
    "jZXS0S8AnUAgFALQ7AlQh/yVHSI6gcSTNo5vJiI0e/LtRJHWrh8gno6EAHhKLCTepHwzqaNi"
    "McRVmNpTIA5U6J3ZC3r3AZz6IroV3j8wYCFn4532cN/OZeA/uAC98weRN/ynL78NdulpYuMM"
    "AAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
_rt_redo = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAAg5J"
    "REFUKJGdkr9rU1EcxT/3vbz2vfS924qRpmopVmIsFCWDiFkCAXHs5CDoJqSrJIP+BS5tXCw0"
    "EHDo4FBUguDgULVQImJJLe0Qu2hqWyKNMT9q0p/XofRHmtrBA9/l3HPPPffcK4Sms4fxyRn1"
    "NDXFYqG0z4Wv+kg+uC34B8SeQTSRUq/S87SbLU2iUn2D6/5unj+612AUTaSUEJpO/OV7Nfb2"
    "Mx5TA2B9W6OyuYVjuGjVdxq4zGhMHD5QCE0nFB1RHl1h6DrZ4hrhgI/+nk7mvueZyCzQK00M"
    "XadS32G5VuNyTydLywUqm1u4AMprNXxdkmp9m3DAx3BkoPHOg0PKf6qNrg4Dx9TYKJa45HEz"
    "vVJGA3AMF7bpxjZ1zp1pb+ogMxoT2eIaAN4Oh+7THdimG2A3AYCUDtK2SE3NH9u2bLOwTTdS"
    "OvucY6zuGlzrv0C1XuOsI/G0NL9YYHBIhXq9SMtqWtMAhiMDYjpXQNoWtwJ9hKIjak9w5/GY"
    "AljIr5L7XaBcqyFtC2lbiBbj4B/cfzKupLZN0H+RX+Uqzz5+JR2PNMQZn5xR2cU887mfLC0X"
    "+FH5c2AAcPNhQt290cf5Tg8r+SIjH+aaTJogNL1hgrGkejExq2az39Trd19UMJZURzWHRztq"
    "mI5HxPCbT6yW1rni7ybo954YwHUcmY5HRNxOKmm1nrgZaOzgf/AXUUy2DjrCDG0AAAAASUVO"
    "RK5CYII=")

#----------------------------------------------------------------------
_rt_sample = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAMNJ"
    "REFUWIXtl0sawiAMhGcoN2mvqIeoV6RHUVwoC5VqiOkXFsyahJ+8ADJM8FRw3X0A9AAQfy3I"
    "t2vWOGaYaAIAAPN8atp82y7ite4pEAOktCKl1Q/gKLkDiIpQovfCk3aPGQAA5MaGJYGo7XMr"
    "RQD4RiCaJi8q3mSWHRVhSSDr5MtyPgTAPQJEOftOBFpq4OlIbElKbsOaIT5vO203uafAHcB0"
    "Ej7UNjk6isBO/7dI48IsBdI3YBXg/7PrxfE1GwDeAHen2yjnZJXsxQAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_save = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAAQ1J"
    "REFUKJFjjE/L/c9AJlg0ZxojCwMDA8Oee78YvOzNGGbVJBHUFFc7hWHfiSsMLkpsDAwMDAws"
    "DAwMDPE+rgyvP39kYGBgYNi7bz9Ozc5Ojgww9U+vHUQYgE0RsQDDAGJcgNcAsl0gysvPEFc7"
    "haAGWRFJ3C5AlyTJBTCw7fxVvBq8DLVxG7Dt/FWG0kBLOF+In5eBn5eHgYeXl4Gfl49BTlKQ"
    "wTChCcUQDBcwMDAwlE1Zy6CppsrAwMDA0JTkjtdFTHhlGRgYfv3+x8D89wfD7z9/yDOA+d93"
    "hq9/WBh+/f2LVR7DC3KifAwrGhMZhKXkGTQVJAiZz8DIyMTMEJeSRXKOXDRnGiMDAwMDALeo"
    "P7cp9rvcAAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
_rt_smiley = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAATpJ"
    "REFUWIXtV9EWwiAIRdeH7dP3Y0UPxiIHXjR31kO8VIPuvQNFTCkvdKXdRv7EjzvXz1Je0qkC"
    "NCkf6IlSevt7xCRUAiG2SH3QuJCMyJn7yIlKPLNdqtrMDIy8tU/w+nSy4WZgBrngtLJxECBp"
    "tyyBiiI/FIDImX0S5Pey0FyENbgA1STI3xKxC/DeXoNrIPQ7Wg6YAQ3eswaiizhUgjMtE7UX"
    "nzYUE8XQ6+A3MvAXgKy3w/XEZ6JyUES22LQYdTCFB5JNARDZ/UFi1ihoVIB0ts0QoomFvG94"
    "UfMA6gciwrMI+XAJiD57vBayKn8PeXlWTUTRrtjb9y1yImMbRnaEkI7Mi1DALmRoyrdxvLcv"
    "/sZYHi1HkxyM5s1OKOUY6YQR8hIbvBvim5H6PvNmhMSMkH4tYKZdfhw/Ad89rp/htXYGAAAA"
    "AElFTkSuQmCC")

#----------------------------------------------------------------------
_rt_underline = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAFdJ"
    "REFUOI1jZGRiZqAEMFGkmxoGsKAL/P/39z8yn5GJmRGbGE4XIEvC2NjEcBpAKhg1gIABS5cs"
    "/o9MYwOMuJIyetwzMGBGIV4DiAUEUyI2gJKwBjw3AgDOdhYrghF5ggAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
_rt_undo = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAPCAYAAADtc08vAAAABHNCSVQICAgIfAhkiAAAAhVJ"
    "REFUKJGNkstrE1EYxX8zmcSZZDJp2rSNfSg22CANYhYijWjAjcviwkVxW2hBVyZ/gZu6aOtK"
    "aLC7dicqwcdGiIrUoCIhpUVDsPZhq4GENqE2aUu5LuqkLxv94Fvce885995zPkmSLRxVffce"
    "ikQ6W123N7i41XOR65fPSeaeFH3wTAz390h7ib2D4+J9ZhGXajskWqxscq27C5MjP0nOEInF"
    "hQkIDgyJpeUCvjoVjyrjtCoAOK0KHlXGV6eSSGUZefxaACgu1cbH6W/0Do6LL/M5WjQNpyqz"
    "tb3NbKnClaCPwMlmpudzJFJZ/G4Hhm2b+OQMAApAp8fOykoRv9uBrlpYq+yQU6NRKbXn+ZFY"
    "XCzNLeN22Jj9UdoV0FU7umoHYK2yTmblF6nR6D5fAFobXRR/5tBVO07r+o6A06pgGM59QMOx"
    "9ddU4pMzhDu8ICtAHgAZwDhmrXZbYz3hDi/BgSFxUMBjkzA0jbXNMucDp3YEJJsVQ9cwdI1S"
    "uczCaoFsLl+N0ySHI/fF1eAZDF3j00KhGqOyWCgy8TZNa0sDXSeauNTuqw6KaWD37Zi4caGT"
    "ekPnXeYrp9uaePPnTKo1iSb5ZjjA8WY333N5JpKfeXm3f9dgSbYc2aHomHj6Ki2mMnPiUWJK"
    "hKJj4iBGrnV7yO/lrL+dfHGD4RcfSI70H4q25hdME0vlDZ7f6TtE/i8P/lW/AfYJsF99ZciZ"
    "AAAAAElFTkSuQmCC")

#----------------------------------------------------------------------

class RichTextFrame(wx.Frame):
	def __init__(self, *args, **kw):
		wx.Frame.__init__(self, *args, **kw)

		self.MakeMenuBar()
		self.MakeToolBar()
		self.CreateStatusBar()
		self.SetStatusText("Welcome to wx.richtext.RichTextCtrl!")

		self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER);
		wx.CallAfter(self.rtc.SetFocus)

		self.rtc.Freeze()
		self.rtc.BeginSuppressUndo()

		self.rtc.BeginParagraphSpacing(0, 20)

		self.rtc.BeginAlignment(rt.TEXT_ALIGNMENT_CENTRE)
		self.rtc.BeginBold()

		self.rtc.BeginFontSize(14)
		self.rtc.WriteText("Welcome to wxRichTextCtrl, a wxWidgets control for editing and presenting styled text and images")
		self.rtc.EndFontSize()
		self.rtc.Newline()

		self.rtc.BeginItalic()
		self.rtc.WriteText("by Julian Smart")
		self.rtc.EndItalic()

		self.rtc.EndBold()

		self.rtc.Newline()
		#self.rtc.WriteImage(images._rt_zebra.GetImage())

		self.rtc.EndAlignment()

		self.rtc.Newline()
		self.rtc.Newline()

		self.rtc.WriteText("What can you do with this thing? ")
		self.rtc.WriteImage(_rt_smiley.GetImage())
		self.rtc.WriteText(" Well, you can change text ")

		self.rtc.BeginTextColour((255, 0, 0))
		self.rtc.WriteText("colour, like this red bit.")
		self.rtc.EndTextColour()

		self.rtc.BeginTextColour((0, 0, 255))
		self.rtc.WriteText(" And this blue bit.")
		self.rtc.EndTextColour()

		self.rtc.WriteText(" Naturally you can make things ")
		self.rtc.BeginBold()
		self.rtc.WriteText("bold ")
		self.rtc.EndBold()
		self.rtc.BeginItalic()
		self.rtc.WriteText("or italic ")
		self.rtc.EndItalic()
		self.rtc.BeginUnderline()
		self.rtc.WriteText("or underlined.")
		self.rtc.EndUnderline()

		self.rtc.BeginFontSize(14)
		self.rtc.WriteText(" Different font sizes on the same line is allowed, too.")
		self.rtc.EndFontSize()

		self.rtc.WriteText(" Next we'll show an indented paragraph.")

		self.rtc.BeginLeftIndent(60)
		self.rtc.Newline()

		self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. An attractive woman came into the cafe, which is nothing remarkable.")
		self.rtc.EndLeftIndent()

		self.rtc.Newline()

		self.rtc.WriteText("Next, we'll show a first-line indent, achieved using BeginLeftIndent(100, -40).")

		self.rtc.BeginLeftIndent(100, -40)
		self.rtc.Newline()

		self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. An attractive woman came into the cafe, which is nothing remarkable.")
		self.rtc.EndLeftIndent()

		self.rtc.Newline()

		self.rtc.WriteText("Numbered bullets are possible, again using sub-indents:")

		self.rtc.BeginNumberedBullet(1, 100, 60)
		self.rtc.Newline()

		self.rtc.WriteText("This is my first item. Note that wxRichTextCtrl doesn't automatically do numbering, but this will be added later.")
		self.rtc.EndNumberedBullet()

		self.rtc.BeginNumberedBullet(2, 100, 60)
		self.rtc.Newline()

		self.rtc.WriteText("This is my second item.")
		self.rtc.EndNumberedBullet()

		self.rtc.Newline()

		self.rtc.WriteText("The following paragraph is right-indented:")

		self.rtc.BeginRightIndent(200)
		self.rtc.Newline()

		self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. An attractive woman came into the cafe, which is nothing remarkable.")
		self.rtc.EndRightIndent()

		self.rtc.Newline()

		self.rtc.WriteText("The following paragraph is right-aligned with 1.5 line spacing:")

		self.rtc.BeginAlignment(rt.TEXT_ALIGNMENT_RIGHT)
		self.rtc.BeginLineSpacing(rt.TEXT_ATTR_LINE_SPACING_HALF)
		self.rtc.Newline()

		self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. An attractive woman came into the cafe, which is nothing remarkable.")
		self.rtc.EndLineSpacing()
		self.rtc.EndAlignment()

		self.rtc.Newline()
		self.rtc.WriteText("Other notable features of wxRichTextCtrl include:")

		self.rtc.BeginSymbolBullet('*', 100, 60)
		self.rtc.Newline()
		self.rtc.WriteText("Compatibility with wxTextCtrl API")
		self.rtc.EndSymbolBullet()

		self.rtc.BeginSymbolBullet('*', 100, 60)
		self.rtc.Newline()
		self.rtc.WriteText("Easy stack-based BeginXXX()...EndXXX() style setting in addition to SetStyle()")
		self.rtc.EndSymbolBullet()

		self.rtc.BeginSymbolBullet('*', 100, 60)
		self.rtc.Newline()
		self.rtc.WriteText("XML loading and saving")
		self.rtc.EndSymbolBullet()

		self.rtc.BeginSymbolBullet('*', 100, 60)
		self.rtc.Newline()
		self.rtc.WriteText("Undo/Redo, with batching option and Undo suppressing")
		self.rtc.EndSymbolBullet()

		self.rtc.BeginSymbolBullet('*', 100, 60)
		self.rtc.Newline()
		self.rtc.WriteText("Clipboard copy and paste")
		self.rtc.EndSymbolBullet()

		self.rtc.BeginSymbolBullet('*', 100, 60)
		self.rtc.Newline()
		self.rtc.WriteText("wxRichTextStyleSheet with named character and paragraph styles, and control for applying named styles")
		self.rtc.EndSymbolBullet()

		self.rtc.BeginSymbolBullet('*', 100, 60)
		self.rtc.Newline()
		self.rtc.WriteText("A design that can easily be extended to other content types, ultimately with text boxes, tables, controls, and so on")
		self.rtc.EndSymbolBullet()

		self.rtc.BeginSymbolBullet('*', 100, 60)
		self.rtc.Newline()

		# Make a style suitable for showing a URL
		urlStyle = rt.TextAttrEx()
		urlStyle.SetTextColour(wx.BLUE)
		urlStyle.SetFontUnderlined(True)

		self.rtc.WriteText("RichTextCtrl can also display URLs, such as this one: ")
		self.rtc.BeginStyle(urlStyle)
		self.rtc.BeginURL("http://wxPython.org/")
		self.rtc.WriteText("The wxPython Web Site")
		self.rtc.EndURL();
		self.rtc.EndStyle();
		self.rtc.WriteText(". Click on the URL to generate an event.")

		self.rtc.Bind(wx.EVT_TEXT_URL, self.OnURL)
		
		self.rtc.Newline()
		self.rtc.EndNumberedBullet()
		self.rtc.WriteText("Note: this sample content was generated programmatically from within the MyFrame constructor in the demo. The images were loaded from inline XPMs. Enjoy wxRichTextCtrl!")

		self.rtc.Newline()
		self.rtc.Newline()
		self.rtc.BeginFontSize(12)
		self.rtc.BeginBold()
		self.rtc.WriteText("Additional comments by David Woods:")
		self.rtc.EndBold()
		self.rtc.EndFontSize()
		self.rtc.Newline()
		self.rtc.WriteText("I find some of the RichTextCtrl method names, as used above, to be misleading.  Some character styles are stacked in the RichTextCtrl, and they are removed in the reverse order from how they are added, regardless of the method called.  Allow me to demonstrate what I mean.")
		self.rtc.Newline()
		
		self.rtc.WriteText('Start with plain text. ')
		self.rtc.BeginBold()
		self.rtc.WriteText('BeginBold() makes it bold. ')
		self.rtc.BeginItalic()
		self.rtc.WriteText('BeginItalic() makes it bold-italic. ')
		self.rtc.EndBold()
		self.rtc.WriteText('EndBold() should make it italic but instead makes it bold. ')
		self.rtc.EndItalic()
		self.rtc.WriteText('EndItalic() takes us back to plain text. ')
		self.rtc.Newline()

		self.rtc.WriteText('Start with plain text. ')
		self.rtc.BeginBold()
		self.rtc.WriteText('BeginBold() makes it bold. ')
		self.rtc.BeginUnderline()
		self.rtc.WriteText('BeginUnderline() makes it bold-underline. ')
		self.rtc.EndBold()
		self.rtc.WriteText('EndBold() should make it underline but instead makes it bold. ')
		self.rtc.EndUnderline()
		self.rtc.WriteText('EndUnderline() takes us back to plain text. ')
		self.rtc.Newline()

		self.rtc.WriteText('According to Julian, this functions "as expected" because of the way the RichTextCtrl is written.  I wrote the SetFontStyle() method here to demonstrate a way to work with overlapping styles that solves this problem.')
		self.rtc.Newline()

		# Create and initialize text attributes
		self.textAttr = rt.RichTextAttr()
		self.SetFontStyle(fontColor=wx.Colour(0, 0, 0), fontBgColor=wx.Colour(255, 255, 255), fontFace='Times New Roman', fontSize=10, fontBold=False, fontItalic=False, fontUnderline=False)
		self.rtc.WriteText('Start with plain text. ')
		self.SetFontStyle(fontBold=True)
		self.rtc.WriteText('Bold. ')
		self.SetFontStyle(fontItalic=True)
		self.rtc.WriteText('Bold-italic. ')
		self.SetFontStyle(fontBold=False)
		self.rtc.WriteText('Italic. ')
		self.SetFontStyle(fontItalic=False)
		self.rtc.WriteText('Back to plain text. ')
		self.rtc.Newline()

		self.rtc.WriteText('Start with plain text. ')
		self.SetFontStyle(fontBold=True)
		self.rtc.WriteText('Bold. ')
		self.SetFontStyle(fontUnderline=True)
		self.rtc.WriteText('Bold-Underline. ')
		self.SetFontStyle(fontBold=False)
		self.rtc.WriteText('Underline. ')
		self.SetFontStyle(fontUnderline=False)
		self.rtc.WriteText('Back to plain text. ')
		self.rtc.Newline()
		self.rtc.EndParagraphSpacing()

		self.rtc.EndSuppressUndo()
		self.rtc.Thaw()
		

	def SetFontStyle(self, fontColor = None, fontBgColor = None, fontFace = None, fontSize = None,
					 fontBold = None, fontItalic = None, fontUnderline = None):
		if fontColor:
			self.textAttr.SetTextColour(fontColor)
		if fontBgColor:
			self.textAttr.SetBackgroundColour(fontBgColor)
		if fontFace:
			self.textAttr.SetFontFaceName(fontFace)
		if fontSize:
			self.textAttr.SetFontSize(fontSize)
		if fontBold != None:
			if fontBold:
				self.textAttr.SetFontWeight(wx.FONTWEIGHT_BOLD)
			else:
				self.textAttr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
		if fontItalic != None:
			if fontItalic:
				self.textAttr.SetFontStyle(wx.FONTSTYLE_ITALIC)
			else:
				self.textAttr.SetFontStyle(wx.FONTSTYLE_NORMAL)
		if fontUnderline != None:
			if fontUnderline:
				self.textAttr.SetFontUnderlined(True)
			else:
				self.textAttr.SetFontUnderlined(False)
		self.rtc.SetDefaultStyle(self.textAttr)

	def OnURL(self, evt):
		wx.MessageBox(evt.GetString(), "URL Clicked")
		

	def OnFileOpen(self, evt):
		# This gives us a string suitable for the file dialog based on
		# the file handlers that are loaded
		wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=False)
		dlg = wx.FileDialog(self, "Choose a filename",
							wildcard=wildcard,
							style=wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			if path:
				fileType = types[dlg.GetFilterIndex()]
				self.rtc.LoadFile(path, fileType)
		dlg.Destroy()

		
	def OnFileSave(self, evt):
		print( self.GetValue() )
		'''
		if not self.rtc.GetFilename():
			self.OnFileSaveAs(evt)
			return
		self.rtc.SaveFile()
		'''
		
	def OnFileSaveAs(self, evt):
		wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)

		dlg = wx.FileDialog(self, "Choose a filename",
							wildcard=wildcard,
							style=wx.FD_SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			if path:
				fileType = types[dlg.GetFilterIndex()]
				ext = rt.RichTextBuffer.FindHandlerByType(fileType).GetExtension()
				if not path.endswith(ext):
					path += '.' + ext
				self.rtc.SaveFile(path, fileType)
		dlg.Destroy()
		
	def GetValue( self ):
		handler = rt.RichTextXMLHandler()
		handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_BASE64)

		stream = StringIO()
		handler.SaveStream( self.rtc.GetBuffer(), stream )
		value = stream.getvalue()
		return value
		
	def SetValue( self, value ):
		handler = rt.RichTextXMLHandler()
		handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_BASE64)
		
		stream = StringIO( value )
		handler.LoadStream( self.rtc.GetBuffer(), stream )
	
	def OnFileViewHTML(self, evt):
		# Get an instance of the html file handler, use it to save the
		# document to a StringIO stream, and then display the
		# resulting html text in a dialog with a HtmlWindow.
		handler = rt.RichTextHTMLHandler()
		handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
		handler.SetFontSizeMapping([7,9,11,12,14,22,100])

		stream = StringIO()
		if not handler.SaveStream(self.rtc.GetBuffer(), stream):
			return

		import wx.html
		dlg = wx.Dialog(self, title="HTML", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		html = wx.html.HtmlWindow(dlg, size=(500,400), style=wx.BORDER_SUNKEN)
		html.SetPage(stream.getvalue())
		btn = wx.Button(dlg, wx.ID_CANCEL)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(html, 1, wx.ALL|wx.EXPAND, 5)
		sizer.Add(btn, 0, wx.ALL|wx.CENTER, 10)
		dlg.SetSizer(sizer)
		sizer.Fit(dlg)

		dlg.ShowModal()

		handler.DeleteTemporaryImages()
		

	
	def OnFileExit(self, evt):
		self.Close(True)

	  
	def OnBold(self, evt):
		self.rtc.ApplyBoldToSelection()
		
	def OnItalic(self, evt): 
		self.rtc.ApplyItalicToSelection()
		
	def OnUnderline(self, evt):
		self.rtc.ApplyUnderlineToSelection()
		
	def OnAlignLeft(self, evt):
		self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_LEFT)
		
	def OnAlignRight(self, evt):
		self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_RIGHT)
		
	def OnAlignCenter(self, evt):
		self.rtc.ApplyAlignmentToSelection(rt.TEXT_ALIGNMENT_CENTRE)
		
	def OnIndentMore(self, evt):
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
		ip = self.rtc.GetInsertionPoint()
		if self.rtc.GetStyle(ip, attr):
			r = rt.RichTextRange(ip, ip)
			if self.rtc.HasSelection():
				r = self.rtc.GetSelectionRange()

			attr.SetLeftIndent(attr.GetLeftIndent() + 100)
			attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
			self.rtc.SetStyle(r, attr)
	   
		
	def OnIndentLess(self, evt):
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
		ip = self.rtc.GetInsertionPoint()
		if self.rtc.GetStyle(ip, attr):
			r = rt.RichTextRange(ip, ip)
			if self.rtc.HasSelection():
				r = self.rtc.GetSelectionRange()

		if attr.GetLeftIndent() >= 100:
			attr.SetLeftIndent(attr.GetLeftIndent() - 100)
			attr.SetFlags(rt.TEXT_ATTR_LEFT_INDENT)
			self.rtc.SetStyle(r, attr)

		
	def OnParagraphSpacingMore(self, evt):
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
		ip = self.rtc.GetInsertionPoint()
		if self.rtc.GetStyle(ip, attr):
			r = rt.RichTextRange(ip, ip)
			if self.rtc.HasSelection():
				r = self.rtc.GetSelectionRange()

			attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() + 20);
			attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
			self.rtc.SetStyle(r, attr)

		
	def OnParagraphSpacingLess(self, evt):
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
		ip = self.rtc.GetInsertionPoint()
		if self.rtc.GetStyle(ip, attr):
			r = rt.RichTextRange(ip, ip)
			if self.rtc.HasSelection():
				r = self.rtc.GetSelectionRange()

			if attr.GetParagraphSpacingAfter() >= 20:
				attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() - 20);
				attr.SetFlags(rt.TEXT_ATTR_PARA_SPACING_AFTER)
				self.rtc.SetStyle(r, attr)

		
	def OnLineSpacingSingle(self, evt): 
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
		ip = self.rtc.GetInsertionPoint()
		if self.rtc.GetStyle(ip, attr):
			r = rt.RichTextRange(ip, ip)
			if self.rtc.HasSelection():
				r = self.rtc.GetSelectionRange()

			attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
			attr.SetLineSpacing(10)
			self.rtc.SetStyle(r, attr)
 
				
	def OnLineSpacingHalf(self, evt):
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
		ip = self.rtc.GetInsertionPoint()
		if self.rtc.GetStyle(ip, attr):
			r = rt.RichTextRange(ip, ip)
			if self.rtc.HasSelection():
				r = self.rtc.GetSelectionRange()

			attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
			attr.SetLineSpacing(15)
			self.rtc.SetStyle(r, attr)

		
	def OnLineSpacingDouble(self, evt):
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
		ip = self.rtc.GetInsertionPoint()
		if self.rtc.GetStyle(ip, attr):
			r = rt.RichTextRange(ip, ip)
			if self.rtc.HasSelection():
				r = self.rtc.GetSelectionRange()

			attr.SetFlags(rt.TEXT_ATTR_LINE_SPACING)
			attr.SetLineSpacing(20)
			self.rtc.SetStyle(r, attr)


	def OnFont(self, evt):
		if not self.rtc.HasSelection():
			return

		r = self.rtc.GetSelectionRange()
		fontData = wx.FontData()
		fontData.EnableEffects(False)
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_FONT)
		if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
			fontData.SetInitialFont(attr.GetFont())

		dlg = wx.FontDialog(self, fontData)
		if dlg.ShowModal() == wx.ID_OK:
			fontData = dlg.GetFontData()
			font = fontData.GetChosenFont()
			if font:
				attr.SetFlags(rt.TEXT_ATTR_FONT)
				attr.SetFont(font)
				self.rtc.SetStyle(r, attr)
		dlg.Destroy()


	def OnColour(self, evt):
		colourData = wx.ColourData()
		attr = rt.TextAttrEx()
		attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)
		if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
			colourData.SetColour(attr.GetTextColour())

		dlg = wx.ColourDialog(self, colourData)
		if dlg.ShowModal() == wx.ID_OK:
			colourData = dlg.GetColourData()
			colour = colourData.GetColour()
			if colour:
				if not self.rtc.HasSelection():
					self.rtc.BeginTextColour(colour)
				else:
					r = self.rtc.GetSelectionRange()
					attr.SetFlags(rt.TEXT_ATTR_TEXT_COLOUR)
					attr.SetTextColour(colour)
					self.rtc.SetStyle(r, attr)
		dlg.Destroy()
		


	def OnUpdateBold(self, evt):
		evt.Check(self.rtc.IsSelectionBold())
	
	def OnUpdateItalic(self, evt): 
		evt.Check(self.rtc.IsSelectionItalics())
	
	def OnUpdateUnderline(self, evt): 
		evt.Check(self.rtc.IsSelectionUnderlined())
	
	def OnUpdateAlignLeft(self, evt):
		evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_LEFT))
		
	def OnUpdateAlignCenter(self, evt):
		evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_CENTRE))
		
	def OnUpdateAlignRight(self, evt):
		evt.Check(self.rtc.IsSelectionAligned(rt.TEXT_ALIGNMENT_RIGHT))

	
	def ForwardEvent(self, evt):
		# The RichTextCtrl can handle menu and update events for undo,
		# redo, cut, copy, paste, delete, and select all, so just
		# forward the event to it.
		self.rtc.ProcessEvent(evt)


	def MakeMenuBar(self):
		def doBind(item, handler, updateUI=None):
			self.Bind(wx.EVT_MENU, handler, item)
			if updateUI is not None:
				self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
			
		fileMenu = wx.Menu()
		'''
		doBind( fileMenu.Append(-1, "&Open\tCtrl+O", "Open a file"),
				self.OnFileOpen )
		'''
		doBind( fileMenu.Append(-1, "&Save\tCtrl+S", "Save a file"),
				self.OnFileSave )
		'''
		doBind( fileMenu.Append(-1, "&Save As...\tF12", "Save to a new file"),
				self.OnFileSaveAs )
		fileMenu.AppendSeparator()
		doBind( fileMenu.Append(-1, "&View as HTML", "View HTML"),
				self.OnFileViewHTML)
		fileMenu.AppendSeparator()
		doBind( fileMenu.Append(-1, "E&xit\tCtrl+Q", "Quit this program"),
				self.OnFileExit )
		'''
		
		editMenu = wx.Menu()
		doBind( editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl+Z"), self.ForwardEvent, self.ForwardEvent)
		doBind( editMenu.Append(wx.ID_REDO, "&Redo\tCtrl+Y"), self.ForwardEvent, self.ForwardEvent )
		editMenu.AppendSeparator()
		doBind( editMenu.Append(wx.ID_CUT, "Cu&t\tCtrl+X"), self.ForwardEvent, self.ForwardEvent )
		doBind( editMenu.Append(wx.ID_COPY, "&Copy\tCtrl+C"), self.ForwardEvent, self.ForwardEvent)
		doBind( editMenu.Append(wx.ID_PASTE, "&Paste\tCtrl+V"), self.ForwardEvent, self.ForwardEvent)
		doBind( editMenu.Append(wx.ID_CLEAR, "&Delete\tDel"), self.ForwardEvent, self.ForwardEvent)
		editMenu.AppendSeparator()
		doBind( editMenu.Append(wx.ID_SELECTALL, "Select A&ll\tCtrl+A"), self.ForwardEvent, self.ForwardEvent )
		
		#doBind( editMenu.AppendSeparator(),  )
		#doBind( editMenu.Append(-1, "&Find...\tCtrl+F"),  )
		#doBind( editMenu.Append(-1, "&Replace...\tCtrl+R"),  )

		formatMenu = wx.Menu()
		doBind( formatMenu.AppendCheckItem(-1, "&Bold\tCtrl+B"), self.OnBold, self.OnUpdateBold)
		doBind( formatMenu.AppendCheckItem(-1, "&Italic\tCtrl+I"), self.OnItalic, self.OnUpdateItalic)
		doBind( formatMenu.AppendCheckItem(-1, "&Underline\tCtrl+U"), self.OnUnderline, self.OnUpdateUnderline)
		formatMenu.AppendSeparator()
		doBind( formatMenu.AppendCheckItem(-1, "L&eft Align"), self.OnAlignLeft, self.OnUpdateAlignLeft)
		doBind( formatMenu.AppendCheckItem(-1, "&Centre"), self.OnAlignCenter, self.OnUpdateAlignCenter)
		doBind( formatMenu.AppendCheckItem(-1, "&Right Align"), self.OnAlignRight, self.OnUpdateAlignRight)
		formatMenu.AppendSeparator()
		doBind( formatMenu.Append(-1, "Indent &More"), self.OnIndentMore)
		doBind( formatMenu.Append(-1, "Indent &Less"), self.OnIndentLess)
		formatMenu.AppendSeparator()
		doBind( formatMenu.Append(-1, "Increase Paragraph &Spacing"), self.OnParagraphSpacingMore)
		doBind( formatMenu.Append(-1, "Decrease &Paragraph Spacing"), self.OnParagraphSpacingLess)
		formatMenu.AppendSeparator()
		doBind( formatMenu.Append(-1, "Normal Line Spacing"), self.OnLineSpacingSingle)
		doBind( formatMenu.Append(-1, "1.5 Line Spacing"), self.OnLineSpacingHalf)
		doBind( formatMenu.Append(-1, "Double Line Spacing"), self.OnLineSpacingDouble)
		formatMenu.AppendSeparator()
		doBind( formatMenu.Append(-1, "&Font..."), self.OnFont)
		
		mb = wx.MenuBar()
		mb.Append(fileMenu, "&File")
		mb.Append(editMenu, "&Edit")
		mb.Append(formatMenu, "F&ormat")
		self.SetMenuBar(mb)


	def MakeToolBar(self):
		def doBind(item, handler, updateUI=None):
			self.Bind(wx.EVT_TOOL, handler, item)
			if updateUI is not None:
				self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
		
		tbar = self.CreateToolBar()
		'''
		doBind( tbar.AddTool(-1, _rt_open.GetBitmap(), shortHelpString="Open"), self.OnFileOpen)
		doBind( tbar.AddTool(-1, _rt_save.GetBitmap(), shortHelpString="Save"), self.OnFileSave)
		tbar.AddSeparator()
		'''
		doBind( tbar.AddTool(wx.ID_CUT, _rt_cut.GetBitmap(), shortHelpString="Cut"), self.ForwardEvent, self.ForwardEvent)
		doBind( tbar.AddTool(wx.ID_COPY, _rt_copy.GetBitmap(), shortHelpString="Copy"), self.ForwardEvent, self.ForwardEvent)
		doBind( tbar.AddTool(wx.ID_PASTE, _rt_paste.GetBitmap(), shortHelpString="Paste"), self.ForwardEvent, self.ForwardEvent)
		tbar.AddSeparator()
		doBind( tbar.AddTool(wx.ID_UNDO, _rt_undo.GetBitmap(), shortHelpString="Undo"), self.ForwardEvent, self.ForwardEvent)
		doBind( tbar.AddTool(wx.ID_REDO, _rt_redo.GetBitmap(), shortHelpString="Redo"), self.ForwardEvent, self.ForwardEvent)
		tbar.AddSeparator()
		doBind( tbar.AddTool(-1, _rt_bold.GetBitmap(), isToggle=True, shortHelpString="Bold"), self.OnBold, self.OnUpdateBold)
		doBind( tbar.AddTool(-1, _rt_italic.GetBitmap(), isToggle=True, shortHelpString="Italic"), self.OnItalic, self.OnUpdateItalic)
		doBind( tbar.AddTool(-1, _rt_underline.GetBitmap(), isToggle=True, shortHelpString="Underline"), self.OnUnderline, self.OnUpdateUnderline)
		tbar.AddSeparator()
		doBind( tbar.AddTool(-1, _rt_alignleft.GetBitmap(), isToggle=True, shortHelpString="Align Left"), self.OnAlignLeft, self.OnUpdateAlignLeft)
		doBind( tbar.AddTool(-1, _rt_centre.GetBitmap(), isToggle=True, shortHelpString="Center"), self.OnAlignCenter, self.OnUpdateAlignCenter)
		doBind( tbar.AddTool(-1, _rt_alignright.GetBitmap(), isToggle=True, shortHelpString="Align Right"), self.OnAlignRight, self.OnUpdateAlignRight)
		tbar.AddSeparator()
		doBind( tbar.AddTool(-1, _rt_indentless.GetBitmap(), shortHelpString="Indent Less"), self.OnIndentLess)
		doBind( tbar.AddTool(-1, _rt_indentmore.GetBitmap(), shortHelpString="Indent More"), self.OnIndentMore)
		tbar.AddSeparator()
		doBind( tbar.AddTool(-1, _rt_font.GetBitmap(), shortHelpString="Font"), self.OnFont)
		doBind( tbar.AddTool(-1, _rt_colour.GetBitmap(), shortHelpString="Font Colour"), self.OnColour)

		tbar.Realize()

#----------------------------------------------------------------------

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = RichTextFrame(None,title="CrossMgr", size=(800,500))
	mainWin.Show()
	app.MainLoop()
