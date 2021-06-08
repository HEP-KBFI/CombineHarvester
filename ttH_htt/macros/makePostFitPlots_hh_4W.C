
#include <TFile.h>
#include <TString.h>
#include <TCanvas.h>
#include <TH1.h>
#include <THStack.h>
#include <TAxis.h>
#include <TLegend.h>
#include <TLegendEntry.h>
#include <TPaveText.h>
#include <TMath.h>
#include <TROOT.h>
#include <TStyle.h>
#include <TList.h>
#include <TF1.h>
#include <TColor.h>

#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <iomanip>
#include <assert.h>


int rebinHistogram = 1;


TH1* loadHistogram(TFile* inputFile, const std::string& directory, const std::string& histogramName)
{
  std::string histogramName_full = Form("%s/%s", directory.data(), histogramName.data());
  TH1* histogram = dynamic_cast<TH1*>(inputFile->Get(histogramName_full.data()));
  if ( !histogram ) {
    std::cerr << "Failed to load histogram = " << histogramName_full << " from file = " << inputFile->GetName() << " !!" << std::endl;
    assert(0);
  }
  if ( !histogram->GetSumw2N() ) histogram->Sumw2();

  if (rebinHistogram > 1) histogram->Rebin(rebinHistogram);
  return histogram;
}

double compIntegral(TH1* histogram, bool includeUnderflowBin, bool includeOverflowBin)
{
  double sumBinContent = 0.;
  int numBins = histogram->GetNbinsX();
  int firstBin = ( includeUnderflowBin ) ? 0 : 1;
  int lastBin = ( includeOverflowBin  ) ? (numBins + 1) : numBins;
  for ( int iBin = firstBin; iBin <= lastBin; ++iBin ) {
    sumBinContent += histogram->GetBinContent(iBin);
  }
  return sumBinContent;
}

double square(double x)
{
  return x*x;
}

void makeBinContentsPositive(TH1* histogram, int verbosity = 0)
{
  if ( verbosity ) {
    std::cout << "<makeBinContentsPositive>:" << std::endl;
    std::cout << " integral(" << histogram->GetName() << ") = " << histogram->Integral() << std::endl;
  }
  double integral_original = compIntegral(histogram, true, true);
  if ( integral_original < 0. ) integral_original = 0.;
  if ( verbosity ) {
    std::cout << " integral_original = " << integral_original << std::endl;
  }
  int numBins = histogram->GetNbinsX();
  for ( int iBin = 0; iBin <= (numBins + 1); ++iBin ) {
    double binContent_original = histogram->GetBinContent(iBin);
    double binError2_original = square(histogram->GetBinError(iBin));
    if ( binContent_original < 0. ) {
      double binContent_modified = 0.;
      double binError2_modified = binError2_original + square(binContent_original - binContent_modified);
      assert(binError2_modified >= 0.);
      if ( verbosity ) {
        std::cout << "bin #" << iBin << " (x =  " << histogram->GetBinCenter(iBin) << "): binContent = " << binContent_original << " +/- " << TMath::Sqrt(binError2_original) 
                  << " --> setting it to binContent = " << binContent_modified << " +/- " << TMath::Sqrt(binError2_modified) << std::endl;
      }
      histogram->SetBinContent(iBin, binContent_modified);
      histogram->SetBinError(iBin, TMath::Sqrt(binError2_modified));
    }
  }
  double integral_modified = compIntegral(histogram, true, true);
  if ( integral_modified < 0. ) integral_modified = 0.;
  if ( verbosity ) {
    std::cout << " integral_modified = " << integral_modified << std::endl;
  }
  if ( integral_modified > 0. ) {
    double sf = integral_original/integral_modified;
    if ( verbosity ) {
      std::cout << "--> scaling histogram by factor = " << sf << std::endl;
    }
    histogram->Scale(sf);
  } else {
    for ( int iBin = 0; iBin <= (numBins + 1); ++iBin ) {
      histogram->SetBinContent(iBin, 0.);
    }
  }
  if ( verbosity ) {
    std::cout << " integral(" << histogram->GetName() << ") = " << histogram->Integral() << std::endl;
  }
}

void dumpHistogram(TH1* histogram)
{
  std::cout << "<dumpHistogram>:" << std::endl;
  std::cout << " histogram: name = " << histogram->GetName() << ", title = " << histogram->GetTitle() << std::endl;
  std::cout << "  fillColor = " << histogram->GetFillColor() << ", fillStyle = " << histogram->GetFillStyle() << ","
	    << " lineColor = " << histogram->GetLineColor() << ", lineStyle = " << histogram->GetLineStyle() << ", lineWidth = " << histogram->GetLineWidth() << "," 
	    << " markerColor = " << histogram->GetMarkerColor() << ", markerStyle = " << histogram->GetMarkerStyle() << ", markerSize = " << histogram->GetMarkerSize() << std::endl;
  TAxis* xAxis = histogram->GetXaxis();
  int numBins = xAxis->GetNbins();
  for ( int iBin = 1; iBin <= numBins; ++iBin ) {
    std::cout << "bin #" << iBin << " (x = " << xAxis->GetBinCenter(iBin) << "): " << histogram->GetBinContent(iBin) << " +/- " << histogram->GetBinError(iBin) << std::endl;
  }
  std::cout << "integral = " << compIntegral(histogram, true, true) << std::endl;
}

