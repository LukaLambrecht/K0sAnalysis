######################################################################################
# grouping some common functions for plotting too long to be included in main script #
######################################################################################

import ROOT
import array

def setTDRstyle():
    # copy from ewkino/plotting/tdrStyle.cc
    # note: some of the options here will be overwritten during the actual plotting.
    # note: most of the commented lines will not be tested and will probably need modification 
    # (from C++ to python).

    # For the canvas:
    ROOT.gStyle.SetCanvasBorderMode(0);
    ROOT.gStyle.SetCanvasColor(ROOT.kWhite);
    ROOT.gStyle.SetCanvasDefH(600); # height of canvas
    ROOT.gStyle.SetCanvasDefW(600); # width of canvas
    ROOT.gStyle.SetCanvasDefX(0); # position on screen
    ROOT.gStyle.SetCanvasDefY(0);

    # For the Pad:
    ROOT.gStyle.SetPadBorderMode(0);
    #ROOT.gStyle.SetPadBorderSize(Width_t size = 1);
    ROOT.gStyle.SetPadColor(ROOT.kWhite);
    ROOT.gStyle.SetPadGridX(ROOT.kFALSE);
    ROOT.gStyle.SetPadGridY(ROOT.kFALSE);
    ROOT.gStyle.SetGridColor(0);
    ROOT.gStyle.SetGridStyle(3);
    ROOT.gStyle.SetGridWidth(1);

    # For the frame:
    ROOT.gStyle.SetFrameBorderMode(0);
    ROOT.gStyle.SetFrameBorderSize(1);
    ROOT.gStyle.SetFrameFillColor(0);
    ROOT.gStyle.SetFrameFillStyle(0);
    ROOT.gStyle.SetFrameLineColor(1);
    ROOT.gStyle.SetFrameLineStyle(1);
    ROOT.gStyle.SetFrameLineWidth(1);

    # For the histo (probably overwritten for each histogram?):
    #ROOT.gStyle.SetHistFillColor(1);
    #ROOT.gStyle.SetHistFillStyle(0);
    ROOT.gStyle.SetHistLineColor(1);
    ROOT.gStyle.SetHistLineStyle(0);
    ROOT.gStyle.SetHistLineWidth(1);
    #ROOT.gStyle.SetLegoInnerR(Float_t rad = 0.5);
    #ROOT.gStyle.SetNumberContours(Int_t number = 20);

    ROOT.gStyle.SetEndErrorSize(2);
    #ROOT.gStyle.SetErrorMarker(20);
    #ROOT.gStyle.SetErrorX(0.);

    ROOT.gStyle.SetMarkerStyle(20);

    # For the fit/function:
    ROOT.gStyle.SetOptFit(1);
    ROOT.gStyle.SetFitFormat("5.4g");
    ROOT.gStyle.SetFuncColor(2);
    ROOT.gStyle.SetFuncStyle(1);
    ROOT.gStyle.SetFuncWidth(1);

    # For the date:
    ROOT.gStyle.SetOptDate(0);
    #ROOT.gStyle.SetDateX(Float_t x = 0.01);
    #ROOT.gStyle.SetDateY(Float_t y = 0.01);

    # For the statistics box:
    ROOT.gStyle.SetOptFile(0);
    ROOT.gStyle.SetOptStat(0); # to display the mean and RMS: SetOptStat("mr");
    ROOT.gStyle.SetStatColor(ROOT.kWhite);
    ROOT.gStyle.SetStatFont(42);
    ROOT.gStyle.SetStatFontSize(0.08); #0.025
    ROOT.gStyle.SetStatTextColor(1);
    ROOT.gStyle.SetStatFormat("6.4g");
    ROOT.gStyle.SetStatBorderSize(1);
    ROOT.gStyle.SetStatH(0.7); #0.1
    ROOT.gStyle.SetStatW(0.15); #0.15
    #ROOT.gStyle.SetStatTextSize(2.5);

    ROOT.gStyle.SetStatX(0.96);
    #ROOT.gStyle.SetStatY(0.35);
    #ROOT.gStyle.SetStatStyle(Style_t style = 1001);
    #ROOT.gStyle.SetStatX(Float_t x = 0);
    #ROOT.gStyle.SetStatY(Float_t y = 0);

    # Margins:
    ROOT.gStyle.SetPadTopMargin(0.05);
    ROOT.gStyle.SetPadBottomMargin(0.13);
    ROOT.gStyle.SetPadLeftMargin(0.14); #0.14
    ROOT.gStyle.SetPadRightMargin(0.04);

    # For the Global title:
    ROOT.gStyle.SetOptTitle(0);
    ROOT.gStyle.SetTitleFont(42);
    ROOT.gStyle.SetTitleColor(1);
    ROOT.gStyle.SetTitleTextColor(1);
    ROOT.gStyle.SetTitleFillColor(10);
    ROOT.gStyle.SetTitleFontSize(0.05);
    #ROOT.gStyle.SetTitleH(0); # set the height of the title box
    #ROOT.gStyle.SetTitleW(0); # set the width of the title box
    #ROOT.gStyle.SetTitleX(0); # set the position of the title box
    #ROOT.gStyle.SetTitleY(0.985); # set the position of the title box
    #ROOT.gStyle.SetTitleStyle(Style_t style = 1001);
    #ROOT.gStyle.SetTitleBorderSize(2);

    # For the axis titles:
    ROOT.gStyle.SetTitleColor(1, "XYZ");
    ROOT.gStyle.SetTitleFont(42, "XYZ");
    ROOT.gStyle.SetTitleSize(0.06, "XYZ");
    #ROOT.gStyle.SetTitleXSize(Float_t size = 0.02); # another way to set the size?
    #ROOT.gStyle.SetTitleYSize(Float_t size = 0.02);
    ROOT.gStyle.SetTitleXOffset(0.9);
    #ROOT.gStyle.SetTitleYOffset(1.25);
    ROOT.gStyle.SetTitleYOffset(1.25); #0.9
    #ROOT.gStyle.SetTitleOffset(1.1, "Y"); # another way to set the Offset

    # For the axis labels:
    ROOT.gStyle.SetLabelColor(1, "XYZ");
    ROOT.gStyle.SetLabelFont(42, "XYZ");
    ROOT.gStyle.SetLabelOffset(0.007, "XYZ");
    #ROOT.gStyle.SetLabelSize(0.1, "XYZ");
    ROOT.gStyle.SetLabelSize(0.05, "XYZ");

    # For the axis:
    ROOT.gStyle.SetAxisColor(1, "XYZ");
    ROOT.gStyle.SetStripDecimals(ROOT.kTRUE);
    ROOT.gStyle.SetTickLength(0.03, "XYZ");
    ROOT.gStyle.SetNdivisions(510, "XYZ");
    ROOT.gStyle.SetPadTickX(1);  # to get tick marks on the opposite side of the frame
    ROOT.gStyle.SetPadTickY(1);

    # Change for log plots:
    ROOT.gStyle.SetOptLogx(0);
    ROOT.gStyle.SetOptLogy(0);
    ROOT.gStyle.SetOptLogz(0);

    # Postscript options:
    ROOT.gStyle.SetPaperSize(20.,20.);
    #ROOT.gStyle.SetLineScalePS(Float_t scale = 3);
    #ROOT.gStyle.SetLineStyleString(Int_t i, const char* text);
    #ROOT.gStyle.SetHeaderPS(const char* header);
    #ROOT.gStyle.SetTitlePS(const char* pstitle);

    #ROOT.gStyle.SetBarOffset(Float_t baroff = 0.5);
    #ROOT.gStyle.SetBarWidth(Float_t barwidth = 0.5);
    #ROOT.gStyle.SetPaintTextFormat(const char* format = "g");
    #ROOT.gStyle.SetPalette(Int_t ncolors = 0, Int_t* colors = 0);
    #ROOT.gStyle.SetTimeOffset(Double_t toffset);
    #ROOT.gStyle.SetHistMinimumZero(kTRUE);

    # For error in SF maps
    #ROOT.gStyle.SetMarkerSize(0.9); # TEMPORARY SIZE FOR DILEPTON PLOTS. SET BACK TO DEFAULT FOR TRILEPTON
    ROOT.gStyle.SetPaintTextFormat("4.2f"); #4.2
    #ROOT.gStyle.SetHatchesLineWidth(5);
    #ROOT.gStyle.SetHatchesSpacing(0.05);

    ROOT.gStyle.SetLegendBorderSize(0);

