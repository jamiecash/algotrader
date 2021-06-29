import importlib
import logging
import wx
import wxconfig as cfg


class MDIFrame(wx.MDIParentFrame):
    """
    The MDI Frame window for the application
    """
    __log = None  # The logger

    def __init__(self):
        # Super
        wx.MDIParentFrame.__init__(self, parent=None, id=wx.ID_ANY, title="Algo Trader",
                                   pos=wx.Point(x=cfg.Config().get('window.x'), y=cfg.Config().get('window.y')),
                                   size=wx.Size(width=cfg.Config().get('window.width'),
                                                height=cfg.Config().get('window.height')))

        # Create logger
        self.__log = logging.getLogger(__name__)

        # Status bar.
        statusbar = self.CreateStatusBar()

        # Create menu bar
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        # Create file menu
        file_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.__on_open_settings,
                  file_menu.Append(wx.ID_ANY, "Se&ttings", "Configure application settings."))
        self.Bind(wx.EVT_MENU, self.__on_exit,
                  file_menu.Append(wx.ID_ANY, "E&xit", "Quits the application."))
        menubar.Append(file_menu, "&File")

        # Create help menu
        help_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.__on_view_log,
                  help_menu.Append(wx.ID_ANY, "View Log", "Show application log."))
        self.Bind(wx.EVT_MENU, self.__on_view_help,
                  help_menu.Append(wx.ID_ANY, "Help", "Show application usage instructions."))
        menubar.Append(help_menu, "&Help")

        # Bind window close event
        self.Bind(wx.EVT_CLOSE, self.__on_close, self)

    def __on_close(self, event):
        """
        Window closing. Save position.
        :param event:
        :return:
        """
        # Save pos and size
        x, y = self.GetPosition()
        width, height = self.GetSize()
        cfg.Config().set('window.x', x)
        cfg.Config().set('window.y', y)
        cfg.Config().set('window.width', width)
        cfg.Config().set('window.height', height)
        cfg.Config().save()

        # End
        event.Skip()

    def __on_exit(self, evt):
        # Close
        self.Close()

    def __on_open_settings(self, evt):
        """
        Opens the settings dialog and handles any changed settings.
        :return:
        """
        settings_dialog = cfg.SettingsDialog(parent=self, exclude=['window'])
        res = settings_dialog.ShowModal()
        if res == wx.ID_OK:
            # TODO Handle any changed settings
            pass

    def __on_view_help(self, evt):
        """
        View the help file
        :return:
        """
        FrameManager.open_frame(parent=self, frame_module='algotrader.gui.mdi_child_util',
                                frame_class='MDIChildHelp', raise_if_open=True)

    def __on_view_log(self, evt):
        """
        View the log file
        :return:
        """
        FrameManager.open_frame(parent=self, frame_module='algotrader.gui.mdi_child_util',
                                frame_class='MDIChildLog', raise_if_open=True)


class FrameManager:
    """
    Manages the opening and raising of MDIChild frames
    """
    @staticmethod
    def open_frame(parent, frame_module, frame_class, raise_if_open=True, **kwargs):
        """
        Opens the frame specified by the frame class
        :param parent: The MDIParentFrame to open the child frame into
        :param frame_module: A string specifying the module containing the frame class to open or raise
        :param frame_class: A string specifying the frame class to open or raise
        :param raise_if_open: Whether the frame should raise rather than open if an instance is already open.
        :param kwargs: A dict of parameters to pass to frame constructor. These will also be checked  in raise_if_open
            to determine uniqueness (i.e. If a frame of the same class is already open but its params are different,
            then the frame will be opened again with the new params instead of being raised.)
        :return:
        """

        # Load the module and class
        module = importlib.import_module(frame_module)
        clazz = getattr(module, frame_class)

        # Do we have an opened instance
        opened_instance = None
        for child in parent.GetChildren():
            if isinstance(child, clazz):
                # do the args match
                match = True
                for key in kwargs:
                    if kwargs[key] != getattr(child, key):
                        match = False

                # Only open existing instance if args matched
                if match:
                    opened_instance = child

        # If we dont have an opened instance or raise_on_open is False then open new frame, otherwise raise it
        if opened_instance is None or raise_if_open is False:
            if len(kwargs) == 0:
                clazz(parent=parent).Show(True)
            else:
                clazz(parent=parent, **kwargs).Show(True)
        else:
            opened_instance.Raise()

