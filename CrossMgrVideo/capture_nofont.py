# -*- encoding: utf-8 -*-
"""
Video Framegrabber for Windows

Copyright © 2009-2014 Jason R. Coombs

Based on the C++ extension-based version by Markus Gritsch:
	http://videocapture.sourceforge.net/

This version has been refactored for easier packaging. For a version
that is fully compatibly with the Gritsch library, please download
revision 0f17f805f7dd.
"""

from __future__ import absolute_import

import datetime
import re
import time
import logging
from ctypes import windll, byref, cast, create_string_buffer, c_long

import PIL.ImageDraw
from comtypes.client import CreateObject
from comtypes import COMError

from .api.objects import (
	FilterGraph, IMediaControl,
	CaptureGraphBuilder2, DeviceEnumerator, CLSID_VideoInputDeviceCategory,
	POINTER, IMoniker, IBaseFilter, tag_AMMediaType, MEDIATYPE_Video,
	MEDIASUBTYPE_RGB24, FORMAT_VideoInfo, PIN_CATEGORY_CAPTURE, IBindCtx,
	SampleGrabber, IVideoWindow, OA_FALSE, OA_TRUE, ISpecifyPropertyPages,
	OleCreatePropertyFrame, MEDIATYPE_Interleaved,
	IAMStreamConfig, IAMVideoControl, PINDIR_OUTPUT,
	VideoControlFlags, VidCapError, VIDEOINFOHEADER, DeleteMediaType,
	VFW_E_WRONG_STATE, LPUNKNOWN,
)

log = logging.getLogger(__name__)

def consume(iterable):
	for x in iterable: pass

