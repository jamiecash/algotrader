import definitions
import markdown
import wx
import wx.html


class MDIChildHelp(wx.MDIChildFrame):
    """
    Shows the README.md file
    """

    def __init__(self, parent):
        # Super
        wx.MDIChildFrame.__init__(self, parent=parent, id=wx.ID_ANY, pos=wx.DefaultPosition, title="Help",
                                  size=wx.Size(width=800, height=-1),
                                  style=wx.DEFAULT_FRAME_STYLE)

        # Panel and sizer for help file
        panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer()
        panel.SetSizer(sizer)

        # HtmlWindow
        html_widget = wx.html.HtmlWindow(parent=panel, id=wx.ID_ANY,
                                         style=wx.html.HW_SCROLLBAR_AUTO | wx.html.HW_NO_SELECTION)
        sizer.Add(html_widget, 1, wx.ALL | wx.EXPAND)

        # Load the help file, convert markdown to HTML and display. The markdown library doesnt understand the shell
        # format so we will remove.
        markdown_text = open(definitions.HELP_FILE).read()
        markdown_text = markdown_text.replace("```shell", "```")
        html = markdown.markdown(markdown_text)
        html_widget.SetPage(html)


class MDIChildLog(wx.MDIChildFrame):
    """
    Shows the debug.log file
    """

    __log_window = None  # Widget to display log file in

    def __init__(self, parent):
        # Super
        wx.MDIChildFrame.__init__(self, parent=parent, id=wx.ID_ANY, pos=wx.DefaultPosition, title="Log",
                                  size=wx.Size(width=800, height=200),
                                  style=wx.DEFAULT_FRAME_STYLE)

        # Panel and sizer for help file
        panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer()
        panel.SetSizer(sizer)

        # Log file window
        self.__log_window = wx.TextCtrl(parent=panel, id=wx.ID_ANY, style=wx.HSCROLL | wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.__log_window, 1, wx.ALL | wx.EXPAND)

        # Refresh to populate
        self.refresh()

    def refresh(self):
        """
        Refresh the log file
        :return:
        """
        # Load the help file
        self.__log_window.LoadFile(definitions.LOG_FILE)

        # Scroll to bottom
        self.__log_window.SetInsertionPoint(-1)

