# Explore the Raspberry Pi Camera in a GUI
# the cmd line instruction used to generate the photo is shown below the photo
# Bill Grainger June 2013 updated Sept 2013

# I learnt a lot about python to create this from various articles on stackoverflow forum
# and image_viewer2.py by created on 03-20-2010 by Mike Driscoll


import os
import wx
import subprocess  # needed to run external program raspistill 
from wx.lib.pubsub import Publisher

defaultfilename = 'image.jpg'
        
########################################################################
class ViewerPanel(wx.Panel):
    """
    creates the main screen
    """
    
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """set up for playing with images"""
        wx.Panel.__init__(self, parent)
        
        width, height = wx.DisplaySize()
       
        self.photoMaxSize = height - 200
        self.img = wx.EmptyImage(self.photoMaxSize,self.photoMaxSize)
        self.image_name=""

        # set up for communication between instances of differnet classes
        Publisher().subscribe(self.updateImages, ("update images"))

        self.layout()

    #----------------------------------------------------------------------
    def fillCS(self):
        """ this draws window to collect all the options for the next image"""
        # screen layout
        xoffset= 2
        xcomoffset=170

        #image size defaults
        w=1920 
        h=1080

        # option list
        self.cbw=wx.CheckBox(self.CS, -1, '-w ', (xoffset, 50))
        self.cbh=wx.CheckBox(self.CS, -1, '-h ', (xoffset, 80))
        self.cbo=wx.CheckBox(self.CS, -1, '-o ', (xoffset, 110))
        self.cbq=wx.CheckBox(self.CS, -1, '-q ', (xoffset, 140))
        self.cbt=wx.CheckBox(self.CS, -1, '-t ', (xoffset, 170))
        self.cbsh=wx.CheckBox(self.CS, -1, '-sh', (xoffset, 200))
        self.cbco=wx.CheckBox(self.CS, -1, '-co ', (xoffset, 230))
        self.cbbr=wx.CheckBox(self.CS, -1, '-br ', (xoffset, 260))
        self.cbsa=wx.CheckBox(self.CS, -1, '-sa ', (xoffset, 290))
        self.cbrot=wx.CheckBox(self.CS, -1, '-rot ', (xoffset, 320))
        self.cbex=wx.CheckBox(self.CS, -1, '-ex ', (xoffset, 350))
        self.cbev=wx.CheckBox(self.CS, -1, '-ev ', (xoffset, 380))
        self.cbawb=wx.CheckBox(self.CS, -1, '-awb ', (xoffset, 410))
        self.cbifx=wx.CheckBox(self.CS, -1, '-ifx ', (xoffset, 440))
        
        # default is to save to a file and have a 1 second delay
        self.cbo.SetValue(True)
        self.cbt.SetValue(True)
        
        # allow changes some with restricted ranges or restricted choices
        self.scw = wx.SpinCtrl(self.CS, -1, str(w), (xoffset+40, 45), (60, -1), min=20, max=5000)
        self.sch = wx.SpinCtrl(self.CS, -1, str(h), (xoffset+40, 75), (60, -1), min=20, max=5000)
        self.oname = wx.TextCtrl(self.CS, pos=(xoffset+40,105),size=(120, -1),value=defaultfilename) # default filename given
        self.scq = wx.SpinCtrl(self.CS, -1, str(75), (xoffset+40, 135), (60, -1), min=0, max=100)
        self.sct = wx.SpinCtrl(self.CS, -1, str(1000), (xoffset+40, 165), (80, -1), min=100, max=100000000)
        self.scsh = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+40, 195), (60, -1), min=-100, max=100)
        self.scco = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+40, 225), (60, -1), min=-100, max=100)
        self.scbr = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+40, 255), (60, -1), min=0, max=100)
        self.scsa = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+40, 285), (60, -1), min=-100, max=100)

        rotmodes = ['0','90','180','270']
        self.scrot = wx.ComboBox(self.CS, -1, pos=(xoffset+40, 315), size=(90, -1), choices=rotmodes, style=wx.CB_READONLY)
        exposuremodes = ['off','auto','night','nightpreview','backlight',
                         'spotlight','sports','snow','beach','verylong','fixedfps','antishake','fireworks']
        self.scex = wx.ComboBox(self.CS, -1, pos=(xoffset+40, 345), size=(90, -1), choices=exposuremodes, style=wx.CB_READONLY)
        self.scev = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+40, 375), (60, -1), min=-10, max=10)

        awbmodes = ['off','auto','sun','cloudshade','tungsten','fluorescent','incandescent','flash','horizon']
        self.scawb = wx.ComboBox(self.CS, -1, pos=(xoffset+40, 405), size=(90, -1), choices=awbmodes, style=wx.CB_READONLY)
        ifxmodes = ['none','negative','solarise','whiteboard','blackboard','sketch','denoise','emboss','oilpaint',
                      'hatch','gpen','pastel','watercolour','film','blur']
        self.scifx = wx.ComboBox(self.CS, -1, pos=(xoffset+40, 435), size=(90, -1), choices=ifxmodes, style=wx.CB_READONLY)
        
        wx.Button(self.CS, 1, 'Take Photo', (30, 470))

        # add brief explanations of settings
        wx.StaticText(self.CS, -1, 'DETAILS', (xcomoffset,1))
        wx.StaticText(self.CS, -1,'width in pixels' , (xcomoffset,50))
        wx.StaticText(self.CS, -1,'height in pixels' , (xcomoffset,80))
        wx.StaticText(self.CS, -1,'filename for picture' , (xcomoffset,110))
        wx.StaticText(self.CS, -1,'quality of jpg' , (xcomoffset,140))
        wx.StaticText(self.CS, -1,'time delay (ms) before' , (xcomoffset,170)) 
        wx.StaticText(self.CS, -1,'sharpness    -100 - 100' , (xcomoffset,200))
        wx.StaticText(self.CS, -1,'contrast     -100 - 100' , (xcomoffset,230))
        wx.StaticText(self.CS, -1,'brightness      0 - 100' , (xcomoffset,260))
        wx.StaticText(self.CS, -1,'saturation   -100 - 100' , (xcomoffset,290))
        wx.StaticText(self.CS, -1,'rotate image' , (xcomoffset,320))
        wx.StaticText(self.CS, -1,'exposure mode' , (xcomoffset,350))
        wx.StaticText(self.CS, -1,'exposure compensation -10 - 10' , (xcomoffset,380))
        wx.StaticText(self.CS, -1,'automatic white balance' , (xcomoffset,410))
        wx.StaticText(self.CS, -1,'image effect' , (xcomoffset,440))
 
        # when happy take a new picture
        self.Bind(wx.EVT_BUTTON, self.TakePic, id=1)
        
        
        
    #----------------------------------------------------------------------
    def TakePic(self, event):
        global defaultfilename
        # pick up all the settings selected and add to command line to be usd to take a picture
        self.cmdln='raspistill '
        if self.cbw.GetValue() :
            self.cmdln=self.cmdln + '-w ' + str(self.scw.GetValue()) +' '
        if self.cbh.GetValue() :
            self.cmdln=self.cmdln + '-h ' + str(self.sch.GetValue()) +' '
        if self.cbo.GetValue() :
            self.cmdln=self.cmdln + '-o "' + str(self.oname.GetValue())+'" '
        if self.cbq.GetValue() :
            self.cmdln=self.cmdln + '-q ' + str(self.scq.GetValue())+' '
        if self.cbt.GetValue() :
            self.cmdln=self.cmdln + '-t ' + str(self.sct.GetValue())+' '      
        if self.cbsh.GetValue() :
            self.cmdln=self.cmdln + '-sh ' + str(self.scsh.GetValue())+' '
        if self.cbco.GetValue() :
            self.cmdln=self.cmdln + '-co ' + str(self.scco.GetValue())+' '
        if self.cbbr.GetValue() :
            self.cmdln=self.cmdln + '-br ' + str(self.scbr.GetValue())+' '
        if self.cbsa.GetValue() :
            self.cmdln=self.cmdln + '-sa ' + str(self.scsa.GetValue())+' '
        if self.cbrot.GetValue() :
            self.cmdln=self.cmdln + '-rot ' + str(self.scrot.GetValue())+' '
        if self.cbex.GetValue() :
            self.cmdln=self.cmdln + '-ex ' + str(self.scex.GetValue())+' '
        if self.cbev.GetValue() :
            self.cmdln=self.cmdln + '-ev ' + str(self.scev.GetValue())+' '    
        if self.cbawb.GetValue() :
            self.cmdln=self.cmdln + '-awb ' + str(self.scawb.GetValue())+' '
        if self.cbifx.GetValue() :
            self.cmdln=self.cmdln + '-ifx ' + str(self.scifx.GetValue())+' '
    
        defaultfilename = str(self.oname.GetValue())
        
        # call external program ro take a picture
        subprocess.check_call([self.cmdln], shell=True)
        # update image on screen
        Publisher().sendMessage("update images","")

       
    #----------------------------------------------------------------------
    def layout(self):
        """
        Layout the widgets on the panel
        """
        self.bigsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, 
                                         wx.BitmapFromImage(self.img))
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)
        self.imageLabel = wx.StaticText(self, label="")
        self.mainSizer.Add(self.imageLabel, 1, wx.ALL, 5)
        
        btnData = [("Rot Clock 90", btnSizer, self.onRotClock),
                   ("Rot Anti-clock 90", btnSizer, self.onRotAclock)]
        for data in btnData:
            label, sizer, handler = data
            self.btnBuilder(label, sizer, handler)
            
        self.mainSizer.Add(btnSizer, 1, wx.CENTER)
        self.CS=wx.Panel(self,0, size=(100,500))
        self.fillCS()
        self.bigsizer.Add(self.CS, 0, wx.ALL,5)
        self.bigsizer.Add(self.mainSizer, 1, wx.ALL,5)
        self.SetSizer(self.bigsizer)
            
    #----------------------------------------------------------------------
    def btnBuilder(self, label, sizer, handler):
        """
        Builds a button, binds it to an event handler and adds it to a sizer
        """
        btn = wx.Button(self, label=label)
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        
    #----------------------------------------------------------------------
    def loadImage(self, image):
        """"""
        self.image_name = os.path.basename(image)
        self.img = wx.Image(image, wx.BITMAP_TYPE_ANY)
        self.rescaleImage()

    #----------------------------------------------------------------------
    def rescaleImage(self):
        # scale the image to fit frame, preserving the aspect ratio
        W = self.img.GetWidth()
        H = self.img.GetHeight()
        if W > H:
            NewW = self.photoMaxSize
            NewH = self.photoMaxSize * H / W
        else:
            NewH = self.photoMaxSize
            NewW = self.photoMaxSize * W / H
        self.img = self.img.Scale(NewW,NewH)

        self.imageCtrl.SetBitmap(wx.BitmapFromImage(self.img))
        self.imageLabel.SetLabel(self.cmdln)
        self.Refresh()
        Publisher().sendMessage("resize", "")
                
    #----------------------------------------------------------------------
    def rotPictureClock(self):
        """
        Rotates the current picture clockwise but only does it once BG 12/6/13
        as it does not store teh rotated image
        """
       
        self.img = self.img.Rotate90(True)
        
        # may need to scale the image, preserving the aspect ratio
        self.rescaleImage()

    #----------------------------------------------------------------------
    def rotPictureAclock(self):
        """
        Rotates the current picture anti-clockwise but only does it once BG 12/6/13
        as it does not store teh rotated image
        """
        
        self.img = self.img.Rotate90(False)
        
        # may need to scale the image, preserving the aspect ratio
        self.rescaleImage()
        
    #----------------------------------------------------------------------
    
    def updateImages(self,msg):
        """
        
        """
        
        self.loadImage(defaultfilename)
              
    #----------------------------------------------------------------------
    def onRotClock(self, event):
        """
        Rotates Image clockwise method, note it works on the image not the camera
        """
        self.rotPictureClock()

    #----------------------------------------------------------------------
    def onRotAclock(self, event):
        """
        Rotates Image anti-clockwise method  
        """
        self.rotPictureAclock()
        
           
        
########################################################################
class ViewerFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Raspberry Pi Camera Simple GUI")
        panel = ViewerPanel(self)
        
        Publisher().subscribe(self.resizeFrame, ("resize"))
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        
        self.Show()
        self.sizer.Fit(self)
        self.Center()     
         
    #----------------------------------------------------------------------
    def resizeFrame(self, msg):
        """"""
        self.sizer.Fit(self)
        
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = ViewerFrame()
    app.MainLoop()
    