void checkCompatibleBinning(const TH1* histogram1, const TH1* histogram2)
{
  if ( histogram1 && histogram2 ) {
    if ( !(histogram1->GetNbinsX() == histogram2->GetNbinsX()) ) {
      std::cerr << "Histograms " << histogram1->GetName() << " and " << histogram2->GetName() << " have incompatible binning !!" << std::endl;
      std::cerr << " (NbinsX: histogram1 = " << histogram1->GetNbinsX() << ", histogram2 = " << histogram2->GetNbinsX() << ")" << std::endl;
      assert(0);
    }
    const TAxis* xAxis1 = histogram1->GetXaxis();
    const TAxis* xAxis2 = histogram2->GetXaxis();
    int numBins = xAxis1->GetNbins();
    for ( int iBin = 1; iBin <= numBins; ++iBin ) {
      double binWidth = 0.5*(xAxis1->GetBinWidth(iBin) + xAxis2->GetBinWidth(iBin));
      double dBinLowEdge = xAxis1->GetBinLowEdge(iBin) - xAxis2->GetBinLowEdge(iBin);
      double dBinUpEdge = xAxis1->GetBinUpEdge(iBin) - xAxis2->GetBinUpEdge(iBin);
      if ( !(dBinLowEdge < (1.e-3*binWidth) && dBinUpEdge < (1.e-3*binWidth)) ) {
	std::cerr << "Histograms " << histogram1->GetName() << " and " << histogram2->GetName() << " have incompatible binning !!" << std::endl;
	std::cerr << " (bin #" << iBin << ": histogram1 = " << xAxis1->GetBinLowEdge(iBin) << ".." << xAxis1->GetBinUpEdge(iBin) << ","
		  << " histogram2 = " << xAxis2->GetBinLowEdge(iBin) << ".." << xAxis2->GetBinUpEdge(iBin) << "" << std::endl;
	assert(0);
      }
    }
  }
}

TH1* divideHistogramByBinWidth(TH1* histogram)
{
  std::string histogramDensityName = Form("%s_density", histogram->GetName());
  TH1* histogramDensity = (TH1*)histogram->Clone(histogramDensityName.data());
  TAxis* xAxis = histogram->GetXaxis();
  int numBins = xAxis->GetNbins();
  for ( int iBin = 1; iBin <= numBins; ++iBin ) {
    double binContent = histogram->GetBinContent(iBin);
    if ( binContent < 0. ) binContent = 0.;
    double binError = histogram->GetBinError(iBin);
    double binWidth = xAxis->GetBinWidth(iBin);
    histogramDensity->SetBinContent(iBin, binContent/binWidth);
    histogramDensity->SetBinError(iBin, binError/binWidth);
  }
  return histogramDensity;
}

void addLabel_CMS_preliminary(double x0, double y0, double x0_luminosity)
{
  TPaveText* label_cms = new TPaveText(x0, y0 + 0.0025, x0 + 0.0950, y0 + 0.0600, "NDC");
  label_cms->AddText("CMS");
  label_cms->SetTextFont(61);
  label_cms->SetTextAlign(13);
  label_cms->SetTextSize(0.0575);
  label_cms->SetTextColor(1);
  label_cms->SetFillStyle(0);
  label_cms->SetBorderSize(0);
  label_cms->Draw();
  
  TPaveText* label_preliminary = new TPaveText(x0 + 0.1050, y0 - 0.0010, x0 + 0.2950, y0 + 0.0500, "NDC");
  label_preliminary->AddText("Preliminary");
  label_preliminary->SetTextFont(52);
  label_preliminary->SetTextAlign(13);
  label_preliminary->SetTextSize(0.050);
  label_preliminary->SetTextColor(1);
  label_preliminary->SetFillStyle(0);
  label_preliminary->SetBorderSize(0);
  label_preliminary->Draw();

  TPaveText* label_luminosity = new TPaveText(x0_luminosity, y0 + 0.0050, x0_luminosity + 0.1900, y0 + 0.0550, "NDC");
  label_luminosity->AddText("41.5 fb^{-1} (13 TeV)");
  label_luminosity->SetTextAlign(13);
  label_luminosity->SetTextSize(0.050);
  label_luminosity->SetTextColor(1);
  label_luminosity->SetFillStyle(0);
  label_luminosity->SetBorderSize(0);
  label_luminosity->Draw();
}

void setStyle_uncertainty(TH1* histogram)
{
  const int color_int = 12;
  const double alpha = 0.40;
  TColor* color = gROOT->GetColor(color_int);
  static int newColor_int = -1;
  static TColor* newColor = 0;
  if ( !newColor ) {
    newColor_int = gROOT->GetListOfColors()->GetSize() + 1;
    newColor = new TColor(newColor_int, color->GetRed(), color->GetGreen(), color->GetBlue(), "", alpha);
  }
  histogram->SetLineColor(newColor_int);
  histogram->SetLineWidth(0);
  histogram->SetFillColor(newColor_int);
  histogram->SetFillStyle(1001);
}