class Device(object):
	def __init__(self, devnum=0, show_video_window=False):
		self.devnum = devnum
		self.show_video_window = show_video_window
		self.initialize()

	def initialize(self):
		self.filter_graph = CreateObject(FilterGraph)
		self.control = self.filter_graph.QueryInterface(IMediaControl)
		self.graph_builder = CreateObject(CaptureGraphBuilder2)
		self.graph_builder.SetFiltergraph(self.filter_graph)
		dev_enum = CreateObject(DeviceEnumerator)
		class_enum = dev_enum.CreateClassEnumerator(CLSID_VideoInputDeviceCategory, 0)
		#del dev_enum

		for iCount in range(self.devnum):
			try:
				(moniker, fetched) = class_enum.RemoteNext(1)
			except ValueError:
				raise RuntimeError("Device not found")

		# del class_enum

		null_context = POINTER(IBindCtx)()
		null_moniker = POINTER(IMoniker)()
		self.source = moniker.RemoteBindToObject(null_context,null_moniker,IBaseFilter._iid_)

		self.filter_graph.AddFilter(self.source, "VideoCapture")

		self.grabber = CreateObject(SampleGrabber)
		self.filter_graph.AddFilter(self.grabber, "Grabber")

		mt = tag_AMMediaType()
		mt.majortype = MEDIATYPE_Video
		mt.subtype = MEDIASUBTYPE_RGB24
		mt.formattype = FORMAT_VideoInfo

		self.grabber.SetMediaType(mt)

		self.graph_builder.RenderStream(
			PIN_CATEGORY_CAPTURE,
			MEDIATYPE_Video,
			self.source,
			self.grabber,
			None,
			)

		window = self.filter_graph.QueryInterface(IVideoWindow)
		window.AutoShow = [OA_FALSE, OA_TRUE][self.show_video_window]

		self.grabber.SetBufferSamples(True)
		self.grabber.SetOneShot(False)
		self.getImage = self.get_image

	def teardown(self):
		if hasattr(self, 'control'):
			self.control.Stop()
			self.control.Release()
			del self.control
		if hasattr(self, 'grabber'):
			self.grabber.Release()
			del self.grabber
		if hasattr(self, 'graph_builder'):
			self.graph_builder.Release()
			del self.graph_builder
		if hasattr(self, 'filter_graph'):
			self.filter_graph.Release()
			del self.filter_graph

	def display_capture_filter_properties(self):
		self.control.Stop()
		self._do_property_pages(self.source)

	@staticmethod
	def _do_property_pages(subject):
		spec_pages = subject.QueryInterface(ISpecifyPropertyPages)
		cauuid = spec_pages.GetPages()
		if cauuid.element_count > 0:
			# self.teardown()
			# self.initialize()
			OleCreatePropertyFrame(
				windll.user32.GetTopWindow(None),
				0, 0, None,
				1, byref(cast(subject, LPUNKNOWN)),
				cauuid.element_count, cauuid.elements,
				0, 0, None)
			windll.ole32.CoTaskMemFree(cauuid.elements)
			# self.teardown()
			# self.initialize()

	def display_capture_pin_properties(self):
		self.control.Stop()
		self._do_property_pages(self._get_stream_config())

	def _get_graph_builder_interface(self, interface):
		args = [
				PIN_CATEGORY_CAPTURE,
				MEDIATYPE_Interleaved,
				self.source,
				interface._iid_,
				]
		try:
			result = self.graph_builder.RemoteFindInterface(*args)
		except COMError:
			args[1] = MEDIATYPE_Video
			result = self.graph_builder.RemoteFindInterface(*args)
		return cast(result, POINTER(interface)).value

	def _get_stream_config(self):
		return self._get_graph_builder_interface(IAMStreamConfig)

	def _get_video_control(self):
		return self._get_graph_builder_interface(IAMVideoControl)

	def _get_ppin(self):
		try:
			return self.graph_builder.FindPin(self.source, PINDIR_OUTPUT,
				PIN_CATEGORY_CAPTURE, MEDIATYPE_Interleaved, False, 0)
		except COMError:
			return self.graph_builder.FindPin(self.source, PINDIR_OUTPUT,
				PIN_CATEGORY_CAPTURE, MEDIATYPE_Video, False, 0)

	def get_capabilities(self):
		video_control = self._get_video_control()
		ppin = self._get_ppin()
		return video_control.GetCaps(ppin)

	def _get_mode(self):
		video_control = self._get_video_control()
		ppin = self._get_ppin()
		return video_control.GetMode(ppin)

	# http://msdn.microsoft.com/en-us/library/dd407321(VS.85).aspx
	def set_mode(self, mode, value):
		video_control = self._get_video_control()
		ppin = self._get_ppin()
		mode_val = video_control.GetMode(ppin)
		vc_flags = VideoControlFlags.from_number(mode_val)
		vc_flags[mode] = bool(value)
		video_control.SetMode(ppin, vc_flags.number)
		new_mode_val = video_control.Getmode(ppin)
		if new_mode_val == mode_val:
			log.warning("Mode value appears unchanged on attempt to set %s", mode)

	def set_resolution(self, width, height):
		self.control.Stop()
		stream_config = self._get_stream_config()
		p_media_type = stream_config.GetFormat()
		media_type = p_media_type.contents
		if media_type.formattype != FORMAT_VideoInfo:
			raise VidCapError("Cannot query capture format")
		p_video_info_header = cast(media_type.pbFormat, POINTER(VIDEOINFOHEADER))
		hdr = p_video_info_header.contents.bmi_header
		hdr.width, hdr.height = width, height
		stream_config.SetFormat(media_type)
		DeleteMediaType(media_type)
		#stream_config.Release()
		#self.teardown()
		#self.initialize()

	error_map = dict(
		E_INVALIDARG="Samples are not being buffered",
		E_POINTER="NULL pointer argument",
		VFW_E_NOT_CONNECTED="The filter is not connected",
		VFW_E_WRONG_STATE="The filter did not buffer a sample yet",
	)

	def get_buffer(self):
		media_type = tag_AMMediaType()
		self.grabber.GetConnectedMediaType(media_type)

		p_video_info_header = cast(media_type.pbFormat, POINTER(VIDEOINFOHEADER))

		# windll.ole32.CoTaskMemFree(media_type.pbFormat) ?

		hdr = p_video_info_header.contents.bmi_header
		size = hdr.image_size
		width = hdr.width
		height = hdr.height
		assert size % 4 == 0
		buffer = create_string_buffer(size)
		long_p_buffer = cast(buffer, POINTER(c_long))
		size = c_long(size)

		self.control.Run()

		try:
			while True:
				# call the function directly, as the in/out semantics of
				# argtypes isn't working here.
				try:
					GetCurrentBuffer = self.grabber._ISampleGrabber__com_GetCurrentBuffer
					GetCurrentBuffer(byref(size), long_p_buffer)
				except COMError as e:
					if e.args[0] == VFW_E_WRONG_STATE:
						time.sleep(.100)
					else:
						raise
				else:
					break
		except COMError as e:
			code = e[0]
			unknown_error = 'Unknown Error ({0:x})'.format(code)
			msg = "Getting the sample grabber's current buffer failed ({0}).".format(self.error_map.get(code, unknown_error))
			raise VidCapError(msg)

		return bytes(buffer[:size.value]), (width, height)

	def get_image(self):
		"""Returns a PIL Image instance."""
		buffer, dimensions = self.get_buffer()
		# todo, what is 'BGR', 0, -1 ?
		return PIL.Image.frombytes('RGB', dimensions, buffer, 'raw', 'BGR', 0, -1)
	
	@staticmethod
	def _get_shadow_draw_locations(origin, shadow_style):
		x, y = origin
		outline_locs = ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
		shadow_draw_locations = dict(
			simple = (),
			shadow = ((x+1, y), (x, y+1), (x+1, y+1)),
			outline = outline_locs,
			)
		shadow_draw_locations['thick-outline'] = (
			outline_locs + ((x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1))
			)
		locs = shadow_draw_locations.get(shadow_style)
		if locs is None:
			raise ValueError("Unknown shadow style {0}".format(shadow_style))
		return locs

	def save_snapshot(self, filename, *args, **kwargs):
		"""
		Saves a snapshot to a file.

		The filetype is inferred from the filename extension. Everything that
		PIL can handle can be specified (foo.jpg, foo.gif, foo.bmp, ...).

		filename: String containing the name of the resulting file.

		Any additional arguments are passed to the save() method of the image
		class.
		For example you can specify the compression level of a JPEG image using
		'quality=95'.
		"""
		self.get_image().save(filename, **kwargs)

def save_frame(filename='test.jpg', resolution=None, mode=None):
	"""
	Save a video frame from the default device.

	resolution, if specified, should be something like (320,240)

	mode should be a dictionary of mode key/values, like
	dict(flip_horizontal=True)
	"""
	if mode is None: mode = dict()
	logging.basicConfig(level=logging.INFO)
	d = Device(show_video_window=False)
	if resolution:
		d.set_resolution(*resolution)
	for pair in mode.items():
		d.set_mode(*pair)
	d.save_snapshot(filename)

if __name__ == '__main__':
	save_frame()
