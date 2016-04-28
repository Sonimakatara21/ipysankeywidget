# -*- coding: utf-8 -*-

# Import widgets, provisioners and traitlets
from ipywidgets import DOMWidget, CallbackDispatcher
from traitlets import Unicode, List, Dict, CInt
import base64


class SankeyWidget(DOMWidget):
    '''
    Sankey widget
    '''

    # the name of the requirejs module (no .js!)
    _view_module = Unicode(
        'nbextensions/ipysankeywidget/js/widget_nbsankey',
        sync=True)

    # the name of the Backbone.View subclass to be used
    _view_name = Unicode(
        'SankeyWidgetView',
        sync=True
    )

    # the name of the CSS file to load with this widget
    _view_style = Unicode(
        'nbextensions/ipysankeywidget/css/widget_nbsankey',
        sync=True
    )

    ########################################################
    # Actual values

    value = Dict({'nodes': [], 'edges': []}, sync=True)
    slice_titles = List(sync=True)

    width = CInt(900, sync=True)
    height = CInt(500, sync=True)
    margins = Dict({}, sync=True)

    # Get image data back
    png = Unicode('', sync=True)

    def __init__(self, **kwargs):
        """Constructor"""
        super(SankeyWidget, self).__init__(**kwargs)
        self._selected_handlers = CallbackDispatcher()
        self._auto_png_filename = None
        self.on_msg(self._handle_sankey_msg)
        self.observe(self._on_png_data, names=['png'])

    def on_selected(self, callback, remove=False):
        """Register a callback to execute when a node is selected.

        The callback will be called with one argument,
        the Sankey widget instance.

        Parameters
        ----------
        remove : bool (optional)
            Set to true to remove the callback from the list of callbacks."""
        self._selected_handlers.register_callback(callback, remove=remove)

    def _handle_sankey_msg(self, _, content, buffers):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""
        if content.get('event', '') == 'selected':
            self._selected_handlers(self, content.get('node'))

    def _on_png_data(self, change):
        if change['type'] != 'change': return
        if self._auto_png_filename:
            self.save_png(self._auto_png_filename)
            self._auto_png_filename = None

    def set_scale(self, scale=None):
        self.send({"method": "set_scale", "value": scale})

    def save_png(self, filename):
        data = base64.decodebytes(bytes(self.png, 'ascii'))
        with open(filename, 'wb') as f:
            f.write(data)

    def auto_save_png(self, filename):
        self._auto_png_filename = filename
        return self