void makePlot(TH1* histogram_data, bool doKeepBlinded,
	      TH1* histogram_hh, 
	      TH1* histogram_Dibosons,
	      TH1* histogram_DY,
	      TH1* histogram_ttPlus,
	      TH1* histogram_SMH,
	      TH1* histogram_Other,
	      TH1* histogram_conversions,
	      TH1* histogram_fakes,
	      //	      TH1* histogram_flips,
	      TH1* histogramSum_mc,
	      TH1* histogramErr_mc,		
	      const std::string& xAxisTitle, 
	      const std::string& yAxisTitle, double yMin, double yMax,
	      bool showLegend,
	      const std::string& label,
	      const std::string& outputFileName,
	      bool useLogScale)
{
  TH1* histogram_data_density = 0;
  if ( histogram_data ) {
    histogram_data_density = divideHistogramByBinWidth(histogram_data);      
  }
  histogram_data_density->SetMarkerColor(1);
  histogram_data_density->SetMarkerStyle(20);
  histogram_data_density->SetMarkerSize(2);
  histogram_data_density->SetLineColor(1);
  histogram_data_density->SetLineWidth(1);
  histogram_data_density->SetLineStyle(1);

  TH1* histogram_hh_density = 0;
  if ( histogram_hh ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_hh, histogram_data);
    histogram_hh_density = divideHistogramByBinWidth(histogram_hh);
  }
  histogram_hh_density->SetFillColor(628);
  histogram_hh_density->SetLineColor(1);
  histogram_hh_density->SetLineWidth(1);

  TH1* histogram_Dibosons_density = 0;
  if ( histogram_Dibosons ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_Dibosons, histogram_data);
    histogram_Dibosons_density = divideHistogramByBinWidth(histogram_Dibosons);
  }
  histogram_Dibosons_density->SetFillColor(822);
  histogram_Dibosons_density->SetLineColor(1);
  histogram_Dibosons_density->SetLineWidth(1);

  TH1* histogram_DY_density = 0;
  if ( histogram_DY ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_DY, histogram_data);
    histogram_DY_density = divideHistogramByBinWidth(histogram_DY);
  }
  histogram_DY_density->SetFillColor(823);
  histogram_DY_density->SetLineColor(1);
  histogram_DY_density->SetLineWidth(1);

  TH1* histogram_ttPlus_density = 0;
  if ( histogram_ttPlus ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_ttPlus, histogram_data);
    histogram_ttPlus_density = divideHistogramByBinWidth(histogram_ttPlus);
  }
  histogram_ttPlus_density->SetFillColor(610);
  histogram_ttPlus_density->SetLineColor(1);
  histogram_ttPlus_density->SetLineWidth(1);

  TH1* histogram_SMH_density = 0;
  if ( histogram_SMH ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_SMH, histogram_data);
    histogram_SMH_density = divideHistogramByBinWidth(histogram_SMH);
  }
  histogram_SMH_density->SetFillColor(851);
  histogram_SMH_density->SetLineColor(1);
  histogram_SMH_density->SetLineWidth(1);

  TH1* histogram_Other_density = 0;
  if ( histogram_Other ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_Other, histogram_data);
    histogram_Other_density = divideHistogramByBinWidth(histogram_Other);
  }
  histogram_Other_density->SetFillColor(715);
  histogram_Other_density->SetLineColor(1);
  histogram_Other_density->SetLineWidth(1);

  TH1* histogram_conversions_density = 0;
  if ( histogram_conversions ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_conversions, histogram_data);
    histogram_conversions_density = divideHistogramByBinWidth(histogram_conversions);
  }
  histogram_conversions_density->SetFillColor(1);
  histogram_conversions_density->SetFillStyle(3006);
  histogram_conversions_density->SetLineColor(1);
  histogram_conversions_density->SetLineWidth(1);
  

  TH1* histogram_fakes_density = 0;
  if ( histogram_fakes ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_fakes, histogram_data);
    histogram_fakes_density = divideHistogramByBinWidth(histogram_fakes);
  }
  histogram_fakes_density->SetFillColor(1);
  histogram_fakes_density->SetFillStyle(3005);
  histogram_fakes_density->SetLineColor(1);
  histogram_fakes_density->SetLineWidth(1);
  /*
  TH1* histogram_flips_density = 0;
  if ( histogram_flips ) {
    if ( histogram_data ) checkCompatibleBinning(histogram_flips, histogram_data);
    histogram_flips_density = divideHistogramByBinWidth(histogram_flips);
  }
  histogram_flips_density->SetFillColor(1);
  histogram_flips_density->SetFillStyle(3006);
  histogram_flips_density->SetLineColor(1);
  histogram_flips_density->SetLineWidth(1);
  */
  TH1* histogramSum_mc_density = 0;
  if ( histogramSum_mc ) {
    if ( histogram_data ) checkCompatibleBinning(histogramSum_mc, histogram_data);
    histogramSum_mc_density = divideHistogramByBinWidth(histogramSum_mc);
  }
  std::cout << "histogramSum_mc_density = " << histogramSum_mc_density << std::endl;
  dumpHistogram(histogramSum_mc_density);

  TH1* histogramErr_mc_density = 0;
  if ( histogramErr_mc ) {
    if ( histogram_data ) checkCompatibleBinning(histogramErr_mc, histogram_data);
    histogramErr_mc_density = divideHistogramByBinWidth(histogramErr_mc);
  }
  setStyle_uncertainty(histogramErr_mc_density);

  TCanvas* canvas = new TCanvas("canvas", "canvas", 950, 1100);
  canvas->SetFillColor(10);
  canvas->SetBorderSize(2);
  canvas->Draw();

  TPad* topPad = new TPad("topPad", "topPad", 0.00, 0.34, 1.00, 0.995);
  topPad->SetFillColor(10);
  topPad->SetTopMargin(0.065);
  topPad->SetLeftMargin(0.20);
  topPad->SetBottomMargin(0.00);
  topPad->SetRightMargin(0.04);
  topPad->SetLogy(useLogScale);
  
  TPad* bottomPad = new TPad("bottomPad", "bottomPad", 0.00, 0.01, 1.00, 0.335);
  bottomPad->SetFillColor(10);
  bottomPad->SetTopMargin(0.085);
  bottomPad->SetLeftMargin(0.20);
  bottomPad->SetBottomMargin(0.35);
  bottomPad->SetRightMargin(0.04);
  bottomPad->SetLogy(false);

  canvas->cd();
  topPad->Draw();
  topPad->cd();

  THStack* histogramStack_mc = new THStack();
  //  histogramStack_mc->Add(histogram_flips_density);
  histogramStack_mc->Add(histogram_Other_density);
  histogramStack_mc->Add(histogram_hh_density);
  histogramStack_mc->Add(histogram_conversions_density);
  histogramStack_mc->Add(histogram_SMH_density);
  histogramStack_mc->Add(histogram_fakes_density);
  histogramStack_mc->Add(histogram_ttPlus_density);
  histogramStack_mc->Add(histogram_DY_density);
  histogramStack_mc->Add(histogram_Dibosons_density);  

  TH1* histogram_ref = histogram_data_density;
  histogram_ref->SetTitle("");
  histogram_ref->SetStats(false);
  histogram_ref->SetMaximum(yMax);
  histogram_ref->SetMinimum(yMin);

  TAxis* xAxis_top = histogram_ref->GetXaxis();
  assert(xAxis_top);
  if ( xAxisTitle != "" ) xAxis_top->SetTitle(xAxisTitle.data());
  xAxis_top->SetTitleOffset(1.20);
  xAxis_top->SetLabelColor(10);
  xAxis_top->SetTitleColor(10);

  TAxis* yAxis_top = histogram_ref->GetYaxis();
  assert(yAxis_top);
  if ( yAxisTitle != "" ) yAxis_top->SetTitle(yAxisTitle.data());
  yAxis_top->SetTitleOffset(1.20);
  yAxis_top->SetTitleSize(0.080);
  yAxis_top->SetLabelSize(0.065);
  yAxis_top->SetTickLength(0.04);  

  histogram_ref->Draw("axis");

  // CV: calling THStack::Draw() causes segmentation violation ?!
  //histogramStack_mc->Draw("histsame");

  // CV: draw histograms without using THStack instead;
  //     note that order in which histograms need to be drawn needs to be reversed 
  //     compared to order in which histograms were added to THStack !!
  histogram_Dibosons_density->Add(histogram_DY_density);
  histogram_Dibosons_density->Add(histogram_ttPlus_density);
  histogram_Dibosons_density->Add(histogram_fakes_density);
  histogram_Dibosons_density->Add(histogram_SMH_density);
  histogram_Dibosons_density->Add(histogram_conversions_density);
  histogram_Dibosons_density->Add(histogram_hh_density);
  histogram_Dibosons_density->Add(histogram_Other_density);
  //  histogram_Dibosons_density->Add(histogram_flips_density);
  histogram_Dibosons_density->Draw("histsame");

  histogram_DY_density->Add(histogram_ttPlus_density);
  histogram_DY_density->Add(histogram_fakes_density);
  histogram_DY_density->Add(histogram_SMH_density);
  histogram_DY_density->Add(histogram_conversions_density);
  histogram_DY_density->Add(histogram_hh_density);
  histogram_DY_density->Add(histogram_Other_density);
  //  histogram_DY_density->Add(histogram_flips_density);
  histogram_DY_density->Draw("histsame");

  histogram_ttPlus_density->Add(histogram_fakes_density);
  histogram_ttPlus_density->Add(histogram_SMH_density);
  histogram_ttPlus_density->Add(histogram_conversions_density);
  histogram_ttPlus_density->Add(histogram_hh_density);
  histogram_ttPlus_density->Add(histogram_Other_density);
  //  histogram_ttPlus_density->Add(histogram_flips_density);
  histogram_ttPlus_density->Draw("histsame");
  
  histogram_fakes_density->Add(histogram_SMH_density);
  histogram_fakes_density->Add(histogram_conversions_density);
  histogram_fakes_density->Add(histogram_hh_density);
  histogram_fakes_density->Add(histogram_Other_density);
  //  histogram_fakes_density->Add(histogram_flips_density);
  histogram_fakes_density->Draw("histsame");

  histogram_SMH_density->Add(histogram_conversions_density);
  histogram_SMH_density->Add(histogram_hh_density);
  histogram_SMH_density->Add(histogram_Other_density);
  //  histogram_SMH_density->Add(histogram_flips_density);
  histogram_SMH_density->Draw("histsame");

  histogram_conversions_density->Add(histogram_hh_density);
  histogram_conversions_density->Add(histogram_Other_density);
  //  histogram_conversions_density->Add(histogram_flips_density);
  histogram_conversions_density->Draw("histsame");

  histogram_hh_density->Add(histogram_Other_density);
  //  histogram_hh_density->Add(histogram_flips_density);
  histogram_hh_density->Draw("histsame");   
  
  //  histogram_Other_density->Add(histogram_flips_density);
  TH1* histogram_Other_density_cloned = (TH1*)histogram_Other_density->Clone();
  histogram_Other_density_cloned->SetFillColor(10);
  histogram_Other_density_cloned->SetFillStyle(1001);
  histogram_Other_density_cloned->Draw("histsame");
  histogram_Other_density->Draw("histsame");

  //  histogram_flips_density->Draw("histsame");

  if ( histogramErr_mc_density ) {    
    histogramErr_mc_density->Draw("e2same");
  }
  
  if ( !doKeepBlinded ) {
    histogram_data_density->Draw("e1psame");
  }

  histogram_ref->Draw("axissame");

  double legend_y0 = 0.6950;
  //  if ( histogram_flips && histogramErr_mc ) legend_y0 -= 0.0500;
  if ( histogramErr_mc ) legend_y0 -= 0.0500;
  if ( showLegend ) {
    TLegend* legend1 = new TLegend(0.2600, legend_y0, 0.5350, 0.9250, NULL, "brNDC");
    legend1->SetFillStyle(0);
    legend1->SetBorderSize(0);
    legend1->SetFillColor(10);
    legend1->SetTextSize(0.050);    
    TH1* histogram_data_forLegend = (TH1*)histogram_data_density->Clone();
    histogram_data_forLegend->SetMarkerSize(2);
    legend1->AddEntry(histogram_data_forLegend, "Observed", "p");
    legend1->AddEntry(histogram_hh_density, "HH#rightarrow 4W, 2W2#tau, 4#tau", "f");
    legend1->AddEntry(histogram_Dibosons_density, "DIbosons", "f");
    legend1->AddEntry(histogram_DY_density, "DY", "f");
    legend1->AddEntry(histogram_ttPlus_density, "t#bar{t} + t#bar{t}V(V)", "f");
    legend1->Draw();
    TLegend* legend2 = new TLegend(0.6600, legend_y0, 0.9350, 0.9250, NULL, "brNDC");
    legend2->SetFillStyle(0);
    legend2->SetBorderSize(0);
    legend2->SetFillColor(10);
    legend2->SetTextSize(0.050); 
    legend2->AddEntry(histogram_SMH_density, "SMH", "f");
    legend2->AddEntry(histogram_Other_density, "Other", "f");
    legend2->AddEntry(histogram_conversions_density, "Conversions", "f");
    legend2->AddEntry(histogram_fakes_density, "Fakes", "f");    
    //    legend2->AddEntry(histogram_flips_density, "Flips", "f");
    if ( histogramErr_mc ) legend2->AddEntry(histogramErr_mc_density, "Uncertainty", "f");
    legend2->Draw();
  }

  //addLabel_CMS_luminosity(0.2100, 0.9700, 0.6350);
  addLabel_CMS_preliminary(0.2100, 0.9700, 0.6350);

  TPaveText* label_category = 0;
  if ( showLegend ) label_category = new TPaveText(0.6600, legend_y0 - 0.0550, 0.9350, legend_y0, "NDC");
  else label_category = new TPaveText(0.2350, 0.8500, 0.5150, 0.9100, "NDC");
  label_category->SetTextAlign(13);
  label_category->AddText(label.data());
  label_category->SetTextSize(0.055);
  label_category->SetTextColor(1);
  label_category->SetFillStyle(0);
  label_category->SetBorderSize(0);
  label_category->Draw();

  canvas->cd();
  bottomPad->Draw();
  bottomPad->cd();
 
  TH1* histogramRatio = (TH1*)histogram_data_density->Clone("histogramRatio");
  if ( !histogramRatio->GetSumw2N() ) histogramRatio->Sumw2();
  histogramRatio->SetTitle("");
  histogramRatio->SetStats(false);
  histogramRatio->SetMinimum(-0.99);
  histogramRatio->SetMaximum(+0.99);
  histogramRatio->SetMarkerColor(histogram_data_density->GetMarkerColor());
  histogramRatio->SetMarkerStyle(histogram_data_density->GetMarkerStyle());
  histogramRatio->SetMarkerSize(histogram_data_density->GetMarkerSize());
  histogramRatio->SetLineColor(histogram_data_density->GetLineColor());

  TH1* histogramRatioUncertainty = (TH1*)histogram_data_density->Clone("histogramRatioUncertainty");
  if ( !histogramRatioUncertainty->GetSumw2N() ) histogramRatioUncertainty->Sumw2();
  histogramRatioUncertainty->SetMarkerColor(10);
  histogramRatioUncertainty->SetMarkerSize(0);
  setStyle_uncertainty(histogramRatioUncertainty);

  int numBins_bottom = histogramRatio->GetNbinsX();
  for ( int iBin = 1; iBin <= numBins_bottom; ++iBin ) {
    double binContent_data = histogram_data_density->GetBinContent(iBin);
    double binError_data = histogram_data_density->GetBinError(iBin);
    double binContent_mc = 0;
    double binError_mc = 0;
    if ( histogramSum_mc && histogramErr_mc ) {
      binContent_mc = histogramSum_mc_density->GetBinContent(iBin);
      binError_mc = histogramErr_mc_density->GetBinError(iBin);
    } else {
      TList* histograms = histogramStack_mc->GetHists();
      TIter nextHistogram(histograms);
      double binError2_mc = 0.;
      while ( TH1* histogram_density = dynamic_cast<TH1*>(nextHistogram()) ) {
        binContent_mc += histogram_density->GetBinContent(iBin);
        binError2_mc += square(histogram_density->GetBinError(iBin));
      }
      binError_mc = TMath::Sqrt(binError2_mc);
    }
    if ( binContent_mc > 0. ) {
      histogramRatio->SetBinContent(iBin, binContent_data/binContent_mc - 1.0);
      histogramRatio->SetBinError(iBin, binError_data/binContent_mc);

      histogramRatioUncertainty->SetBinContent(iBin, 0.);
      histogramRatioUncertainty->SetBinError(iBin, binError_mc/binContent_mc);
    }
  }
  std::cout << "histogramRatio = " << histogramRatio << std::endl;
  dumpHistogram(histogramRatio);
  std::cout << "histogramRatioUncertainty = " << histogramRatioUncertainty << std::endl;
  dumpHistogram(histogramRatioUncertainty);

  TAxis* xAxis_bottom = histogramRatio->GetXaxis();
  assert(xAxis_bottom);
  xAxis_bottom->SetTitle(xAxis_top->GetTitle());
  xAxis_bottom->SetLabelColor(1);
  xAxis_bottom->SetTitleColor(1);
  xAxis_bottom->SetTitleOffset(1.05);
  xAxis_bottom->SetTitleSize(0.16);
  xAxis_bottom->SetTitleFont(xAxis_top->GetTitleFont());
  xAxis_bottom->SetLabelOffset(0.02);
  xAxis_bottom->SetLabelSize(0.12);
  xAxis_bottom->SetTickLength(0.065);
  xAxis_bottom->SetNdivisions(505);

  TAxis* yAxis_bottom = histogramRatio->GetYaxis();
  assert(yAxis_bottom);
  yAxis_bottom->SetTitle("#frac{Data - Expectation}{Expectation}");
  yAxis_bottom->SetLabelColor(1);
  yAxis_bottom->SetTitleColor(1);
  yAxis_bottom->SetTitleOffset(0.95);
  yAxis_bottom->SetTitleFont(yAxis_top->GetTitleFont());
  yAxis_bottom->SetNdivisions(505);
  yAxis_bottom->CenterTitle();
  yAxis_bottom->SetTitleSize(0.095);
  yAxis_bottom->SetLabelSize(0.110);
  yAxis_bottom->SetTickLength(0.04);  

  histogramRatio->Draw("axis");

  TF1* line = new TF1("line","0", xAxis_bottom->GetXmin(), xAxis_bottom->GetXmax());
  line->SetLineStyle(3);
  line->SetLineWidth(1.5);
  line->SetLineColor(kBlack);
  line->Draw("same");

  histogramRatioUncertainty->Draw("e2same"); 

  if ( !doKeepBlinded ) {
    histogramRatio->Draw("epsame");
  }

  histogramRatio->Draw("axissame");

  canvas->Update();

  size_t idx = outputFileName.find_last_of('.');
  std::string outputFileName_plot = std::string(outputFileName, 0, idx);
  if ( useLogScale ) outputFileName_plot.append("_log");
  else outputFileName_plot.append("_linear");
  canvas->Print(std::string(outputFileName_plot).append(".pdf").data());
  canvas->Print(std::string(outputFileName_plot).append(".root").data());

  //delete label_cms;
  delete topPad;
  delete label_category;
  delete histogramRatio;
  delete histogramRatioUncertainty;
  delete line;
  delete bottomPad;    
  delete canvas;
}

