#!/bin/bash

declare -A hadd_map
hadd_map["0l_2tau"]="Tight_OS/hadd/hadd_stage2_Tight_OS.root"
hadd_map["1l_1tau"]="Tight_disabled/hadd/hadd_stage2_Tight_disabled.root"
hadd_map["1l_2tau"]="Tight_OS/hadd/hadd_stage2_Tight_OS.root"
hadd_map["2l_2tau"]="Tight_sumOS/hadd/hadd_stage2_lepdisabled_taudisabled_Tight_sumOS.root"
hadd_map["2lss_1tau"]="Tight_SS_OS/hadd/hadd_stage2_Tight_lepSS_sumOS.root"
hadd_map["2los_1tau"]="Tight/hadd/hadd_stage2_Tight.root"
hadd_map["3l_1tau"]="Tight_OS/hadd/hadd_stage2_Tight_OS.root"

declare -A outputvar_map
outputvar_map["0l_2tau"]="mvaOutput_Legacy"
outputvar_map["1l_1tau"]="mvaOutput_Legacy_6"
outputvar_map["1l_2tau"]="mvaOutput_legacy"
outputvar_map["2l_2tau"]="mvaOutput_final"
outputvar_map["2lss_1tau"]="mvaOutput_final"
outputvar_map["2los_1tau"]="mvaOutput_legacy"
outputvar_map["3l_1tau"]="mvaOutput_legacy"

declare -A addsys_map
addsys_map["0l_2tau"]="addSystFakeRates_0l_2tau_0l_2tau_mvaOutput_Legacy_OS"
addsys_map["1l_1tau"]="addSystFakeRates_1l_1tau_1l_1tau_mvaOutput_Legacy_6_disabled"
addsys_map["1l_2tau"]="addSystFakeRates_1l_2tau_mvaOutput_legacy_OS"
addsys_map["2l_2tau"]="addSystFakeRates_2l_2tau_lepdisabled_taudisabled_sumOS_mvaOutput_final"
addsys_map["2lss_1tau"]="addSystFakeRates_2lss_1tau_sumOS_mvaOutput_final"
addsys_map["2los_1tau"]="addSystFakeRates_2los_1tau_mvaOutput_legacy"
addsys_map["3l_1tau"]="addSystFakeRates_3l_1tau_OS_mvaOutput_legacy"

declare -A title_map
title_map["0l_2tau"]="0l_2tau_OS_Tight"
title_map["1l_1tau"]="1l_1tau_Tight"
title_map["1l_2tau"]="1l_2tau_OS_Tight"
title_map["2l_2tau"]="2l_2tau_sumOS_Tight"
title_map["2lss_1tau"]="2lss_1tau_lepSS_sumOS_Tight"
title_map["2los_1tau"]="2los_1tau_Tight"
title_map["3l_1tau"]="3l_1tau_OS_lepTight_hadTauTight"

declare -A stxs_map
stxs_map["0l_2tau"]="stxs_0l_2tau_0l_2tau_mvaOutput_Legacy_OS"
stxs_map["1l_1tau"]="stxs_1l_1tau_1l_1tau_mvaOutput_Legacy_6_disabled"
stxs_map["1l_2tau"]="stxs_1l_2tau_mvaOutput_legacy_OS"
stxs_map["2l_2tau"]="stxs_2l_2tau_lepdisabled_taudisabled_sumOS_mvaOutput_final"
stxs_map["2lss_1tau_rest"]="stxs_2lss_1tau_sumOS_output_NN_rest"
stxs_map["2lss_1tau_ttH"]="stxs_2lss_1tau_sumOS_output_NN_ttH"
stxs_map["2lss_1tau_tH"]="stxs_2lss_1tau_sumOS_output_NN_tH"
stxs_map["2los_1tau"]="stxs_2los_1tau_mvaOutput_legacy"
stxs_map["3l_1tau"]="stxs_3l_1tau_OS_mvaOutput_legacy"

basetopdir=$PWD/cards
mkdir -p $basetopdir
tar -C $basetopdir -I lz4 -xvf /hdfs/local/karl/archives/HIG-19-008/ttHAnalysis_stxs_2020Jun18.tar.lz4

rm -f ./compare_histograms.py;
wget https://raw.githubusercontent.com/HEP-KBFI/tth-htt/dcard_production/scripts/compare_histograms.py

hig_dcards=$HOME/hig-19-008
if [ ! -d $hig_dcards ]; then
  echo "Please create $hig_dcards first"
  exit 1
fi

rescaled_cards=$HOME/stxs_rescaled
if [ ! -d $rescaled_cards ]; then
  echo "Please create $rescaled_cards first"
  exit 1
fi

for era in 2016 2017 2018; do

  topdir=$basetopdir/$era
  mkdir -p $topdir

  for channel in 0l_2tau 1l_1tau 1l_2tau 2l_2tau 2lss_1tau 2los_1tau 3l_1tau; do
    
    resultsdir=$topdir/2020Jun18/datacards/$channel/results
    mkdir -p $resultsdir

    logdir=$topdir/2020Jun18/logs/$channel
    mkdir -p $logdir
    
    subchannels=$channel
    if [ $channel = "2lss_1tau" ]; then
      subchannels="${channel}_rest ${channel}_tH ${channel}_ttH"
    fi
    echo "Subchannels are: $subchannels";
    
    for subchannel in $subchannels; do
    
      merge_htxs_output_base=stxs_${subchannel}_${outputvar_map[$channel]}
      merge_htxs_output=$topdir/2020Jun18/datacards/$channel/stxs/${merge_htxs_output_base}.root
      rescaled_htxs=$rescaled_cards/$era/hadd_stage1_rescaled_${subchannel}_stxsMerged.root
      input_orig=$topdir/2020Jun18/datacards/$channel/stxs/${stxs_map[$subchannel]}.root

      if [ ! -f $input_orig ]; then
        echo "No such file: $input_orig"
        exit 1
      fi
      if [ ! -f $rescaled_htxs ]; then
        echo "No such file: $rescaled_htxs"
        exit 1
      fi

      # make sure that there are no common histograms between the two files we're about to hadd
      nof_lines=$(./compare_histograms.py -i $input_orig -j $rescaled_htxs 2>&1 1>/dev/null | grep "Nothing to compare$" | wc -l)
      if [ "$nof_lines" -ne 1 ]; then
        echo "Found common histograms between $input_orig and $rescaled_htxs"
        exit 1
      fi
      hadd $merge_htxs_output $input_orig $rescaled_htxs;

      merge_htxs_output_mod=$resultsdir/${merge_htxs_output_base}_mod.root

      set -x
      /usr/bin/time --verbose WriteDatacards.py --era $era --shapeSyst --stxs \
        --inputShapes $merge_htxs_output --channel $subchannel \
        --cardFolder $resultsdir \
        --noX_prefix --forceModifyShapes &> $logdir/out_$subchannel.log
      set +x

      datacard=$hig_dcards/ttH_${subchannel}_${era}.root
      diff_txt=$topdir/diff_${era}_${subchannel}.txt
      
      ./compare_histograms.py -i $merge_htxs_output_mod -j $datacard -d ttH_${subchannel} -D ttH_${subchannel} &> $diff_txt
      echo "RESULT: $era $subchannel ( $diff_txt )  -> $(grep -v Comparing $diff_txt | wc -l)"
    
    done

  done
done