############################################################

def drawLumi(pad,
	cmstext="CMS",
	cmstext_size_factor=0.8, 
	cmstext_offset=0.03,
	extratext="Preliminary",
        lumitext="<lumi> fb^{-1} (13 TeV)",
	lumitext_size_factor=0.6,
	lumitext_offset=0.01,
	cms_in_grid=True,
	rfrac=0.):

    pad.Update()

    # get margins for pad
    lmargin = pad.GetLeftMargin();
    tmargin = pad.GetTopMargin();
    rmargin = pad.GetRightMargin();

    # define text sizes and offsets relative to margin
    CMSTextSize = tmargin*cmstext_size_factor;
    lumiTextSize = tmargin*lumitext_size_factor;

    CMSTextVerticalOffset = cmstext_offset
    lumiTextVerticalOffset = lumitext_offset

    pad.cd();
    # define latex text to draw on plot
    latex = ROOT.TLatex()
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(ROOT.kBlack);

    latex.SetTextFont(61);
    latex.SetTextAlign(11);
    latex.SetTextSize(CMSTextSize);
    latex.SetText(0,0,'CMS')
    #cmsX = latex.GetXsize(); # does not seem to work properly
    cmsX = CMSTextSize*2*(1-rfrac) # phenomenological alternative
    # old style: cms label outside of frame:
    if not cms_in_grid: latex.DrawLatex(lmargin+0.03, 1 - tmargin + CMSTextVerticalOffset,cmstext);
    # new style: cms label inside frame:
    else: latex.DrawLatex( lmargin+0.03, 1-tmargin-CMSTextVerticalOffset-CMSTextSize,cmstext)

    extraTextSize = CMSTextSize*0.8
    latex.SetTextFont(52);
    latex.SetTextSize(extraTextSize);
    latex.SetTextAlign(11);
    if not cms_in_grid: latex.DrawLatex(lmargin+0.03 + 1.2*cmsX,
                        1-tmargin+CMSTextVerticalOffset, extratext);
    else: latex.DrawLatex(lmargin+0.03 + 1.2*cmsX,
            1-tmargin-CMSTextVerticalOffset-CMSTextSize, extratext);

    latex.SetTextFont(42);
    latex.SetTextAlign(31);
    latex.SetTextSize(lumiTextSize);
    latex.DrawLatex(1-rmargin,1-tmargin+lumiTextVerticalOffset,lumitext);
    
    return