void makePostFitPlots_hh_4W(
	std::string name ,
	std::string dir,
	std::string channel,
	std::string source,
	bool useLogPlot,
	bool hasFlips,
	bool hasConversions,
	std::string labelX,
	std::string labelVar,
	float minYPlot,
	float maxYPlot,
	bool gentau,
	std::string typeFit,
	bool divideByBinWidth,
	bool doKeepBlinded = true,
	int         mHH = 400
)
{
  gROOT->SetBatch(true);
  std::cout << "options passed = " << useLogPlot << " "
	    << hasFlips << " "
	    << labelX << " "
	    << minYPlot << " "
	    << maxYPlot << " "
	    << std::endl;

  printf("makePostFitPlots_hh_4W:: options:: \n name: %s, \n dir: %s, \n channel: %s, \n source: %s, \n useLogPlot: %d, \n hasFlips: %d, \n hasConversions: %d\n",
	 name.data(),dir.data(),channel.data(),source.data(),
	 useLogPlot,hasFlips,hasConversions);
  printf(" labelX: %s, \n labelVar: %s, \n minYPlot: %f, \n maxYPlot: %f, \n gentau: %d, \n typeFit: %s, \n divideByBinWidth: %d, \n doKeepBlinded: %d, \n mHH: %i \n",
	 
	 labelX.data(),labelVar.data(),  minYPlot,maxYPlot, gentau, typeFit.data(),
	 divideByBinWidth,doKeepBlinded, mHH);


  
  TH1::AddDirectory(false);

  std::vector<std::string> categories;
  std::string channelC="";
  channelC.append(channel.data());
  if (typeFit == "prefit") channelC.append("_prefit");
  if (typeFit == "postfit") channelC.append("_postfit");
  categories.push_back(channelC);

  std::string inputFilePath = source.data();
  std::map<std::string, std::string> inputFileNames; // key = category
  std::string fileI=dir.data();
  fileI.append("/");
  fileI.append(name);
  fileI.append("_shapes.root");
  inputFileNames[channelC]  = fileI;

  int hhMass = mHH;
  
  //  bool doKeepBlinded = true;
  //bool doKeepBlinded = false;

  for ( std::vector<std::string>::const_iterator category = categories.begin();
	category != categories.end(); ++category ) {
    std::string inputFileName_full = Form("%s%s", inputFilePath.data(), inputFileNames[*category].data());
    TFile* inputFile = new TFile(inputFileName_full.data());
    if ( !inputFile ) {
      std::cerr << "Failed to open input file = " << inputFileName_full << " !!" << std::endl;
      assert(0);
    }

    TH1* histogram_data = loadHistogram(inputFile, *category, "data_obs");
    std::cout << "histogram_data = " << histogram_data << ":" << std::endl;
    if ( !doKeepBlinded ) {
      dumpHistogram(histogram_data);
    }

    TH1* histogram_hh_tttt = loadHistogram(inputFile, *category, Form("signal_ggf_spin0_%i_hh_tttt",hhMass));
    TH1* histogram_hh_wwtt = loadHistogram(inputFile, *category, Form("signal_ggf_spin0_%i_hh_wwtt",hhMass));
    TH1* histogram_hh_wwww = loadHistogram(inputFile, *category, Form("signal_ggf_spin0_%i_hh_wwww",hhMass));
    std::cout << "histogram_hh: -> tttt = " << histogram_hh_tttt << ", wwtt = " << histogram_hh_wwtt << ", wwww = " << histogram_hh_wwww << std::endl;
    TString histogramName_hh = TString(histogram_hh_tttt->GetName()).ReplaceAll("_tttt", "_sum");
    TH1* histogram_hh = (TH1*)histogram_hh_tttt->Clone(histogramName_hh.Data());
    histogram_hh->Add(histogram_hh_wwtt);
    histogram_hh->Add(histogram_hh_wwww);
    makeBinContentsPositive(histogram_hh);
    std::cout << "histogram_hh = " << histogram_hh << ":" << std::endl;
    dumpHistogram(histogram_hh);


    TH1* histogram_WW = loadHistogram(inputFile, *category, "WW");
    TH1* histogram_WZ = loadHistogram(inputFile, *category, "WZ");
    TH1* histogram_ZZ = loadHistogram(inputFile, *category, "ZZ");
    std::cout << "histograms dibosons: WW = " << histogram_WW << ", WZ = " << histogram_WZ << ", ZZ =" << histogram_ZZ << std::endl;
    TString histogramName_Dibosons = TString(histogram_WW->GetName()).ReplaceAll("_WW", "_Dibosons");
    TH1* histogram_Dibosons = (TH1*)histogram_WW->Clone(histogramName_Dibosons.Data());
    histogram_Dibosons->Add(histogram_WZ);
    histogram_Dibosons->Add(histogram_ZZ);
    makeBinContentsPositive(histogram_Dibosons);
    std::cout << "histogram_Dibosons = " << histogram_Dibosons << ":" << std::endl;
    dumpHistogram(histogram_Dibosons);


    TH1* histogram_DY = loadHistogram(inputFile, *category, "DY");
    std::cout << "histogram_DY = " << histogram_DY << std::endl;
    makeBinContentsPositive(histogram_DY);
    dumpHistogram(histogram_DY);

    
    TH1* histogram_tt   = loadHistogram(inputFile, *category, "TT");
    TH1* histogram_ttW  = loadHistogram(inputFile, *category, "TTW");
    TH1* histogram_ttZ  = loadHistogram(inputFile, *category, "TTZ");
    TH1* histogram_ttWW = loadHistogram(inputFile, *category, "TTWW");
    std::cout << "histogram: tt = " << histogram_tt << ", ttW = " << histogram_ttW << " ttZ = " << histogram_ttZ << ", ttWW = " << histogram_ttWW << std::endl;
    TString histogramName_ttPlus = TString(histogram_tt->GetName()).ReplaceAll("_tt", "_ttPlus");
    TH1* histogram_ttPlus = (TH1*)histogram_tt->Clone(histogramName_ttPlus.Data());
    histogram_ttPlus->Add(histogram_ttW);
    histogram_ttPlus->Add(histogram_ttZ);
    histogram_ttPlus->Add(histogram_ttWW);
    makeBinContentsPositive(histogram_ttPlus);
    std::cout << "histogram_ttPlus = " << histogram_ttPlus << ":" << std::endl;
    dumpHistogram(histogram_ttPlus);    

    
    TH1* histogram_VH   = loadHistogram(inputFile, *category, "VH");
    TH1* histogram_TH   = loadHistogram(inputFile, *category, "TH");
    TH1* histogram_TTH  = loadHistogram(inputFile, *category, "TTH");
    std::cout << "histogram: VH = " << histogram_VH << ", TH = " << histogram_TH << ", TTH = " << histogram_TTH << std::endl;
    TString histogramName_SMH = TString(histogram_VH->GetName()).ReplaceAll("_VH", "_SMH");
    TH1* histogram_SMH = (TH1*)histogram_VH->Clone(histogramName_SMH.Data());
    histogram_SMH->Add(histogram_TH);
    histogram_SMH->Add(histogram_TTH);
    makeBinContentsPositive(histogram_SMH);
    std::cout << "histogram_SMH = " << histogram_SMH << ":" << std::endl;
    dumpHistogram(histogram_SMH);
    
    TH1* histogram_W   = loadHistogram(inputFile, *category, "W");
    TH1* histogram_other   = loadHistogram(inputFile, *category, "Other");
    std::cout << "histograms: W = " << histogram_W << ", other = " << histogram_other << std::endl;
    TString histogramName_Other = TString(histogram_W->GetName()).ReplaceAll("_W", "_Other");
    TH1* histogram_Other = (TH1*)histogram_W->Clone(histogramName_Other.Data());
    histogram_Other->Add(histogram_other);
    makeBinContentsPositive(histogram_Other);
    std::cout << "histogram_Other = " << histogram_Other << ":" << std::endl;
    dumpHistogram(histogram_Other);


    TH1* histogram_conversions = loadHistogram(inputFile, *category, "conversions");
    std::cout << "histogram_conversions = " << histogram_conversions << std::endl;
    makeBinContentsPositive(histogram_conversions);
    dumpHistogram(histogram_conversions);

    TH1* histogram_fakes = loadHistogram(inputFile, *category, "fakes_data");
    std::cout << "histogram_fakes = " << histogram_fakes << std::endl;
    makeBinContentsPositive(histogram_fakes);
    dumpHistogram(histogram_fakes);
    /*
    TH1* histogram_flips = loadHistogram(inputFile, *category, "flips_data");
    std::cout << "histogram_flips = " << histogram_flips << std::endl;
    makeBinContentsPositive(histogram_flips);
    dumpHistogram(histogram_flips);
    */
    TH1* histogramSum_mcBgr = loadHistogram(inputFile, *category, "TotalBkg");
    std::cout << "histogramSum_mcBgr = " << histogramSum_mcBgr << std::endl;
    makeBinContentsPositive(histogramSum_mcBgr);
    dumpHistogram(histogramSum_mcBgr);
    TH1* histogramSum_mc = (TH1*)histogramSum_mcBgr->Clone("histogramSum_mc");
    histogramSum_mc->Add(histogram_hh);
    std::cout << "histogramSum_mc = " << histogramSum_mc << std::endl;
    TH1* histogramErr_mc = (TH1*)histogramSum_mc->Clone("TotalBkgErr");

    //std::string outputFilePath = string(getenv("CMSSW_BASE")) + "/src/CombineHarvester/ttH_htt/plots";
    //std::string outputFilePath = "/home/ssawant/ana/hhwwww/hh_3l/20181021/CalLimit_v20181127/vMvaSUMBk_HH_woShapeSys_woAsimov/PostfitPlots/Plots";
    //std::string outputFilePath = ".";
    //std::string outputFileName = Form("%s/makePostFitPlots_%s_mvaOutput_xga_SUMBk_HH_%i_v20190213_test.pdf", outputFilePath.data(), category->data(), hhMass);

    std::string outputFilePath = source;
    std::string fileO=dir.data();
    fileO.append("/");
    fileO.append(name);
    fileO.append(Form("_makePostFitPlots_%s.root",typeFit.data()));
    std::string outputFileName = Form("%s%s",outputFilePath.data(),fileO.data());
    
    
    makePlot(histogram_data, doKeepBlinded,
	     histogram_hh, 
	     histogram_Dibosons,
	     histogram_DY,
	     histogram_ttPlus,
	     histogram_SMH,
	     histogram_Other,
	     histogram_conversions,
	     histogram_fakes,
	     //	     histogram_flips,
	     histogramSum_mc,
	     histogramErr_mc,		
	     "BDT", 
	     //"Events", 1.01e-2, 3.99e+2, 
	     "Events", 1., 1e5,
	     true,
	     "hh_3l",
	     outputFileName,
	     true);

    delete histogram_hh;
    delete histogramErr_mc;
    delete inputFile;
  }
}

