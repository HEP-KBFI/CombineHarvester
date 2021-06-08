from optparse import OptionParser
import matplotlib
import ROOT
matplotlib.use('agg')
import matplotlib.pyplot as plt
parser = OptionParser()
parser.add_option("--input_path", type='string', dest="input_path", help="path of preparedatacard file")
parser.add_option("--method ", dest="method", help="type of res/nonres", default='lbn', choices=['bdt', 'lbn'])
parser.add_option("--era ", dest="era", help="era", default='2018', choices=['2016', '2017', '2018'])
parser.add_option("--channel", dest="channel", help="which channel is considering", default = '1l_0tau')
(options, args) = parser.parse_args()
input_path = options.input_path
method = options.method
era = options.era
channel = options.channel
modes = ['SM', 'BM1', 'BM2', 'BM3', 'BM4', 'BM5', 'BM6', 'BM7', 'BM8', 'BM9', 'BM10', 'BM11', 'BM12']
ff = 'nonreslimit_%s.txt' %era
f1 = open(ff, 'w+')
def ReadLimits():
    '''central = []
    do1 = []
    do2 = []
    up1 = []
    up2 = []'''
    limits = []
    for mode in modes:
        limit = []
        file_ = '%s/%s_%s_%s_%s.log' %(input_path, mode, method, channel, era)
        f1.write(mode+'\n')
        f = open(file_, 'r+')
        lines = f.readlines() # get all lines as a list (array)
        for line in  lines:
            l = []
            tokens = line.split()
            if "Expected  2.5%"  in line : 
                #do2=do2+[float(tokens[4])]
                f1.write(line)
                limit.append(float(tokens[4]))
            if "Expected 16.0%:" in line : 
                #do1=do1+[float(tokens[4])]
                f1.write(line)
                limit.append(float(tokens[4]))
            if "Expected 50.0%:" in line : 
                #central=central+[float(tokens[4])]
                f1.write(line)
                limit.append(float(tokens[4]))
            if "Expected 84.0%:" in line : 
                #up1=up1+[float(tokens[4])]
                limit.append(float(tokens[4]))
                f1.write(line)
            if "Expected 97.5%:" in line : 
                #up2=up2+[float(tokens[4])]
                f1.write(line)
                limit.append(float(tokens[4]))
        limits.append(limit)
    return limits #[central,do1,do2,up1,up2]

limits = ReadLimits()
N = len(modes)
yellow = ROOT.TGraph(2*N)    # yellow band
green = ROOT.TGraph(2*N)     # green band
median = ROOT.TGraph(N)      # median line
up2s = [ ]
dn2s = []
indx = 0
values = range(len(modes))
for i in range(len(modes)):
    limit = limits[i]
    up2s.append(limit[4])
    dn2s.append(limit[0])
    for j in range(100):
        indx = indx +1
        yellow.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit[4] ) # + 2 sigma
        green.SetPoint(     indx,    values[i]-0.5+(j+1.)/100., limit[3] ) # + 1 sigma
        median.SetPoint(    indx,    values[i]-0.5+(j+1.)/100., limit[2] ) # median
        green.SetPoint(  2*N*100-1-indx, values[i]-0.5+(j+1.)/100., limit[1] ) # - 1 sigma
        yellow.SetPoint( 2*N*100-1-indx, values[i]-0.5+(j+1.)/100., limit[0] ) # - 2 sigma                                                                                                              

W = 800
H  = 600
T = 0.08*H
B = 0.12*H
L = 0.12*W
R = 0.04*W
c = ROOT.TCanvas("c","c",100,100,W,H)
c.SetFillColor(0)
c.SetBorderMode(0)
c.SetFrameFillStyle(0)
c.SetFrameBorderMode(0)
c.SetLeftMargin( L/W )
c.SetRightMargin( R/W )
c.SetTopMargin( T/H )
c.SetBottomMargin( 1.2*B/H )
c.SetTickx(0)
c.SetTicky(0)
c.SetGrid()
c.cd()
frame = c.DrawFrame(1.4,0.001, 4.1, 10)
frame.GetYaxis().CenterTitle()
frame.GetYaxis().SetTitleSize(0.05)
frame.GetXaxis().SetTitleSize(0.05)
frame.GetXaxis().SetLabelSize(0.04)
frame.GetYaxis().SetLabelSize(0.04)
frame.GetYaxis().SetTitleOffset(0.9)
frame.GetXaxis().SetTitleOffset(1.4)
frame.GetXaxis().SetNdivisions(508)
frame.GetYaxis().CenterTitle(True)
frame.GetYaxis().SetTitle("95% upper limit on #sigma (#Chi#rightarrow hh) [pb]")
frame.GetXaxis().SetTitle('nonRes BM')
frame.SetMinimum(min(dn2s)*.01)
frame.SetMaximum(max(up2s)*1.05)
print max(up2s), '\t', min(limits[0]), limits[0]
#if logy:
 #   frame.SetMaximum(max(up2s)*15)
median.SetLineColor(1)
median.SetLineWidth(2)
median.SetLineStyle(2)
median.Draw('Lsame')
#CMS_lumi.lumi_sqrtS = ''#ylabel
#CMS_lumi.CMS_lumi(c,0,11)
ROOT.gPad.SetTicks(1,1)
frame.Draw('sameaxis')

x1 = 0.55
x2 = x1 + 0.24
y2 = 0.86
y1 = 0.70
legend = ROOT.TLegend(x1,y1,x2,y2)
legend.SetFillStyle(0)
legend.SetBorderSize(0)
legend.SetTextSize(0.041)
legend.SetTextFont(42)
legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
legend.AddEntry(green, "#pm 1 std. deviation",'f')
legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
legend.Draw()
print " "
c.SaveAs('limit.pdf')
#c.SaveAs(outpath.replace('.pdf','.root'))
c.Close()

#fig, ax = plt.subplots(figsize=(5, 5))
#binstoDo = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#plt.plot(
 #           binstoDo,limits[0], linestyle='-',marker='o'
  #      )

#fig.savefig('limit.png')
