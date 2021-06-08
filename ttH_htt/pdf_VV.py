import math
def err(weight, error, up=True):
    err = 0
    for w, e in zip(weight, error):
        err += (w*w*e*e)
    err = math.sqrt(err)
    if up:
        return '%.3f' %(1+err)
    else:
        return '%.3f' %(1/(1+err))

xs_WZ = 4.9173+2.8309+0.716+0.5442+0.3807+0.1842+0.07452+0.0799+0.1068+5.6+10.71
xs_WW = 12.2+50.45+52.15
xs_ggZZ = 0.002703+0.005406
xs_qqZZ = 1.3816+0.6204+6.072
tot_xs = xs_ggZZ + xs_qqZZ + xs_WZ + xs_WW
w_ggZZ = xs_ggZZ/tot_xs
w_qqZZ = xs_qqZZ/tot_xs
w_WZ = xs_WZ/tot_xs
w_WW = xs_WW/tot_xs

qcd_ggZZ_up=0.236
qcd_qqZZ_up=0.0208
qcd_WZ_up = 0.038
qcd_ggZZ_dn=0.176
qcd_qqZZ_dn=0.0133
qcd_WZ_dn = 0.033

pdf_ggZZ = 0.173
pdf_qqZZ = 0.0314
pdf_WZ   = 0.014

qcd_VV_up = err([w_ggZZ, w_qqZZ, w_WZ], [qcd_ggZZ_up, qcd_qqZZ_up, qcd_WZ_up], True)
print 'QCD_VV_Up: ', qcd_VV_up
qcd_VV_dn = err([w_ggZZ, w_qqZZ, w_WZ], [qcd_ggZZ_dn, qcd_qqZZ_dn, qcd_WZ_dn], False)
print 'QCD_VV_Dn: ', qcd_VV_dn
pdf_VV = err([w_ggZZ, w_qqZZ, w_WZ], [pdf_ggZZ, pdf_qqZZ, pdf_WZ])
print 'pdf_VV: ', pdf_VV

xs_ttZ = 0.2814+0.5868+0.0822+0.8854
xs_ttW = 0.196+0.4049+0.6008+0.0162562
tot_ttV_xs = xs_ttZ + xs_ttW
w_ttZ = xs_ttZ/tot_ttV_xs
w_ttW = xs_ttW/tot_ttV_xs

qcd_ttZ_up = 0.096
qcd_ttW_up = 0.129
qcd_ttZ_dn = 0.113
qcd_ttW_dn = 0.115

pdf_ttZ = 0.028
pdf_ttW = 0.02

alphas_ttZ = 0.028
alphas_ttW = 0.027

qcd_ttV_up = err([w_ttZ, w_ttW], [qcd_ttZ_up, qcd_ttW_up], True)
print 'QCD_ttV_Up: ', qcd_ttV_up
qcd_ttV_dn = err([w_ttZ, w_ttW], [qcd_ttZ_dn, qcd_ttW_dn], False)
print 'QCD_ttV_Dn: ', qcd_ttV_dn

pdf_ttV = err([w_ttZ, w_ttW], [pdf_ttZ, pdf_ttW])
print 'pdf_ttV: ', pdf_ttV

alphas_ttV = err([w_ttZ, w_ttW], [alphas_ttZ, alphas_ttW])
print 'alphas_ttV: ', alphas_ttV

xs_ST_tW = (2*35.85)+0.01096
xs_ST_t_channel = (2*80.95)+136.02
xs_ST_s_channel = 2*3.364
tot_ST_xs = xs_ST_tW+xs_ST_t_channel+xs_ST_s_channel
w_ST_tW = xs_ST_tW/tot_ST_xs
w_ST_t_channel = xs_ST_t_channel/tot_ST_xs
w_ST_s_channel = xs_ST_s_channel/tot_ST_xs

qcd_ST_tW_up = 0.018
qcd_ST_t_channel_up = 0.066
qcd_ST_s_channel_up = 0.029

qcd_ST_tW_dn = 0.018
qcd_ST_t_channel_dn = 0.046
qcd_ST_s_channel_dn = 0.024

pdf_ST_tW = 0.034
pdf_ST_t_channel = 0.061
pdf_ST_s_channel = 0.027

qcd_ST_up = err([w_ST_tW, w_ST_t_channel, w_ST_s_channel], [qcd_ST_tW_up, qcd_ST_t_channel_up, qcd_ST_s_channel_up], True)
print 'QCD_ST_up: ', qcd_ST_up
qcd_ST_dn = err([w_ST_tW, w_ST_t_channel, w_ST_s_channel], [qcd_ST_tW_dn, qcd_ST_t_channel_dn, qcd_ST_s_channel_dn], False)
print 'QCD_ST_dn: ', qcd_ST_dn
pdf_ST = err([w_ST_tW, w_ST_t_channel, w_ST_s_channel], [pdf_ST_tW, pdf_ST_t_channel, pdf_ST_s_channel])
print 'pdf_ST: ', pdf_ST


