#coding:utf-8
import wx
import os
import glob,shutil
import zipfile
import dragdrop


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        global fileList,startStr,endStr
        self.dirname=''

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(200,-1))
        self.fileList = wx.ListBox(self,26,wx.DefaultPosition,(370,500),flist,wx.LB_SINGLE)
        fileList = self.fileList
        self.fileList.Bind(wx.EVT_LISTBOX_DCLICK,self.dclickList)
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        self.startStr = wx.StaticText(self,-1,"Start:")
        self.startStr.SetForegroundColour("red")
        startStr = self.startStr
        self.endStr = wx.StaticText(self,-1,"End:")
        self.endStr.SetForegroundColour("red")
        endStr = self.endStr

        # Setting up the menu.
        filemenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open\tCtrl+O"," Open a file to edit")
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Events.
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        dropTarget = dragdrop.FileDropTarget(self.fileList,self)
        self.fileList.SetDropTarget(dropTarget)


        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer3 = wx.BoxSizer(wx.HORIZONTAL)

        self.buttonStart = wx.Button(self,label=u"区間指定")
        #self.buttonEnd = wx.Button(self,label=u"終了ページ指定")
        self.buttonCancel = wx.Button(self,label=u"指定取り消し")
        self.buttonZip = wx.Button(self,label=u"圧縮開始")
        self.buttonFree = wx.Button(self,label=u"フォルダ選択解除")
        self.buttonDelete = wx.Button(self,label=u"オリジナルファイルの削除")
        self.sizer2.Add(self.buttonStart,1,wx.EXPAND)
        #self.sizer2.Add(self.buttonEnd,1,wx.EXPAND)
        self.sizer2.Add(self.buttonCancel,1,wx.EXPAND)
        self.sizer2.Add(self.buttonZip,1,wx.EXPAND)
        self.sizer3.Add(self.buttonFree,1,wx.EXPAND)
        self.sizer3.Add(self.buttonDelete,1,wx.EXPAND)
        self.buttonStart.Bind(wx.EVT_BUTTON,self.selectStart)
        #self.buttonEnd.Bind(wx.EVT_BUTTON,self.selectEnd)
        self.buttonCancel.Bind(wx.EVT_BUTTON,self.selectCancel)
        self.buttonZip.Bind(wx.EVT_BUTTON,self.selectZip)
        self.buttonFree.Bind(wx.EVT_BUTTON,self.selectFree)
        self.buttonDelete.Bind(wx.EVT_BUTTON,self.selectDelete)


        # Use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.fileList, 1, wx.EXPAND)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)
        self.sizer.Add(self.sizer3, 0, wx.EXPAND)
        self.sizer.Add(self.startStr, 0, wx.EXPAND)
        self.sizer.Add(self.endStr, 0, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Centre()
        self.Show()

    def decodeStr(self,list):
        ret = []
        for name in list:
            ret.append(name.decode("cp932"))
        return ret

    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, u"指定したフォルダ内のファイルを圧縮して整理します ", u"About ページピッカー", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    def OnOpen(self,e):
        global dirPath,flist,startPath,endPath
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a folder",style=wx.DD_DEFAULT_STYLE)
        if dirPath is not None:
            dlg.SetPath(dirPath) 
        if dlg.ShowModal() == wx.ID_OK:
            dirPath = dlg.GetPath()
            print dirPath
            #os.chdir(dirPath)
            #↓setDrop...と同様にos.walkを使うべき＊glob.globは日本語対応していない
            flist = glob.glob(os.path.join(dirPath,"*"))
            basenames = []
            for name in flist:
                basenames.append(os.path.basename(name))
            fileList.Set(basenames)
            startPath = None
            endPath = None
            
        dlg.Destroy()

    def setDropedList(self,path):
        global dirPath,flist,startPath,endPath,originalFile
        print type(path)
        originalFile = path
        if not os.path.isdir(path):
            print "this is not direcotry!!"
            ext = os.path.splitext(path)[1].lower()
            if ext == ".zip":
                print "zip!"
                path = self.unzip(path)
            elif ext == ".rar":
                print "rar!"
                #unrar
            else:
                return

        dirPath = path
        print dirPath
        #os.chdir(dirPath)
        #flist = glob.glob(os.path.join(dirPath,"*"))
        flist = self.getInDirFileList(dirPath)
        basenames = []
        for name in flist:
            basenames.append(os.path.basename(name))
        fileList.Set(basenames)
        startPath = None
        endPath = None

    def setStart(self,index,path):
        global startPath,startIndex
        startIndex = index
        startPath = path
        startStr.SetLabel("start: " + os.path.basename(startPath))
    def setEnd(self,index,path):
        global endPath,endIndex
        endIndex = index
        endPath = path
        endStr.SetLabel("end: " + os.path.basename(endPath))
  

    #need to cheange 
    def selectStart(self,e):
        global startIndex,endIndex
        print flist[fileList.GetSelections()[0]]
        selectedIndex = fileList.GetSelections()[0]
        selectedPath = flist[fileList.GetSelections()[0]]
        #開始も終了位置も選択されていない場合
        if startIndex == None and endIndex == None:
            self.setStart(selectedIndex,selectedPath)
        #開始位置だけ選択されている場合
        elif startIndex != None and endIndex == None:
            if selectedIndex >= startIndex:
                self.setEnd(selectedIndex,selectedPath)
            else:
                endIndex = startIndex
                self.setEnd(endIndex,flist[endIndex])
                self.setStart(selectedIndex,selectedPath)
        #終了位置だけ選択されている場合（ありえないと思うので未実装）
        elif startIndex == None and endIndex != None:
            print u"エラー：想定外の選択です"
        #開始，終了どちらも選択済みの場合
        else:
            if selectedIndex > endIndex:
                self.setEnd(selectedIndex,selectedPath)
                return
            elif selectedIndex < startIndex:
                self.setStart(selectedIndex,selectedPath)
                return

            dialog = wx.MessageDialog(None,u"Yesなら開始位置に，Noなら終了位置に設定します",
                    u"開始位置か終了位置かを選んでください",
                    wx.YES_NO | wx.ICON_QUESTION)
            if dialog.ShowModal() == wx.ID_YES:
                self.setStart(selectedIndex,selectedPath)
            else:
                self.setEnd(selectedIndex,selectedPath)
            dialog.Destroy()






    """
    def selectEnd(self,e):
        global endPath,endIndex
        print flist[fileList.GetSelections()[0]]
        endIndex = fileList.GetSelections()[0]
        endPath = flist[fileList.GetSelections()[0]]
        endStr.SetLabel("end: " + os.path.basename(endPath))
    """
    def selectCancel(self,e):
        global startPath,endPath,startIndex,endIndex
        startStr.SetLabel("start: ")
        endStr.SetLabel("end: ")
        startPath = None
        endPath = None
        startIndex = None
        endIndex = None
    def selectZip(self,e):
        global flist,trimelist,endPath,endIndex,startPath,startIndex
        if startPath is None and endPath is None:
            endIndex = len(flist)-1
            endPath = flist[endIndex]
            startIndex = 0
            startPath = flist[0]

        if startPath is None or endPath is None:
            print"choose files"
            return
        dialog = wx.FileDialog(self,"choose save place",wildcard="*.zip",style=wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            print dialog.GetPath()
        else:
            return
        trimelist = flist[startIndex:endIndex+1]
        zip = zipfile.ZipFile(dialog.GetPath(),"w",zipfile.ZIP_DEFLATED)
        for f in trimelist:
            if not os.path.isfile(f) :continue
            print os.path.basename(f)
            zip.write(f,os.path.basename(f).encode("cp932"))
        zip.close()
        print "zipping was end"
        self.selectCancel(None)

    def selectFree(self,e):
        global dirPath,fileList,originalFile
        dirPath = None
        originalFile = None
        fileList.Set([""])

    def dclickList(self,e):
        print fileList.GetSelections()[0]
        self.fileList.SetItemBackgroundColour(fileList.GetSelections()[0],wx.Colour(0,255,255))
        self.fileList.Refresh()
        print "dclicked"
        self.selectStart(e)

    def selectDelete(self,e):
        global dirPath
        if originalFile is None : 
            return
        dlg = wx.MessageDialog(self,originalFile+u"\n\nを本当に削除しますか？",u"確認",wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_OK :
            print "run"
            #shutil.rmtree(dirPath)
            shutil.rmtree(originalFile)
            dirPath = None
            fileList.Set([""])
        else:
            print "canceled"

    def unzip(self,path):
        if os.path.isdir("tmp"):
            shutil.rmtree("tmp")
            os.mkdir("tmp")
        else:
            os.mkdir("tmp")
        targetZIP =  zipfile.ZipFile(path,"r")
        countMax = len(targetZIP.namelist())
        count = 0
        dlg = wx.ProgressDialog(u"ZIPを展開中...","",maximum = countMax,parent=self,
                style = wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME|wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE|wx.PD_SMOOTH)
        dlg.SetSize((500,150))

        for f in targetZIP.namelist():
            count+=1
            if not os.path.basename(f):
                os.mkdir(os.path.join("tmp",f))
            else:
                unzipFile = file(os.path.join("tmp",f),"wb")
                dlg.Update(count,u"%s を解凍中" % f)
                unzipFile.write(targetZIP.read(f))
                unzipFile.close()

        targetZIP.close()
        dlg.Destroy()
        return os.path.abspath("tmp")

    def unrar(self,path):
        if os.path.isdir("tmp"):
            shutil.rmtree("tmp")
            os.mkdir("tmp")
        else:
            os.mkdir("tmp")

        os.system("unrar %s" % path)

    def getInDirFileList(self,dir):
        ret = []
        for root,dirs,files in os.walk(dir):
            if root == dir:
                for f in files:
                    ret.append(os.path.join(dir,f))
            else:
                continue
        return ret




startIndex = None
endIndex = None
startPath = None
endPath = None
startStr = None
endStr = None

fileList = None
flist = []
trimelist = []
dirPath = None
originalFile = None
app = wx.App(False)#Falseにすることで標準出力にエラーが表示される
frame = MainWindow(None, u"ページピッカー")
app.MainLoop()
