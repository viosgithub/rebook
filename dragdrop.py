#coding:utf8
import wx

class FileDropTarget(wx.FileDropTarget):
   """ This object implements Drop Target functionality for Files """
   def __init__(self, obj,parent):
      # Initialize the wxFileDropTarget Object
      wx.FileDropTarget.__init__(self)
      # Store the Object Reference for dropped files
      self.obj = obj
      self.parent = parent

   def OnDropFiles(self, x, y, filenames):
      """ Implement File Drop """
      #複数のファイルがドロップされた場合
      if len(filenames) is not 1:
          print "Please drop a directory or archive file(zip,rar)"
          return

      self.parent.setDropedList(filenames[0])


