import math
def err(objects, type):
    err = 0
    for obj in objects:
        if type == 'QCDup':
            err += pow(obj.qcd_up*obj.weight,2)
        elif type == 'QCDdn':
            err += pow(obj.qcd_dn*obj.weight,2)
        elif type == 'pdf':
            err += pow(obj.pdf*obj.weight,2)
        elif type == 'alpha':
            err += pow(obj.alpha*obj.weight,2)
    err = math.sqrt(err)
    if 'up' in type:
        return '%.3f' %(1+err)
    elif 'dn' in type:
        return '%.3f' %(1/(1+err))
    else:
        return '%.3f' %(1+err)

class object():
    def __init__(self, xs, totxs, qcd_dn=-1, qcd_up=-1, pdf=-1, alpha=-1):
        self.qcd_up = qcd_up
        self.qcd_dn = qcd_dn
        self.pdf = pdf
        self.alpha = alpha
        self.weight = xs/totxs

xs_WZ = (4*4.9173)+2.8309+0.716+0.5442+0.3807+0.1842+0.07452+0.0799+0.1068+5.6+10.71
xs_WW = 12.2+(3*50.45)+52.15
xs_ggZZ = (3*0.002703)+(3*0.005406)
xs_qqZZ = (3*1.3816)+(2*0.6204)+6.072
tot_VV_xs = xs_ggZZ + xs_qqZZ + xs_WZ + xs_WW

ggZZ = object(xs_ggZZ, tot_VV_xs, qcd_dn=0.176, qcd_up=0.236, pdf=0.173, alpha=-1)
WZ = object(xs_WZ, tot_VV_xs, qcd_dn=0.033, qcd_up=0.038, pdf=0.014, alpha=-1)
qqZZ= object(xs_qqZZ, tot_VV_xs, qcd_dn=0.0133, qcd_up=0.0208, pdf=0.0314, alpha=-1)

qcd_VV_up = err([ggZZ, qqZZ, WZ], 'QCDup')
print 'QCD_VV_Up: ', qcd_VV_up
qcd_VV_dn = err([ggZZ, qqZZ, WZ], 'QCDdn')
print 'QCD_VV_Dn: ', qcd_VV_dn
pdf_VV = err([ggZZ, qqZZ, WZ], 'pdf')
print 'pdf_VV: ', pdf_VV

xs_ttZ = (2*0.2814)+0.5868+0.0822+0.8854
xs_ttW = 0.196+0.4049+0.6008+0.0162562
tot_ttV_xs = xs_ttZ + xs_ttW

ttZ = object(xs_ttZ, tot_ttV_xs, qcd_dn=0.113, qcd_up=0.096, pdf=0.028, alpha=0.028)
ttW = object(xs_ttW, tot_ttV_xs, qcd_dn=0.115, qcd_up=0.129, pdf=0.02, alpha=0.027)

qcd_ttV_up = err([ttZ, ttW], 'QCDup')
print 'QCD_ttV_Up: ', qcd_ttV_up
qcd_ttV_dn = err([ttZ, ttW], 'QCDdn')
print 'QCD_ttV_Dn: ', qcd_ttV_dn

pdf_ttV = err([ttZ, ttW], 'pdf')
print 'pdf_ttV: ', pdf_ttV

alphas_ttV = err([ttZ, ttW], 'alpha')
print 'alphas_ttV: ', alphas_ttV

xs_ST_tW = (2*35.85)+0.01096
xs_ST_t_channel = (2*80.95)+136.02
xs_ST_s_channel = 2*3.364
tot_ST_xs = xs_ST_tW+xs_ST_t_channel+xs_ST_s_channel

ST_tW = object(xs_ST_tW, tot_ST_xs, qcd_dn=0.018, qcd_up=0.018, pdf=0.034, alpha=-1)
ST_t_channel = object(xs_ST_t_channel, tot_ST_xs, qcd_dn=0.046, qcd_up=0.066, pdf=0.061, alpha=-1)
ST_s_channel = object(xs_ST_s_channel, tot_ST_xs, qcd_dn=0.024, qcd_up=0.029, pdf=0.027, alpha=-1)

qcd_ST_dn = err([ST_tW, ST_t_channel, ST_s_channel], 'QCDdn')
print 'QCD_ST_dn: ', qcd_ST_dn
qcd_ST_up = err([ST_tW, ST_t_channel, ST_s_channel], 'QCDup')
print 'QCD_ST_up: ', qcd_ST_up
pdf_ST = err([ST_tW, ST_t_channel, ST_s_channel], 'pdf')
print 'pdf_ST: ', pdf_ST

xs_DY_0jet = 4843.6
xs_DY_1jet = 897.8
xs_DY_2jet = 335.8
tot_DY_xs = xs_DY_0jet+xs_DY_1jet+xs_DY_2jet\

